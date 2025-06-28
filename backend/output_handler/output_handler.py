import boto3
import tarfile
import json
import io
from Utils import get_postgresql_connection
import datetime

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            print(f"New record: {record}")
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            conn = get_postgresql_connection()
            s3 = boto3.client('s3')
            obj = s3.get_object(Bucket=bucket, Key=key)
            tar_bytes = io.BytesIO(obj['Body'].read())
            print(f"Processing file: {key}")
            # Extract .json inside the tar.gz
            with tarfile.open(fileobj=tar_bytes, mode='r:gz') as tar:
                for member in tar.getmembers():
                    if member.name == "output" and member.isfile():
                        file = tar.extractfile(member)
                        results = json.load(file)
                        print(f"Extracted JSON: {results}")
                        break
            print(f"Results: {results}")
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
                conn.close()
    except Exception as e:
        print(f"Error processing record: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def add_entities_to_article(cursor, article_id, entities):
    entities_text = [entity['Text'] for entity in entities]
    cursor.execute("SELECT * FROM entities WHERE entity in (%s)", (tuple(entities_text),))
    entity_db_array = [row[0] for row in cursor.fetchall()]
    location_mentions = []
    officials_involved = []
    relevance_category = []
    for entity in entities:
        entity_in_db = [db_entity for db_entity in entity_db_array if db_entity['entity'] == entity['Text']]
        if not entity_in_db:
            current_time = datetime.datetime.utcnow()
            cursor.execute("INSERT INTO entities (create_time,entity,type) VALUES (%s, %s, %s) RETURNING id", (current_time, entity['Text'], entity['Type']))
            db_entity = cursor.fetchone()
            if entity['Type'] == 'Location':
                location_mentions.append(db_entity[0])
            elif entity['Type'] == 'Person':
                officials_involved.append(db_entity[0])
            elif entity['Type'] == 'KeyPhrases':
                relevance_category.append(db_entity[0])
            else:
                print(f"Unknown entity type: {entity['Type']}")
        else:
            if entity['Type'] == 'Location':
                location_mentions.append(entity_in_db[0]['Id'])
            elif entity['Type'] == 'Person':
                officials_involved.append(entity_in_db[0]['Id'])
            elif entity['Type'] == 'KeyPhrases':
                relevance_category.append(entity_in_db[0]['Id'])
            else:
                print(f"Unknown entity type: {entity['Type']}")
    if location_mentions:
        location_mentions = ','.join(map(str, location_mentions))
        cursor.execute("""update articles set location_mentions = %s where articles_id = %s""", (location_mentions, article_id))

    if officials_involved:
        officials_involved = ','.join(map(str, officials_involved))
        cursor.execute("""update articles set officials_involved = %s where articles_id = %s""", (officials_involved, article_id))

    if relevance_category:
        relevance_category = ','.join(map(str, relevance_category))
        cursor.execute("""update articles set relevance_category = %s where articles_id = %s""", (relevance_category, article_id))