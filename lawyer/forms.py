from django import forms
from .models import CaseRequest, ContactMessage, Lawyer, OfficeCard, Specialization


# ==============================================================================
# طرق كتابة الفورم الثلاث في Django (تلبية للتكليف الدراسي)
# ==============================================================================

# ------------------------------------------------------------------------------
# الطريقة الأولى: ModelForm (الفورم القائم على النموذج مباشرة)
# ------------------------------------------------------------------------------
class LawyerForm(forms.ModelForm):
    # إضافة حقل اختيار التخصصات الفرعية (كثير إلى كثير - Many-to-Many)
    specializations = forms.ModelMultipleChoiceField(
        queryset=Specialization.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'specialization-checkboxes'}),
        required=False,
        label="التخصصات الفرعية (Many-to-Many)"
    )

    class Meta:
        model = Lawyer
        fields = ['name', 'phone', 'email', 'image', 'experience_years', 'specialization', 'specializations']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'اسم المحامي الكامل'}),
            'phone': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'رقم الجوال'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'البريد الإلكتروني'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control bg-dark text-light border-secondary'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'سنوات الخبرة'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'التخصص الرئيسية'}),
        }


class OfficeCardForm(forms.ModelForm):
    """فورم البطاقة المكتبية للمحامي (تطبيق One-to-One)"""
    class Meta:
        model = OfficeCard
        fields = ['card_number', 'office_room']
        widgets = {
            'card_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: LIC-2024-99'}),
            'office_room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: قاعة 3 - الدور الثاني'}),
        }


class CaseRequestForm(forms.ModelForm):
    class Meta:
        model = CaseRequest
        fields = ['case_type', 'application_type', 'description']
        widgets = {
            'case_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: دعوى مالية'}),
            'application_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: تطبيق تعويض'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'اكتب تفاصيل القضية'}),
        }


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسمك الكريم'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل رقم جوالك'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'موضوع الاستفسار'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'اكتب تفاصيل الاستفسار أو القضية'}),
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['reply', 'is_replied']
        widgets = {
            'reply': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'اكتب رد الإدارة'}),
            'is_replied': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CaseAssignmentForm(forms.ModelForm):
    class Meta:
        model = CaseRequest
        fields = ['lawyer', 'status']
        widgets = {
            'lawyer': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


# ------------------------------------------------------------------------------
# الطريقة الثانية: forms.Form (الفورم المخصص العادي المستقل عن Model)
# ------------------------------------------------------------------------------
class QuickConsultationForm(forms.Form):
    """
    نموذج استشارة سريعة كـ (forms.Form) عادي غير مرتقب بموديل مباشر.
    يتم التعامل مع البيانات فيه برمجياً في الـ View.
    """
    CONSULTATION_TYPES = [
        ('commercial', 'استشارة تجارية'),
        ('labor', 'استشارة عمالية'),
        ('real_estate', 'استشارة عقارية'),
        ('personal', 'أحوال شخصية'),
    ]

    full_name = forms.CharField(
        max_length=100,
        label="الاسم الكامل",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل الاسم'})
    )
    email_address = forms.EmailField(
        label="البريد الإلكتروني",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@domain.com'})
    )
    consultation_type = forms.ChoiceField(
        choices=CONSULTATION_TYPES,
        label="نوع الاستشارة",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    urgency_level = forms.ChoiceField(
        choices=[('normal', 'عادي'), ('urgent', 'مستعجل جداً')],
        label="مستوى الأهمية",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    details = forms.CharField(
        label="تفاصيل الاستشارة",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'اكتب ملخص الاستشارة'})
    )


# ------------------------------------------------------------------------------
# الطريقة الثالثة: (HTML Raw Form)
# يتم استقبال البيانات مباشرة من request.POST وحفظها يدويًا في الـ View
# دون استخدام أي كلاس من forms.py (تم تطبيقها في دوال View باسم manual_contact_create).
# ------------------------------------------------------------------------------