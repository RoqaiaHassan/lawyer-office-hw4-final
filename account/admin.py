from django.contrib import admin
from .models import LawyerProfile


@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "license_number",
        "specialization",
        "is_approved",
        "created_at",
    )
    list_display_links = ("id", "user", "license_number")
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "license_number",
        "specialization",
    )
    list_filter = ("is_approved", "specialization", "created_at")
    ordering = ("-id",)
    list_editable = ("is_approved",)
    fieldsets = (
        (
            "بيانات الحساب الأساسية",
            {"fields": ("user", "license_number")},
        ),
        (
            "التفاصيل المهنية",
            {"fields": ("specialization",)},
        ),
        (
            "حالة الاعتماد",
            {"fields": ("is_approved",)},
        ),
    )