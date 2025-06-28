import boto3
import tarfile
import json
import io
from Utils import get_postgresql_connection
import datetime

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
                article_id = row['article_id']
                for result in results:
                    if type == 'entities':
                        entity_array = result['Entities']
                        if not entity_array:
                            ## get the entities from the entities table
                            add_entities_to_article(cursor, article_id, entity_array)
                    elif type == 'keyphrases':
                        keyPhrases_array = result['KeyPhrases']
                        if not keyPhrases_array:
                            for keyPhrase in keyPhrases_array:
                                keyPhrase['Type'] = 'KeyPhrase'
                            add_entities_to_article(cursor, article_id, keyPhrases_array)
                    elif type == 'sentiment':
                        sentiment = result.get('Sentiment', 'NEUTRAL')
                        if not sentiment:
                            cursor.execute("""update articles set sentiment = %s where articles_id = %s""", (sentiment, article_id))
            cursor.close()
            ## delete the s3 object
            s3.delete_object(Bucket=bucket, Key=result['input_s3_uri'])
            # s3.delete_object(Bucket=bucket, Key=key)
            conn.close()

def add_entities_to_article(cursor, article_id, entities):
    entities_text = [entity['Text'] for entity in entities]
    cursor.execute("SELECT * FROM entities WHERE entity in (%s)", (tuple(entities_text),))
    entity_db_array = [row[0] for row in cursor.fetchall()]
    entity_ids = cursor.execute("SELECT entities FROM articles WHERE articles_id = %s", (article_id,)).cursor.fetchall()
    for entity in entities:
        entity_in_db = [db_entity for db_entity in entity_db_array if db_entity['entity'] == entity['Text']]
        if not entity_in_db:
            current_time = datetime.datetime.utcnow()
            cursor.execute("INSERT INTO entities (create_time,entity,type) VALUES (%s, %s, %s) RETURNING id", (current_time, entity['Text'], entity['Type']))
            db_entity = cursor.fetchone()
            entity_ids.append(db_entity[0])
        else:
            entity_ids.append(entity_in_db[0]['Id'])
    cursor.execute("""update articles set entities = %s where articles_id = %s""", (entity_ids, article_id))