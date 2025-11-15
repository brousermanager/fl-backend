import html
import re
import uuid
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from rest_framework import serializers

from podcast_collection.models import PodcastCollection
from podcaster.models import Podcaster


# Create your models here.
class Podcast(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True, unique=True)
    duration = models.IntegerField(null=True, blank=True)
    audio_file = models.FileField(
        upload_to=settings.AUDIO_UPLOAD_FOLDER, null=True, blank=True, max_length=500
    )
    audio_url = models.URLField(max_length=500, blank=True)
    cover_file = models.ImageField(
        upload_to=settings.COVER_UPLOAD_FOLDER, null=True, blank=True, max_length=500
    )
    cover_url = models.URLField(max_length=500, blank=True)
    insert_time = models.DateTimeField(null=True)
    update_time = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(
        PodcastCollection, on_delete=models.CASCADE, null=True, blank=True
    )
    podcasters = models.ManyToManyField(Podcaster, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_values = {
            field.name: getattr(self, field.name) for field in self._meta.get_fields()
        }

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    # override save method to add audio_url field
    def save(self, *args, **kwargs):
        self.title = html.unescape(self.title)
        self.description = html.unescape(self.description)

        if "audio_file" in self.changed_fields:
            key = f"{settings.AUDIO_UPLOAD_FOLDER}{self.audio_file.name}"
            self.audio_url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.amazonaws.com/{key}"
        if "cover_file" in self.changed_fields:
            key = f"{settings.COVER_UPLOAD_FOLDER}{self.cover_file.name}"
            self.cover_url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.amazonaws.com/{key}"

        if self.insert_time is None:
            self.insert_time = datetime.now().time()

        # Update the collection's update_time if a collection is associated
        if self.collection and self.pk is None:
            self.collection.update_time = datetime.now()
            self.collection.save()

        super().save(*args, **kwargs)

    @property
    def changed_fields(self):
        return {
            field.name: getattr(self, field.name)
            for field in self._meta.get_fields()
            if getattr(self, field.name) != self.initial_values[field.name]
        }

    def clean(self):
        super().clean()
        # Only allow letters, numbers, dots, underscores, and hyphens
        allowed_pattern = re.compile(r"^[A-Za-z0-9._-]+$")
        if self.audio_file and "audio_file" in self.changed_fields:
            if not allowed_pattern.match(self.audio_file.name):
                raise ValidationError(
                    {
                        "audio_file": "File name can only contain letters, numbers, dots, underscores, and hyphens."
                    }
                )
        if self.cover_file and "cover_file" in self.changed_fields:
            if not allowed_pattern.match(self.cover_file.name):
                raise ValidationError(
                    {
                        "cover_file": "File name can only contain letters, numbers, dots, underscores, and hyphens."
                    }
                )


class PodcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Podcast
        fields = "__all__"
