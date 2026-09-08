from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    phone_number = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="رقم الهاتف"
    )
    is_lawyer = models.BooleanField(default=False, verbose_name="هل هو محامي؟")
    is_client = models.BooleanField(default=True, verbose_name="هل هو موكل؟")
    welcome_email_sent = models.BooleanField(default=False, verbose_name="تم إرسال رسالة الترحيب")

    def __str__(self):
        return self.username


class LawyerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name="المستخدم")
    license_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الرخصة المهنية")
    specialization = models.CharField(max_length=100, verbose_name="التخصص القانوني")
    is_approved = models.BooleanField(default=False, verbose_name="معتمد من الإدارة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.specialization}"