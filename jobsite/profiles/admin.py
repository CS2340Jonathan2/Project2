from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'headline', 'commute_radius', 'is_visible_to_recruiters')
    list_filter = ('is_visible_to_recruiters',)
    search_fields = ('user__username', 'headline', 'skills')
