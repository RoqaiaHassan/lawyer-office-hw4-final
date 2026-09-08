from django.contrib import admin
from .models import CaseRequest, ContactMessage, Lawyer, OfficeCard, Service, Specialization


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name", "description")


@admin.register(OfficeCard)
class OfficeCardAdmin(admin.ModelAdmin):
    list_display = ("id", "lawyer", "card_number", "office_room", "issued_date")
    search_fields = ("card_number", "office_room", "lawyer__name")


@admin.register(Lawyer)
class LawyerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "phone", "email", "experience_years", "specialization")
    list_display_links = ("id", "name")
    search_fields = ("name", "email", "specialization", "user__username", "user__email")
    list_filter = ("specialization", "experience_years")
    filter_horizontal = ("specializations",)
    ordering = ("id",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price")
    list_display_links = ("id", "title")
    search_fields = ("title", "description")
    list_filter = ("price",)
    ordering = ("id",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "phone", "subject", "is_replied", "sent_at")
    list_display_links = ("id", "name")
    search_fields = ("name", "phone", "subject", "message", "user__username")
    list_filter = ("subject", "is_replied", "sent_at")
    ordering = ("-sent_at",)
    readonly_fields = ("name", "phone", "subject", "message", "sent_at")


@admin.register(CaseRequest)
class CaseRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "lawyer", "case_type", "application_type", "status", "created_at")
    list_display_links = ("id", "user", "case_type")
    search_fields = ("user__username", "case_type", "application_type", "description")
    list_filter = ("status", "created_at", "lawyer")
    ordering = ("-created_at",)