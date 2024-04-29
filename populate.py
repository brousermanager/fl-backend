import os
import boto3
import sqlite3
import json

bucket_name = 'podcast-fl'
prefix = 'MP3_PODCAST/'
suffix = '.mp3'
database_path = './podcast_db.sqlite'


def get_s3_objects(bucket_name, prefix):
  s3 = boto3.client('s3',
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'))
  response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

  if 'Contents' in response:
    return [obj['Key'] for obj in response['Contents']]
  else:
    return []


def fetch_podcasts_from_database(database_path):
  conn = sqlite3.connect(database_path)
  cursor = conn.cursor()

  podcasts = []
  for row in cursor.execute('SELECT title, mp3_file, shortdesc, mtime FROM episodes'):
    title, mp3_file, shortdesc, mtime = row
    podcast = {'title': title, 'mp3_file': mp3_file, 'description': shortdesc, 'insert_time': mtime}
    podcasts.append(podcast)

  conn.close()
  return podcasts


def process_data(bucket_name, prefix, database_path):
  s3_objects = get_s3_objects(bucket_name, prefix)
  podcasts_data = fetch_podcasts_from_database(database_path)
  result_data = []
  podcast_data_not_done = []
  s3_objects_done = []
  for podcast_data in podcasts_data:
    flag = True
    for s3_object in s3_objects:
      s3_object = s3_object.replace(prefix, '')
      #check data
      # if podcast_data['insert_time'].split(' ')[0] == s3_object.split('_')[0]:
      #   # check 1 word in description
      #   if s3_object.split('_')[1] in podcast_data['description'].split():
      if podcast_data['mp3_file'] == s3_object:
        podcast_data['file_url'] = f"https://{bucket_name}.s3.amazonaws.com/{s3_object}"
        result_data.append(podcast_data)
        flag = False
        s3_objects_done.append(s3_object)
        break
    if flag:
      podcast_data_not_done.append(podcast_data['title'])
  s3_objects_not_done = []
  for s3_object in s3_objects:
    if not s3_object.replace(prefix, '') in s3_objects_done:
      s3_objects_not_done.append(s3_object)
  with open('result.json', 'w') as f:
    json.dump(result_data, f, indent=2)
  with open('mismatch.json', 'w') as f:
    json.dump(
        {
            'podcast_data_not_done': podcast_data_not_done,
            's3_objects_not_done': s3_objects_not_done
        },
        f,
        indent=2)
  print(f'match: {len(result_data)}')

process_data(bucket_name, prefix, database_path)
