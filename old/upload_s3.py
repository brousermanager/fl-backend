import os
import json
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_bucket_name = os.getenv("AWS_BUCKET_NAME")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

# Path to the audio and cover image folders
local_audio_path = "audio"
local_cover_path = "cover_image"
audio_upload_folder = "MP3_PODCAST/"
cover_upload_folder = "podcast_covers/"

# Load the JSON data
with open("feed.json", "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

# Count total items
total_items = len(data["items"])
failed_uploads = []


# Function to check if a file exists in the S3 bucket
def file_exists_in_s3(bucket_name, s3_key):
    try:
        s3_client.head_object(Bucket=bucket_name, Key=s3_key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            raise


# Upload files to S3 and log progress
for index, item in enumerate(data["items"]):
    try:
        # Upload audio file if guid exists
        if "guid" in item and item["guid"]:
            audio_filename = os.path.join(
                local_audio_path, os.path.basename(item["guid"])
            )
            s3_key = f"{audio_upload_folder}{os.path.basename(audio_filename)}"
            if file_exists_in_s3(aws_bucket_name, s3_key):
                print(f"File {s3_key} already exists in S3, overwriting...")
            s3_client.upload_file(audio_filename, aws_bucket_name, s3_key)

        # Upload cover image if image exists
        if "image" in item and item["image"]:
            image_filename = os.path.join(
                local_cover_path, os.path.basename(item["image"])
            )
            s3_key = f"{cover_upload_folder}{os.path.basename(image_filename)}"
            if file_exists_in_s3(aws_bucket_name, s3_key):
                print(f"File {s3_key} already exists in S3, overwriting...")
            s3_client.upload_file(image_filename, aws_bucket_name, s3_key)

        # Log progress
        progress = (index + 1) / total_items * 100
        print(f"Uploaded {index + 1}/{total_items} ({progress:.2f}%)")

    except Exception as e:
        failed_uploads.append({"item": item, "error": str(e)})
        print(
            f"Failed to upload {item.get('guid', 'N/A')} or {item.get('image', 'N/A')}: {e}"
        )

# Save failed uploads to a file
with open("failed_uploads.json", "w", encoding="utf-8") as json_file:
    json.dump(failed_uploads, json_file, ensure_ascii=False, indent=4)

print(f"Upload completed with {len(failed_uploads)} failures.")