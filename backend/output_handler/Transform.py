import boto3
import tarfile
import json
import io
from Utils import get_postgresql_connection

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
                        entity_array = [entity['Text'] for entity in result['Entities']]
                        location_array = [entity['Text'] for entity in result['Entities'] if entity['Type'] == 'LOCATION']
                        relevance_array = [entity['Text'] for entity in result['Entities'] if entity['Type'] != 'LOCATION' and entity['Type'] != 'PERSON']
                        if not entity_array:
                            ## get the entities from the entities table
                            cursor.execute("SELECT * FROM entities WHERE entity in (%s)",(tuple(entity_array),))
                            entity_db_array = [row[0] for row in cursor.fetchall()]
                            entity_ids = []
                            for entity in entity_array:
                                entity_in_db = [db_entity for db_entity in entity_db_array if db_entity['entity'] == entity]
                                if not entity_in_db:
                                    cursor.execute("INSERT INTO entities (entity) VALUES (%s) RETURNING id", (entity,))
                                    db_entity = cursor.fetchone()
                                    db_entity = {'Id': db_entity[0], 'Text': entity}
                                else:
                                    cursor.execute("SELECT * FROM entities WHERE entity = %s", (entity,))
                                    db_entity = cursor.fetchone()
                                    db_entity = {'Id': db_entity[0], 'Text': entity}
                            for db_entity in entity_db_array:

                                entity_array.append(db_entity)
                        entity_ids_array = [db_entity['Id'] for entity_db in entity_db_array if entity['Text'] in entity_array]
                        location_mentions = ', '.join([entity['Text'] for entity in result['Entities'] if entity['Type'] == 'LOCATION'])
                        officials_involved = ', '.join([entity['Text'] for entity in result['Entities'] if entity['Type'] == 'PERSON'])
                        relevance_category = ', '.join([entity['Text'] for entity in result['Entities'] if entity['Type'] != 'LOCATION' and entity['Type'] != 'PERSON'])
                        if not location_mentions:
                            cursor.execute("""update articles set location_mentions = %s where articles_id = %s""", (location_mentions, article_id))
                        if not officials_involved:
                            cursor.execute("""update articles set  officials_involved = %s where articles_id = %s""", (officials_involved, article_id))
                        if not relevance_category:
                            cursor.execute("""update articles set  relevance_category = %s where articles_id = %s""", (relevance_category, article_id))
                    elif type == 'sentiment':
                        sentiment = result.get('Sentiment', 'NEUTRAL')
                        if not sentiment:
                            cursor.execute("""update articles set sentiment = %s where articles_id = %s""", (sentiment, article_id))
                    elif type == 'keyphrases':
                        key_phrases = ', '.join(result.get('KeyPhrases', []))
                        if not key_phrases:
                            cursor.execute("""update articles set key_phrases = %s where articles_id = %s""", (key_phrases, article_id))
            cursor.close()
            ## delete the s3 object
            s3.delete_object(Bucket=bucket, Key=result['input_s3_uri'])
            # s3.delete_object(Bucket=bucket, Key=key)
            conn.close()