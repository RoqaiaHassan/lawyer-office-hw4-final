from django.contrib import admin
from .models import Branch, ServiceType


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city", "address")
    search_fields = ("name", "city")
    list_filter = ("city",)
    ordering = ("-id",)


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "base_fee", "description")
    search_fields = ("name",)
    list_editable = ("base_fee",)
    ordering = ("name",)