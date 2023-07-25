from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "tag",
        "language",
        "text",
    )
    raw_id_fields = []
    readonly_fields = ["id"]
