import os
import boto3
import json
from botocore.exceptions import ClientError
from podcast.models import Podcast
from django.core.management.base import BaseCommand
from datetime import datetime, timezone

# Access environment variables
aws_access_key_id = os.getenv("AWS_ACCESS_KEY")
aws_secret_access_key = os.getenv("AWS_SECRET_KEY")
aws_bucket_name = os.getenv("BUCKET_NAME")
audio_upload_folder = "MP3_PODCAST/"
cover_upload_folder = "podcast_covers/"

class Command(BaseCommand):
    help = "Loads a JSON file to populate the Podcast model. Example usage: python3 manage.py seed --json_file old/feed.json --cutoff 2023 5 12"
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    def add_arguments(self, parser):
        parser.add_argument("--json_file", type=str, help="The JSON file to load")
        parser.add_argument(
            "--cutoff",
            type=int,
            nargs=3,
            metavar=("year", "month", "day"),
            help="The cutoff date",
        )

    def file_exists_in_s3(self, bucket_name, s3_key):
        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                self.stdout.write(
                    self.style.ERROR(f"File {s3_key} does not exist in S3")
                )
                return False
            else:
                raise

    def handle(self, *args, **kwargs):
        json_file = kwargs["json_file"]
        year, month, day = kwargs["cutoff"]  # 2023, 5, 12
        with open(json_file) as f:
            data = json.load(f)

        for item in data["items"]:
            published_date_str = item.get("published", "")
            if published_date_str:
                # Parse the published date
                published_date = datetime.strptime(
                    published_date_str, "%a, %d %b %Y %H:%M:%S %Z"
                )
                published_date = published_date.replace(tzinfo=timezone.utc)
            else:
                published_date = None

            cutoff_date = datetime(year, month, day, tzinfo=timezone.utc)

            if published_date and published_date > cutoff_date:
                continue

            audio_url = f"https://podcast-fl.s3.eu-north-1.amazonaws.com/{audio_upload_folder}{os.path.basename(item['guid'])}"
            cover_url = f"https://podcast-fl.s3.eu-north-1.amazonaws.com/{cover_upload_folder}{os.path.basename(item['image'])}"

            # Check if the audio and cover files exist in S3
            if not self.file_exists_in_s3(
                aws_bucket_name,
                f"{audio_upload_folder}{os.path.basename(item['guid'])}",
            ):
                print(f"File {audio_url} does not exist in S3")
                continue

            Podcast.objects.create(
                title=item["title"],
                description=item["description"],
                insert_time=published_date,
                audio_url=audio_url,
                cover_url=cover_url,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Successfully added {item['title']} to podcasts")
            )