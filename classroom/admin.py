from django.contrib import admin

from .models import LiveClass


@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "subject", "date", "time", "is_active", "created_at")
    list_filter = ("is_active", "subject", "course", "date")
    search_fields = ("title", "subject", "description", "course__title")
    ordering = ("date", "time")
