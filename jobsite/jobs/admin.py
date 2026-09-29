from django.contrib import admin

# Register your models here.
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'company_name',
        'location',
        'is_remote',
        'visa_sponsorship',
        'created_at',
    )

    search_fields = (
        'title',
        'company_name',
        'skills',
        'location',
    )

    list_filter = (
        'is_remote',
        'visa_sponsorship',
    )
