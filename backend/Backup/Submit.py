import io
import pandas as pd
import boto3
import time
import uuid
from Utils import get_postgresql_connection

comprehend = boto3.client('comprehend')

input_s3_uri = 's3://awstraindata/input.csv'
role_arn = 'arn:aws:iam::269854564686:role/hackathon-comprehend-role'

s3 = boto3.client('s3')
# Download the file object
input_csv_object = s3.get_object(Bucket='awstraindata', Key='input.csv')

# Read CSV into DataFrame
conn = get_postgresql_connection()
cursor = conn.cursor()
cursor.execute("drop table if exists articles")
cursor.execute("""CREATE TABLE IF NOT EXISTS articles (
                        articles_id TEXT,
                        title TEXT,
                        body TEXT,
                        source TEXT,
                        published_date TEXT,
                        location_mentions TEXT,
                        officials_involved TEXT,
                        relevance_category TEXT,
                        sentiment TEXT
                    )""")
input_csv = pd.read_csv(io.BytesIO(input_csv_object['Body'].read()))
for index, row in input_csv.iterrows():
    print(f"Processing row {index}: {row}")
    cursor.execute("""
            INSERT INTO articles (articles_id, title, body, source, published_date)
            VALUES (%s, %s, %s, %s, %s)""", (row[0], row[1], row[2], row[3], row[4]))
conn.commit()
cursor.close()
entities_job = comprehend.start_entities_detection_job(
    InputDataConfig={'S3Uri': input_s3_uri, 'InputFormat': 'ONE_DOC_PER_LINE'},
    OutputDataConfig={'S3Uri': 's3://awstraindata/output/entities/'},
    DataAccessRoleArn=role_arn,
    LanguageCode='en',
    JobName='MyEntityDetectionJob_' + str(int(time.time())), 
)
result = comprehend.describe_entities_detection_job(JobId=entities_job['JobId'])
entities_output = result['EntitiesDetectionJobProperties']['OutputDataConfig']['S3Uri']

# SENTIMENT detection job
sentiment_job = comprehend.start_sentiment_detection_job(
    InputDataConfig={'S3Uri': input_s3_uri, 'InputFormat': 'ONE_DOC_PER_LINE'},
    OutputDataConfig={'S3Uri': 's3://awstraindata/output/sentiment/'},
    DataAccessRoleArn=role_arn,
    LanguageCode='en',
    JobName='MySentimentDetectionJob_' + str(int(time.time())),
)
res = comprehend.describe_sentiment_detection_job(JobId=sentiment_job['JobId'])
sentiment_output = res['SentimentDetectionJobProperties']['OutputDataConfig']['S3Uri']

# KEY PHRASES detection job
phrases_job = comprehend.start_key_phrases_detection_job(
    InputDataConfig={'S3Uri': input_s3_uri, 'InputFormat': 'ONE_DOC_PER_LINE'},
    OutputDataConfig={'S3Uri': 's3://awstraindata/output/keyphrases/'},
    DataAccessRoleArn=role_arn,
    LanguageCode='en',
    JobName='MyKeyPhrasesDetectionJob_' + str(int(time.time())),
)
res = comprehend.describe_key_phrases_detection_job(JobId=phrases_job['JobId'])
key_phrases_output = res['KeyPhrasesDetectionJobProperties']['OutputDataConfig']['S3Uri']
print("Entities Job Response:", entities_job)
print("Sentiment Job Response:", sentiment_job)
print("Key Phrases Job Response:", phrases_job)
conn = get_postgresql_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comprehend_jobs (
        batch_id TEXT,
        input_s3_uri TEXT,
        entities_job JSONB,
        sentiment_job JSONB,
        key_phrases_job JSONB
    )
    """)
    cursor.execute("""
        INSERT INTO comprehend_jobs (batch_id, input_s3_uri, entities_path, sentiment_path, key_phrases_path)
        VALUES (%s, %s, %s, %s, %s)""", (str(uuid.uuid4()), input_s3_uri, entities_output.replace('s3://awstraindata/', ''), sentiment_output.replace('s3://awstraindata/', ''), key_phrases_output.replace('s3://awstraindata/', '')))
    conn.commit()
    cursor.close()
    conn.close()

