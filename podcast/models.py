import os
import uuid
import boto3
import tempfile
import requests
from urllib.parse import quote
from datetime import datetime
from django.db import models
from rest_framework import serializers
from django.conf import settings
from mutagen.mp3 import MP3
from podcast_collection.models import PodcastCollection
from podcaster.models import Podcaster


audio_upload_folder = "MP3_PODCAST/"
cover_upload_folder = "podcast_covers/"

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")


s3 = boto3.client(
    service_name="s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name="eu-north-1",
)
# Create your models here.
class Podcast(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    audio_file = models.FileField(
        upload_to=audio_upload_folder, null=True, blank=True, max_length=500
    )
    audio_url = models.URLField(max_length=500, null=True, blank=True)
    cover_file = models.ImageField(
        upload_to=cover_upload_folder, null=True, blank=True, max_length=500
    )
    cover_url = models.URLField(max_length=500, null=True, blank=True)
    insert_time = models.DateTimeField(null=True)
    update_time = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(
        PodcastCollection, on_delete=models.CASCADE, null=True, blank=True
    )
    podcasters = models.ManyToManyField(Podcaster, blank=True)

    def __unicode__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_values = {
            field.name: getattr(self, field.name) for field in self._meta.get_fields()
        }

    @property
    def changed_fields(self):
        return {
            field.name: getattr(self, field.name)
            for field in self._meta.get_fields()
            if getattr(self, field.name) != self.initial_values[field.name]
        }

    # override save method to add audio_url field
    def save(self, *args, **kwargs):
        sf = "~()*!.'%"  # safe characters, including %

        if "audio_file" in self.changed_fields:
            filename = quote(self.audio_file.name.replace(" ", "_"), safe=sf)
            key = f"{audio_upload_folder}{filename}"
            self.audio_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"
        if "cover_file" in self.changed_fields:
            filename = quote(self.cover_file.name.replace(" ", "_"), safe=sf)
            key = f"{cover_upload_folder}{filename}"
            self.cover_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"

        if self.insert_time is None:
            self.insert_time = datetime.now().time()
        if self.audio_url:
            try:
                # Download the file and save it to a temporary file
                response = requests.get(self.audio_url)
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.write(response.content)
                temp_file.close()

                # Use mutagen to get the duration of the MP3 file
                audio = MP3(temp_file.name)
                os.remove(temp_file.name)

                self.duration = audio.info.length
            except:
                print("Error getting duration of audio file")

        super().save(*args, **kwargs)


class PodcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Podcast
        fields = "__all__"
