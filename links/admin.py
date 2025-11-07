from django.contrib import admin

from .models import ShortLink


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ("short_code", "original_url", "created_at", "click_count")
    search_fields = ("short_code", "original_url")
    ordering = ("-created_at",)
