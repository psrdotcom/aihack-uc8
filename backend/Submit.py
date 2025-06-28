import csv
import io
import pandas as pd
import boto3
import time
import uuid
from Utils import get_postgresql_connection

comprehend = boto3.client('comprehend')

role_arn = 'arn:aws:iam::269854564686:role/hackathon-comprehend-role'
bucket_name = 'awstraindata'
s3 = boto3.client('s3')
# Download the file object
input_csv_object = s3.get_object(Bucket=bucket_name, Key='input_small.csv')

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
                        entities TEXT,
                        sentiment TEXT
                    )""")
cursor.execute("""
                drop table if exists comprehend_jobs
""")
cursor.execute("""
                CREATE TABLE IF NOT EXISTS comprehend_jobs (
                    article_id TEXT,
                    input_s3_uri TEXT,
                    entities_path TEXT,
                    sentiment_path TEXT,
                    key_phrases_path TEXT
                )
                """)
input_csv = pd.read_csv(io.BytesIO(input_csv_object['Body'].read()))
for index, row in input_csv.iterrows():
    print(f"Processing row {index}: {row}")
    articles_id = str(uuid.uuid4())  # Generate a unique ID for each article
    cursor.execute("""
            INSERT INTO articles (articles_id, title, body, source, published_date)
            VALUES (%s, %s, %s, %s, %s)""", (articles_id, row[1], row[2], row[3], row[4]))
    # Convert to CSV in-memory
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    # writer.writerow(row.headers)  # Write header
    writer.writerow(row)
    s3_path = 'input/' + articles_id + '.csv'
    s3_uri = 's3://' + bucket_name + '/' + s3_path
    s3.put_object(
        Bucket=bucket_name,
        Key=s3_path,  # adjust as needed
        Body=csv_buffer.getvalue(),
        ContentType='text/csv'
    )
    entities_job = comprehend.start_entities_detection_job(
        InputDataConfig={'S3Uri': s3_uri, 'InputFormat': 'ONE_DOC_PER_LINE'},
        OutputDataConfig={'S3Uri': 's3://awstraindata/output/entities/'},
        DataAccessRoleArn=role_arn,
        LanguageCode='en',
        JobName='MyEntityDetectionJob_'+ articles_id + '_' + str(int(time.time()))
    )
    result = comprehend.describe_entities_detection_job(JobId=entities_job['JobId'])
    entities_output = result['EntitiesDetectionJobProperties']['OutputDataConfig']['S3Uri']

    # SENTIMENT detection job
    sentiment_job = comprehend.start_sentiment_detection_job(
        InputDataConfig={'S3Uri': s3_uri, 'InputFormat': 'ONE_DOC_PER_LINE'},
        OutputDataConfig={'S3Uri': 's3://awstraindata/output/sentiment/'},
        DataAccessRoleArn=role_arn,
        LanguageCode='en',
        JobName='MySentimentDetectionJob_' + articles_id + '_' + str(int(time.time()))
    )
    res = comprehend.describe_sentiment_detection_job(JobId=sentiment_job['JobId'])
    sentiment_output = res['SentimentDetectionJobProperties']['OutputDataConfig']['S3Uri']

    # KEY PHRASES detection job
    phrases_job = comprehend.start_key_phrases_detection_job(
        InputDataConfig={'S3Uri': s3_uri, 'InputFormat': 'ONE_DOC_PER_LINE'},
        OutputDataConfig={'S3Uri': 's3://awstraindata/output/keyphrases/'},
        DataAccessRoleArn=role_arn,
        LanguageCode='en',
        JobName='MyKeyPhrasesDetectionJob_' + articles_id + '_' + str(int(time.time()))
    )
    res = comprehend.describe_key_phrases_detection_job(JobId=phrases_job['JobId'])
    key_phrases_output = res['KeyPhrasesDetectionJobProperties']['OutputDataConfig']['S3Uri']
    print("Entities Job Response:", entities_output)
    print("Sentiment Job Response:", sentiment_output)
    print("Key Phrases Job Response:", key_phrases_output)
    print("Inserting into comprehend_jobs table")
    cursor.execute("""
        INSERT INTO comprehend_jobs (article_id, input_s3_uri, entities_path, sentiment_path, key_phrases_path)
        VALUES (%s, %s, %s, %s, %s)""", (articles_id, s3_uri, entities_output.replace('s3://awstraindata/', ''), sentiment_output.replace('s3://awstraindata/', ''), key_phrases_output.replace('s3://awstraindata/', '')))
    conn.commit()
cursor.close()
conn.close()