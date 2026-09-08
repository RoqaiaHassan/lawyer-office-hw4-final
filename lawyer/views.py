from unittest import case
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.http import request
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from .forms import (
    CaseAssignmentForm, CaseRequestForm, ContactMessageForm, LawyerForm,
    OfficeCardForm, QuickConsultationForm, ReplyForm
)
from .models import CaseRequest, ContactMessage, Lawyer, OfficeCard, Service, Specialization


def is_admin_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# الدوال الأساسية للموقع
def home(request):
    if not request.user.is_authenticated:
        return redirect("account:register")

    context = {
        "office_name": "Vision Law Office",
        "lab_number": 3,
        "is_open": True,
        "lawyers": Lawyer.objects.select_related('office_card').prefetch_related('specializations').all(),
        "services": Service.objects.all(),
    }
    return render(request, "lawyer/home.html", context)


def about(request):
    context = {
        "description": "مكتب متخصص في تقديم الاستشارات والقضايا القانونية"
    }
    return render(request, "lawyer/about.html", context)


def services(request):
    context = {"services": Service.objects.all()}
    return render(request, "lawyer/services.html", context)


def contact(request):
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            if request.user.is_authenticated:
                msg.user = request.user
            msg.save()
            messages.success(request, 'تم إرسال رسالتك بنجاح وسنرد عليك في أقرب وقت')
            return redirect('lawyer:contact')
    else:
        form = ContactMessageForm()
    return render(request, "lawyer/contact.html", {"form": form})


def detail(request, lawyer_id):
    lawyer = get_object_or_404(Lawyer.objects.select_related('office_card', 'user').prefetch_related('specializations'), pk=lawyer_id)
    context = {"lawyer": lawyer}
    return render(request, "lawyer/detail.html", context)


# دوال إدارة المحامين (عرض، إضافة، تعديل، حذف)
SEARCH_TRANSLATIONS = {
    "قانون الأعمال": "قانون تجاري",
    "قانون الأعمال التجارية": "قانون تجاري",
    "القانون التجاري": "قانون تجاري",
}


def lawyer_list(request):
    query = request.GET.get("q", "").strip()
    translated_query = query
    for source, target in SEARCH_TRANSLATIONS.items():
        if source in query:
            translated_query = query.replace(source, target)

    lawyers = Lawyer.objects.select_related('office_card', 'user').prefetch_related('specializations').all()
    if query:
        lawyers = lawyers.filter(
            Q(name__icontains=query)
            | Q(email__icontains=query)
            | Q(specialization__icontains=query)
            | Q(specialization__icontains=translated_query)
            | Q(specializations__name__icontains=query)
        ).distinct()
    return render(request, "lawyer/lawyer_list.html", {"lawyers": lawyers, "is_admin": is_admin_user(request.user), "query": query})


@login_required
@user_passes_test(is_admin_user)
def lawyer_add(request):
    if request.method == "POST":
        form = LawyerForm(request.POST, request.FILES)
        if form.is_valid():
            lawyer = form.save()
            # تطبيق علاقة 1-to-1 تلقائياً عن طريق إنشاء بطاقة مكتبية
            OfficeCard.objects.get_or_create(
                lawyer=lawyer,
                defaults={
                    'card_number': f'LIC-{lawyer.id}-2024',
                    'office_room': 'قاعة الاستشارات الرئيسية'
                }
            )
            messages.success(request, 'تمت إضافة المحامي وإنشاء بطاقته المكتبية (One-to-One) وتعيين التخصصات (Many-to-Many) بنجاح')
            return redirect("lawyer:lawyer_list")
    else:
        form = LawyerForm()
    return render(
        request,
        "lawyer/lawyer_form.html",
        {"form": form, "title": "إضافة محامي جديد"},
    )


@login_required
@user_passes_test(is_admin_user)
def lawyer_edit(request, pk):
    lawyer = get_object_or_404(Lawyer, pk=pk)
    if request.method == "POST":
        form = LawyerForm(request.POST, request.FILES, instance=lawyer)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل بيانات المحامي وتخصصاته الفرعية')
            return redirect("lawyer:lawyer_list")
    else:
        form = LawyerForm(instance=lawyer)
    return render(
        request,
        "lawyer/lawyer_form.html",
        {"form": form, "title": "تعديل بيانات المحامي"},
    )

@login_required
@user_passes_test(is_admin_user)
def lawyer_delete(request, pk):
    lawyer = get_object_or_404(Lawyer, pk=pk)
    if request.method == "POST":
        lawyer.delete()
        messages.success(request, "تم حذف المحامي")
        return redirect("lawyer:lawyer_list")
    return render(
        request, "lawyer/lawyer_confirm_delete.html", {"lawyer": lawyer}
    )

@login_required
def case_create(request):
    if request.method == "POST":
        form = CaseRequestForm(request.POST)
        if form.is_valid():
            case = form.save(commit=False)
            case.user = request.user
            case.save()

            # إرسال تأكيد للعميل
            if request.user.email:
                send_mail(
                    "تم استلام طلب القضية",
                    f"""مرحبًا {request.user.username}،

تم استلام طلب القضية الخاص بك بنجاح.

نوع القضية: {case.case_type}
نوع الطلب: {case.application_type}

سيتم مراجعة طلبك والتعامل معه من قبل المكتب.

شكرًا لاستخدامك Vision Law Office.""",
                    None,
                    [request.user.email],
                    fail_silently=False,
                )

            # إرسال إشعار للمكتب
            admin_email = getattr(settings, "EMAIL_HOST_USER", None)
            if admin_email:
                send_mail(
                    "🚨 قضية جديدة في Vision Law Office",
                    f"""تم استلام قضية جديدة من أحد العملاء.

بيانات القضية:
-------------------------
اسم العميل: {request.user.get_full_name() or request.user.username}
البريد الإلكتروني: {request.user.email}
نوع القضية: {case.case_type}
نوع الطلب: {case.application_type}

تفاصيل القضية:
{case.description}

حالة القضية: جديدة

يرجى الدخول إلى لوحة الإدارة لمراجعة القضية وتعيين محامٍ لها.

Vision Law Office""",
                    None,
                    [admin_email],
                    fail_silently=False,
                )

            messages.success(
                request, "تم إرسال القضية بنجاح وعرضها في لوحة الحساب"
            )
            return redirect("account:dashboard")
    else:
        form = CaseRequestForm()

    return render(
        request,
        "lawyer/case_form.html",
        {"form": form, "title": "إرسال قضية جديدة"},
    )
@login_required
def case_list(request):
    query = request.GET.get("q", "")
    if is_admin_user(request.user):
        cases = CaseRequest.objects.select_related('user', 'lawyer').all().order_by('-created_at')
        if query:
            cases = cases.filter(
                Q(case_type__icontains=query) | Q(application_type__icontains=query) | Q(description__icontains=query) | Q(user__username__icontains=query)
            )
        case_forms = [(case, CaseAssignmentForm(instance=case)) for case in cases]
    else:
        cases = CaseRequest.objects.filter(user=request.user).select_related('lawyer').order_by('-created_at')
        if query:
            cases = cases.filter(
                Q(case_type__icontains=query) | Q(application_type__icontains=query) | Q(description__icontains=query)
            )
        case_forms = [(case, None) for case in cases]

    return render(request, "lawyer/case_list.html", {"case_forms": case_forms, "is_admin": is_admin_user(request.user), "query": query})


@login_required
@user_passes_test(is_admin_user)
def case_assign(request, pk):
    case = get_object_or_404(CaseRequest, pk=pk)

    if request.method == "POST":
        old_lawyer = case.lawyer
        old_status = case.status

        form = CaseAssignmentForm(request.POST, instance=case)

        if form.is_valid():
            case = form.save()

            client_email = case.user.email if case.user else None

            # 1. تم تعيين محامي جديد
            if (
                case.lawyer
                and case.lawyer != old_lawyer
                and client_email
            ):
                send_mail(
                    "تم تعيين محامٍ لقضيتك",
                    f"""مرحبًا {case.user.username}،

تم تعيين المحامي {case.lawyer.name} لمتابعة قضيتك.

نوع القضية: {case.case_type}
نوع الطلب: {case.application_type}

سيتم التواصل معك ومتابعة القضية من خلال المكتب.

شكرًا لاستخدامك Vision Law Office.
""",
                    None,
                    [client_email],
                    fail_silently=False,
                )

            # 2. القضية أصبحت قيد التنفيذ
            if (
                case.status == "in_progress"
                and old_status != "in_progress"
                and client_email
            ):
                send_mail(
                    "بدأت معالجة قضيتك",
                    f"""مرحبًا {case.user.username}،

نود إبلاغك بأن قضيتك أصبحت الآن قيد التنفيذ.

نوع القضية: {case.case_type}
المحامي المسؤول: {case.lawyer.name if case.lawyer else "سيتم التعيين لاحقًا"}

بدأ المكتب في معالجة طلبك.

شكرًا لاستخدامك Vision Law Office.
""",
                    None,
                    [client_email],
                    fail_silently=False,
                )

            # 3. القضية أغلقت
            if (
                case.status == "closed"
                and old_status != "closed"
                and client_email
            ):
                send_mail(
                    "تم إغلاق قضيتك",
                    f"""مرحبًا {case.user.username}،

نود إبلاغك بأنه تم إغلاق قضيتك.

نوع القضية: {case.case_type}
نوع الطلب: {case.application_type}

شكرًا لاستخدامك Vision Law Office.
""",
                    None,
                    [client_email],
                    fail_silently=False,
                )

            messages.success(
                request,
                "تم تحديث القضية وإرسال الإشعار المناسب للعميل"
            )

    return redirect("lawyer:case_list")


@login_required
@user_passes_test(is_admin_user)
def contact_messages(request):
    messages_list = ContactMessage.objects.order_by('-sent_at')
    reply_forms = []
    for message in messages_list:
        reply_forms.append((message, ReplyForm(instance=message)))
    return render(request, 'lawyer/contact_messages.html', {'reply_forms': reply_forms})


@login_required
@user_passes_test(is_admin_user)
def reply_message(request, pk):
    message = get_object_or_404(ContactMessage, pk=pk)

    if request.method == "POST":
        form = ReplyForm(request.POST, instance=message)
        if form.is_valid():
            message = form.save()

            if message.user and message.user.email and message.reply:
                send_mail(
                    f"رد على رسالتك: {message.subject}",
                    f"""مرحبًا {message.name}،

تم الرد على رسالتك من Vision Law Office.

الرد:
{message.reply}

شكرًا لتواصلك معنا.""",
                    None,
                    [message.user.email],
                    fail_silently=False,
                )

            messages.success(
                request, "تم حفظ الرد وإرساله إلى بريد المستخدم بنجاح"
            )
            return redirect("lawyer:message_list")
    else:
        form = ReplyForm(instance=message)

    return render(
        request,
        "lawyer/reply_message.html",
        {"form": form, "message": message},
    )
# ==============================================================================
#                 تكليف هندسة البرمجيات (SOFTWARE ENGINEERING HW)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1 & 2. تطبيق دوال QuerySet 
# ------------------------------------------------------------------------------
def homework_queryset_demo(request):
    """
    دالة تجميع استعلامات QuerySet المعتمدة في التكليف (7 دوال على الأقل في مكان واحد):
    الدالة 1: filter()         - تصفية النتائج بناء على شرط معين
    الدالة 2: exclude()        - استبعاد العناصر التي تحقق شرطاً معينًا
    الدالة 3: order_by()       - ترتيب النتائج تصاعدياً أو تنازلياً
    الدالة 4: select_related() - جلب العلاقات 1-to-1 و Foreign Key بحزام استعلام واحد (SQL JOIN)
    الدالة 5: prefetch_related()- جلب العلاقات Many-to-Many بكفاءة عالية
    الدالة 6: annotate()       - تجميع وإضافة حقول مخصصة (مثل عدد القضايا لكل محام)
    الدالة 7: aggregate()      - حساب القيم الإجمالية (متوسط، أعلى قيمة، أقل قيمة)
    الدالة 8: values()         - تحديد حقول معينة بدلا من الكائن الكامل
    الدالة 9: count()          - حساب العدد الإجمالي للنتائج
    الدالة 10: exists()        - فحص وجود بيانات من عدمه
    """
    # 1. filter() - تصفية المحامين الذين لديهم خبرة أكبر من سنتين
    qs_filter = Lawyer.objects.filter(experience_years__gt=2)

    # 2. exclude() - استبعاد المحامين الذين ليس لديهم تخصص محدد
    qs_exclude = Lawyer.objects.exclude(specialization="")

    # 3. order_by() - ترتيب المحامين تنازلياً حسب سنوات الخبرة
    qs_order_by = Lawyer.objects.order_by('-experience_years')

    # 4. select_related() - تحسين استعلام 1-to-1 (البطاقة المكتبية والمستخدم)
    qs_select_related = Lawyer.objects.select_related('office_card', 'user').all()

    # 5. prefetch_related() - تحسين استعلام Many-to-Many (التخصصات الفرعية)
    qs_prefetch_related = Lawyer.objects.prefetch_related('specializations').all()

    # 6. annotate() - حساب عدد القضايا لكل محامٍ
    qs_annotate = Lawyer.objects.annotate(total_cases=Count('caserequest'))

    # 7. aggregate() - حساب متوسط وأعلى وأقل سنوات خبرة
    qs_aggregate = Lawyer.objects.aggregate(
        avg_experience=Avg('experience_years'),
        max_experience=Max('experience_years'),
        min_experience=Min('experience_years')
    )

    # 8. values() - جلب حقول محددة فقط (الاسم والتخصص)
    qs_values = Lawyer.objects.values('id', 'name', 'specialization', 'experience_years')

    # 9. count() - حساب عدد المحامين المسجلين
    total_lawyers_count = Lawyer.objects.count()

    # 10. exists() - فحص وجود محامين في النظام
    has_lawyers = Lawyer.objects.exists()

    context = {
        "title": "دوال QuerySet السبع المعتمدة في التكليف",
        "qs_filter": qs_filter,
        "qs_exclude": qs_exclude,
        "qs_order_by": qs_order_by,
        "qs_select_related": qs_select_related,
        "qs_prefetch_related": qs_prefetch_related,
        "qs_annotate": qs_annotate,
        "qs_aggregate": qs_aggregate,
        "qs_values": list(qs_values),
        "total_lawyers_count": total_lawyers_count,
        "has_lawyers": has_lawyers,
    }
    return render(request, "lawyer/queryset_homework.html", context)


# ------------------------------------------------------------------------------
# 3. استعراض طرق كتابة الفورم الثلاث (Forms 3 Ways Demo)
# ------------------------------------------------------------------------------
def homework_forms_demo(request):
    """
    استعراض وإدارة طرق كتابة الفورم الثلاث:
    - الطريقة الأولى: ModelForm (LawyerForm)
    - الطريقة الثانية: forms.Form (QuickConsultationForm)
    - الطريقة الثالثة: HTML Form يدوي ينعكس في View (Manual Handling)
    """
    model_form = LawyerForm(prefix="model_form")
    standard_form = QuickConsultationForm(prefix="standard_form")

    # معالجة إرسال النموذج المستقل (Method 2: forms.Form)
    if request.method == "POST" and "submit_standard" in request.POST:
        standard_form = QuickConsultationForm(request.POST, prefix="standard_form")
        if standard_form.is_valid():
            data = standard_form.cleaned_data
            messages.success(
                request,
                f"تم استقبال استشارتك بنجاح عبر (forms.Form)! الاسم: {data['full_name']} | نوع الاستشارة: {data['consultation_type']}"
            )
            return redirect("lawyer:forms_demo")

    # معالجة إرسال الفورم اليدوي HTML (Method 3: Raw HTML Form)
    if request.method == "POST" and "submit_manual_html" in request.POST:
        raw_name = request.POST.get("raw_name", "").strip()
        raw_phone = request.POST.get("raw_phone", "").strip()
        raw_subject = request.POST.get("raw_subject", "").strip()
        raw_message = request.POST.get("raw_message", "").strip()

        if raw_name and raw_message:
            ContactMessage.objects.create(
                name=raw_name,
                phone=raw_phone,
                subject=raw_subject or "استفسار يدوي من HTML Form",
                message=raw_message,
                user=request.user if request.user.is_authenticated else None
            )
            messages.success(request, f"تمت معالجة وحفظ البيانات مباشرة في الـ View من HTML Form اليدوي للعميل: {raw_name}")
            return redirect("lawyer:forms_demo")
        else:
            messages.error(request, "يرجى كتابة الاسم والرسالة في HTML Form")

    context = {
        "title": "طرق كتابة الفورم الثلاث في Django",
        "model_form": model_form,
        "standard_form": standard_form,
    }
    return render(request, "lawyer/forms_demo.html", context)


# ------------------------------------------------------------------------------
# 4. إدارة التخصصات والبطاقة المكتبية (CRUD التخصصات Many-to-Many و البطاقة 1-to-1)
# ------------------------------------------------------------------------------
@login_required
@user_passes_test(is_admin_user)
def specialization_list(request):
    specializations = Specialization.objects.annotate(lawyers_count=Count('lawyers'))
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if name:
            Specialization.objects.create(name=name, description=description)
            messages.success(request, "تمت إضافة التخصص الفرعي بنجاح (Many-to-Many)")
            return redirect("lawyer:specialization_list")
    return render(request, "lawyer/specialization_list.html", {"specializations": specializations})


@login_required
@user_passes_test(is_admin_user)
def specialization_delete(request, pk):
    spec = get_object_or_404(Specialization, pk=pk)
    if request.method == "POST":
        spec.delete()
        messages.success(request, "تم حذف التخصص الفرعي بنجاح")
    return redirect("lawyer:specialization_list")


@login_required
@user_passes_test(is_admin_user)
def office_card_edit(request, lawyer_id):
    lawyer = get_object_or_404(Lawyer, pk=lawyer_id)
    card, created = OfficeCard.objects.get_or_create(
        lawyer=lawyer,
        defaults={'card_number': f'LIC-{lawyer.id}-2024', 'office_room': 'المكتب الرئيسي - القاعة A'}
    )
    if request.method == "POST":
        form = OfficeCardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            messages.success(request, f"تم تحديث البطاقة المكتبية (One-to-One) للمحامي {lawyer.name}")
            return redirect("lawyer:lawyer_list")
    else:
        form = OfficeCardForm(instance=card)
    return render(request, "lawyer/office_card_form.html", {"form": form, "lawyer": lawyer})