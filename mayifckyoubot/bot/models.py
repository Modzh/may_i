import uuid

from bot.localize import Language
from django.db import models
from tinymce.models import HTMLField  # noqa: F401


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tag = models.CharField(max_length=255, blank=True, null=True, default=None)
    language = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default=None,
        choices=[(lang, lang) for lang in Language],
    )
    text = models.TextField(blank=True)

    def __str__(self):
        return f"{self.tag} :: {self.text[:50]}"  # noqa: E231

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["tag", "language"], name="tag_language_unique"
            ),
        )
