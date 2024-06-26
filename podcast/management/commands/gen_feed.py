from django.core.management.base import BaseCommand
from django.test.client import Client
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = "Save RSS feed to S3"

    def handle(self, *args, **options):
        # Generate the feed
        client = Client()
        response = client.get("/feed/rss/xml/")  # Replace with your feed URL

        # Delete the existing feed file if it exists
        file_name = "feed.xml"
        if default_storage.exists(file_name):
            default_storage.delete(file_name)

        # Save the new feed to a file
        file_content = ContentFile(response.content)
        default_storage.save(file_name, file_content)

        self.stdout.write(self.style.SUCCESS("Successfully saved feed to S3"))
