from django.conf import settings
from django.db import models


class Specialization(models.Model):
    """
    نموذج التخصصات القانونية - يُستخدم في تطبيق علاقة (كثير إلى كثير - Many-to-Many)
    """
    name = models.CharField(max_length=100, verbose_name="اسم التخصص الفرعي")
    description = models.TextField(blank=True, verbose_name="وصف التخصص")

    class Meta:
        verbose_name = "تخصص فرعي"
        verbose_name_plural = "التخصصات الفرعية"

    def __str__(self):
        return self.name


class Lawyer(models.Model):
    # 1. علاقة من واحد إلى واحد (One-to-One Relationship)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المستخدم",
        help_text="ارتباط هذا السجل بمستخدم مسجل إذا كان المحامي يملك حسابًا",
    )
    name = models.CharField(max_length=100, verbose_name="اسم المحامي")
    phone = models.CharField(max_length=20, verbose_name="رقم الجوال")
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    image = models.ImageField(upload_to='lawyers/', blank=True, null=True, verbose_name='صورة المحامي')
    experience_years = models.PositiveIntegerField(default=0, verbose_name="سنوات الخبرة")
    specialization = models.CharField(max_length=150, verbose_name="التخصص الرئيسي")

    # 2. علاقة من كثير إلى كثير (Many-to-Many Relationship)
    specializations = models.ManyToManyField(
        Specialization,
        blank=True,
        related_name="lawyers",
        verbose_name="التخصصات الفرعية (كثير إلى كثير)"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    def __str__(self):
        return self.name


class OfficeCard(models.Model):
    """
    نموذج البطاقة المكتبية للمحامي - تطبيق إضافي ومباشر لعلاقة (واحد إلى واحد - One-to-One)
    """
    lawyer = models.OneToOneField(
        Lawyer,
        on_delete=models.CASCADE,
        related_name="office_card",
        verbose_name="المحامي"
    )
    card_number = models.CharField(max_length=50, unique=True, verbose_name="رقم البطاقة المهنية")
    office_room = models.CharField(max_length=50, verbose_name="رقم القاعة / المكتب")
    issued_date = models.DateField(auto_now_add=True, verbose_name="تاريخ الإصدار")

    class Meta:
        verbose_name = "بطاقة مكتبية"
        verbose_name_plural = "البطاقات المكتبية"

    def __str__(self):
        return f"بطاقة {self.lawyer.name} ({self.card_number})"


class Service(models.Model):
    title = models.CharField(max_length=150, verbose_name="عنوان الخدمة")
    description = models.TextField(verbose_name="وصف الخدمة")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="تبدأ الأتعاب من")
    icon_class = models.CharField(max_length=50, default="fa-solid fa-briefcase", verbose_name="أيقونة FontAwesome")

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="الاسم الكامل")
    phone = models.CharField(max_length=20, verbose_name="رقم الجوال")
    subject = models.CharField(max_length=100, verbose_name="نوع الخدمة / الموضوع")
    message = models.TextField(verbose_name="الرسالة")
    # ربط رسالة الاتصال بمستخدم مسجّل إن وُجد
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المستخدم المرسل",
    )
    reply = models.TextField(blank=True, null=True, verbose_name="الرد الإداري")
    is_replied = models.BooleanField(default=False, verbose_name="تم الرد")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")

    def __str__(self):
        return f"رسالة من {self.name} - {self.subject}"


class CaseRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'جديد'),
        ('assigned', 'تم التعيين'),
        ('in_progress', 'قيد التنفيذ'),
        ('closed', 'مغلق'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="العميل")
    lawyer = models.ForeignKey(Lawyer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المحامي")
    case_type = models.CharField(max_length=120, verbose_name="نوع القضية")
    application_type = models.CharField(max_length=120, verbose_name="نوع التطبيق")
    description = models.TextField(verbose_name="وصف القضية")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='الحالة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإرسال')

    def __str__(self):
        return f"{self.case_type} - {self.user.username}"