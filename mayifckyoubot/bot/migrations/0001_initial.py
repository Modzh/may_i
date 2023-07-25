# Generated by Django 4.2.3 on 2023-07-25 10:19

import uuid

import bot.localize
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Document",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "tag",
                    models.CharField(
                        blank=True, default=None, max_length=255, null=True
                    ),
                ),
                (
                    "language",
                    models.CharField(
                        blank=True,
                        choices=[
                            (bot.localize.Language["EN"], bot.localize.Language["EN"]),
                            (bot.localize.Language["RU"], bot.localize.Language["RU"]),
                        ],
                        default=None,
                        max_length=255,
                        null=True,
                    ),
                ),
                ("text", models.TextField(blank=True)),
            ],
        ),
        migrations.AddConstraint(
            model_name="document",
            constraint=models.UniqueConstraint(
                fields=("tag", "language"), name="tag_language_unique"
            ),
        ),
    ]
