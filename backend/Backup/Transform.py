from turtle import pd
import boto3
import tarfile
import json
import psycopg2
import io

from EntityRecog.Utils import get_postgresql_connection
def lambda_handler(event, context):
    for record in event['Records']:
        print(f"New record: {record}")
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        conn = get_postgresql_connection()
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=bucket, Key=key)
        tar_bytes = io.BytesIO(obj['Body'].read())

        # Extract .json inside the tar.gz
        with tarfile.open(fileobj=tar_bytes, mode='r:gz') as tar:
            for member in tar.getmembers():
                if member.name == "output" and member.isfile():
                    file = tar.extractfile(member)
                    results = json.load(file)
                    print(f"Extracted JSON: {results}")
                    break

        if not results:
            folderSplit = key.split('/')
            type = folderSplit[0]
            cursor = conn.cursor()
            query = "SELECT * FROM comprehend_jobs WHERE entities_path = %s or sentiment_path = %s or key_phrases_path = %s"
            cursor.execute(query, (key, key, key))
            row = cursor.fetchone()
            if row:
                # Download the file object
                response = s3.get_object(Bucket=bucket, Key=row['input_s3_uri'])

                # Read CSV into DataFrame
                input_csv = pd.read_csv(io.BytesIO(response['Body'].read()))
                for row in results:
                    if type == 'entities':
                        location_mentions = ', '.join([entity['Text'] for entity in row['Entities'] if entity['Type'] == 'LOCATION'])
                        officials_involved = ', '.join([entity['Text'] for entity in row['Entities'] if entity['Type'] == 'PERSON'])
                        relevance_category = ', '.join([entity['Text'] for entity in row['Entities'] if entity['Type'] == 'TITLE'])
                        if not location_mentions:
                            cursor.execute("""update articles set location_mentions = %s where articles_id = %s""", (location_mentions, input_article['articles_id']))
                        if not officials_involved:
                            cursor.execute("""update articles set  officials_involved = %s where articles_id = %s""", (officials_involved, input_article['articles_id']))
                        if not relevance_category:
                            cursor.execute("""update articles set  relevance_category = %s where articles_id = %s""", (relevance_category, input_article['articles_id']))
                    elif type == 'sentiment':
                        sentiment = row.get('Sentiment', 'NEUTRAL')
                        if not sentiment:
                            cursor.execute("""update articles set sentiment = %s where articles_id = %s""", (sentiment, input_article['articles_id']))
                    elif type == 'keyphrases':
                        key_phrases = ', '.join(row.get('KeyPhrases', []))
                        if not key_phrases:
                            cursor.execute("""update articles set key_phrases = %s where articles_id = %s""", (key_phrases, input_article['articles_id']))
                line_number = row['Line']
                input_article = input_csv[line_number]
               
            cursor.close()
            conn.close()