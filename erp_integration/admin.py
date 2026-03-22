from django.contrib import admin
from .models import FinanceRecord


@admin.register(FinanceRecord)
class FinanceRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "status", "reference", "updated_at")
    list_filter = ("status",)
    search_fields = ("student__student_number", "student__user__username", "reference")