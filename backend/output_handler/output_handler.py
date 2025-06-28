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
            print(f"Processing file from bucket: {bucket}, key: {key}")
            conn = get_postgresql_connection()
            s3 = boto3.client('s3')
            print(f"Connecting to S3 bucket: {bucket}")
            obj = s3.get_object(Bucket=bucket, Key=key)
            print(f"Downloaded object from S3: {key}")
            tar_bytes = io.BytesIO(obj['Body'].read())
            print(f"Processing file: {key}")
            # Extract .json inside the tar.gz
            with tarfile.open(fileobj=tar_bytes, mode='r:gz') as tar:
                print(f"Extracting files from tar: {key}")
                for member in tar.getmembers():
                    print(f"Found member: {member.name}")
                    if member.name == "output" and member.isfile():
                        print(f"Extracting JSON file: {member.name}")
                        file = tar.extractfile(member)
                        if not file:
                            print(f"File {member.name} not found in tar.")
                            continue
                        result = json.load(file)
                        print(f"Extracted JSON: {result}")
                        break
            print(f"Results: {result}")
            if result:
                print(f"Results found in the file: {key}")
                folderSplit = key.split('/')
                type = folderSplit[1]
                cursor = conn.cursor()
                query = "SELECT * FROM comprehend_jobs WHERE entities_path = %s or sentiment_path = %s or key_phrases_path = %s"
                cursor.execute(query, (key, key, key))
                row = cursor.fetchone()
                print(f"Row found: {row}")
                print(f"Type of analysis: {type}")
                if row:
                    article_id = row[0]
                    print(f"Article ID: {article_id}")
                    if type == 'entities':
                        entity_array = result['Entities']
                        if entity_array:
                            ## get the entities from the entities table
                            add_entities_to_article(cursor, article_id, entity_array)
                    elif type == 'keyphrases':
                        keyPhrases_array = result['KeyPhrases']
                        if keyPhrases_array:
                            for keyPhrase in keyPhrases_array:
                                keyPhrase['Type'] = 'KeyPhrase'
                            add_entities_to_article(cursor, article_id, keyPhrases_array)
                    elif type == 'sentiment':
                        sentiment = result.get('Sentiment', 'NEUTRAL')
                        if sentiment:
                            cursor.execute("""update articles set sentiment = %s where article_id = %s""", (sentiment, article_id))
                conn.commit()
                cursor.close()
                ## delete the s3 object
                # s3.delete_object(Bucket=bucket, Key=result['input_s3_uri'])
                conn.close()
    except Exception as e:
        print(f"Error processing record: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def add_entities_to_article(cursor, article_id, entities):
    entities_text = [entity['Text'] for entity in entities]
    print(f"Entities to be added: {entities_text}")
    cursor.execute("SELECT * FROM entities WHERE entity in %s", (tuple(entities_text),))
    entity_db_array = cursor.fetchall()
    print(f"Entities in DB: {entity_db_array}")
    location_mentions = []
    officials_involved = []
    relevance_category = []
    print(f"article_id: {article_id}")
    
    print(f"Relevance category: {relevance_category}")
    for entity in entities:
        print(f"Processing entity: {entity}")
        entity_in_db = [db_entity for db_entity in entity_db_array if db_entity[3] == entity['Text']]
        print(f"Entity in DB: {entity_in_db}")
        if not entity_in_db:
            current_time = datetime.datetime.utcnow()
            cursor.execute("INSERT INTO entities (create_time,entity,type) VALUES (%s, %s, %s) RETURNING id", (current_time, entity['Text'], entity['Type']))
            db_entity = cursor.fetchone()
            print(f"Inserted new entity: {db_entity}")
            if entity['Type'] == 'LOCATION':
                location_mentions.append(db_entity[0])
            elif entity['Type'] == 'PERSON':
                officials_involved.append(db_entity[0])
            else:
                relevance_category.append(db_entity[0])
        else:
            print(f"Entity already exists in DB: {entity_in_db}")
            if entity['Type'] == 'LOCATION':
                location_mentions.append(entity_in_db[0][0])
            elif entity['Type'] == 'PERSON':
                officials_involved.append(entity_in_db[0][0])
            else:
                relevance_category.append(entity_in_db[0][0])
    if location_mentions:
        location_mentions = ','.join(map(str, location_mentions))
        cursor.execute("""update articles set location_mentions = %s where article_id = %s""", (location_mentions, article_id))

    if officials_involved:
        officials_involved = ','.join(map(str, officials_involved))
        cursor.execute("""update articles set officials_involved = %s where article_id = %s""", (officials_involved, article_id))

    if relevance_category:
        cursor.execute("SELECT relevance_category FROM articles WHERE article_id = %s", (article_id,))
        existing = cursor.fetchone()
        relevance_category = ','.join(map(str, relevance_category))
        if existing[0] is not None:
            print(f"Existing relevance category: {existing[0]}")
            relevance_category = relevance_category + ',' + existing[0]
        cursor.execute("""update articles set relevance_category = %s where article_id = %s""", (relevance_category, article_id))


# events = [
#     {
#         "s3": {
#             "bucket": {
#                 "name": "awstraindata"
#             },
#             "object": {
#                 "key": "output/entities/269854564686-NER-7b5218ec8e556761890504a59e10da02/output/output.tar.gz"
#             }
#         }
#     }
# ]
# obj= {
#     "Records": events
# }
# lambda_handler(obj, None)