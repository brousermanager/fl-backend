import os
import boto3
from datetime import datetime, date
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed

from podcast.models import Podcast

PODCAST_LIMIT: int = int(os.getenv("PODCAST_LIMIT", 150))
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")

HOST_BASE_URL = os.getenv("PROD_HOST")
email = os.getenv("EMAIL", "rfl.radiofrequenzalibera@gmail.com")

s3 = boto3.client(
    service_name="s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name="eu-north-1",
)

bucket_url = f"https://{BUCKET_NAME}.s3.{s3.meta.region_name}.amazonaws.com/"


class iTunesPodcastsFeedGenerator(Rss201rev2Feed):
    def rss_attributes(self):
        return {
            "version": self._version,
            "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
            "xmlns:atom": "http://www.w3.org/2005/Atom",
        }

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        handler.startElement("itunes:image", {"href": item["enclosure_cover"]})
        handler.endElement("itunes:image")

    def add_root_elements(self, handler):
        super().add_root_elements(handler)
        handler.addQuickElement(
            "managingEditor",
            email,
        )

        handler.addQuickElement("itunes:author", "Radio Frequenza Libera")
        handler.addQuickElement("itunes:explicit", "false")
        handler.startElement(
            "itunes:image",
            {
                "href": "https://podcast-fl.s3.eu-north-1.amazonaws.com/podcast_media_generics/foto+profilo.jpg"
            },
        )
        handler.endElement("itunes:image")
        handler.startElement("itunes:category", {"text": "Arts"})
        handler.endElement("itunes:category")
        handler.startElement(
            "itunes:category", {"text": "Games & Hobbies"}
        )  # Change this line
        handler.endElement("itunes:category")
        handler.startElement(
            "itunes:category", {"text": "Government"}
        )  # Change this line
        handler.endElement("itunes:category")

        handler.startElement("itunes:owner", {})
        handler.addQuickElement("itunes:name", "Radio Frequenza Libera")
        handler.addQuickElement("itunes:email", email)
        handler.endElement("itunes:owner")


class PodcastFeed(Feed):
    feed_type = iTunesPodcastsFeedGenerator
    title = "Podcast Radio Frequenza Libera"
    link = f"https:{HOST_BASE_URL}/feed/rss/"  # Change this line
    description = "Dal 2013 frequenza Libera vive e da voce agli studenti e alle studentesse degli atenei senza distinzione, " \
            "associazione web radio fondata dagli stessi in modalità volontaria.Patrocinata dal Politecnico di Bari, è tutt'ora " \
            "uno spazio di incontro, collaborazione, contaminazione e diffusione. Dai podcast intrattenitivi o divulgativi alle " \
            "chiacchierate e interviste con ospiti tra i più svariati, dagli artisti, registi, professori e tanto altro... Seguici, e vedi che ti ascolti!"
    author_name = "Radio Frequenza Libera"
    author_email = email
    categories = ("Arts", "Games & Hobbies > Video Games", "News & Politics")
    image = "https://podcast-fl.s3.eu-north-1.amazonaws.com/podcast_media_generics/foto+profilo.jpg"
    language = "it"

    def items(self):
        return Podcast.objects.all().order_by("-insert_time")[:PODCAST_LIMIT]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return item.audio_url

    def item_enclosure_url(self, item):
        return item.audio_url

    def item_enclosure_length(self, item):
        return item.duration

    def item_enclosure_mime_type(self, item):
        return "audio/mpeg"

    def item_enclosure_cover(self, item):
        return item.cover_url

    def item_guid(self, item):  # Add this method
        return item.audio_url

    def item_explicit(self, item):  # Add this method
        return "no"

    def item_pubdate(self, item):
        # Combine the current date with the time
        return item.insert_time

    def item_extra_kwargs(self, item):
        return {"enclosure_cover": self.item_enclosure_cover(item)}
