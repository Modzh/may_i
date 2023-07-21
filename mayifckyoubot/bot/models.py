import uuid

from django.db import models
from tinymce.models import HTMLField  # noqa: F401


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(blank=True)
    is_first_question = models.BooleanField(default=False)
    previous_question = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="next_question",
    )

    def save(self, *args, **kwargs):
        if self.is_first_question:
            Question.objects.filter(is_first_question=True).update(
                is_first_question=False
            )
        super(Question, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} :: {self.text[:50]}"  # noqa: E231
