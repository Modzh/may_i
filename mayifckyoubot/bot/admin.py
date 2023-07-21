from django.contrib import admin

from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "is_first_question", "previous_question")
    raw_id_fields = ["previous_question"]
    readonly_fields = ["id"]
