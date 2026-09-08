from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الفرع")
    city = models.CharField(max_length=50, verbose_name="المدينة")
    address = models.TextField(verbose_name="العنوان التفصيلي")

    class Meta:
        verbose_name = "فرع"
        verbose_name_plural = "الفروع"

    def __str__(self):
        return f"{self.name} - {self.city}"


class ServiceType(models.Model):
    name = models.CharField(max_length=100, verbose_name="نوع الخدمة")
    description = models.TextField(verbose_name="وصف الخدمة")
    base_fee = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="الأتعاب"
    )

    class Meta:
        verbose_name = "نوع خدمة"
        verbose_name_plural = "أنواع الخدمات"

    def __str__(self):
        return self.name