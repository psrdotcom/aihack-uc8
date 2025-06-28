import base64
from requests_toolbelt.multipart import decoder
import uuid
from Utils import get_postgresql_connection
from fastapi import FastAPI
from docx import Document
import csv
import io
import re
import boto3

app = FastAPI()

s3 = boto3.client('s3')
BUCKET_NAME = 'awstraindata'

def lambda_handler(event, context):
    try:
        # Decode base64-encoded body (API Gateway encodes binary automatically)
        print(f"Received event")
        if event.get("isBase64Encoded", False):
            body = base64.b64decode(event['body'])
        else:
            body = event['body'].encode("utf-8")
        print(f"Decoded body length: {len(body)} bytes")
        # Get content-type header
        content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type')
        if not content_type:
            return {"statusCode": 400, "body": "Missing Content-Type header"}

        # Parse multipart form
        multipart_data = decoder.MultipartDecoder(body, content_type)
        print(f"Multipart data parts: {len(multipart_data.parts)}")
        s3_urls = []
        conn = get_postgresql_connection()
        cursor = conn.cursor()
        for part in multipart_data.parts:
            print(f"Processing part: {part.headers.get(b'Content-Disposition')}")
            # Extract file name from content-disposition
            articles = extract_articles(io.BytesIO(part.content))
            print(f"Extracted {len(articles)} articles from part")
            for article in articles:
                print(f"Processing article: {article[0]}")
                output_csv = io.StringIO()
                writer = csv.DictWriter(output_csv, fieldnames=["Title", "Source", "Date", "Content"])
                writer.writeheader()
                writer.writerow(article)
                article_id = str(uuid.uuid4())
                # Generate unique filename
                csv_filename = f"input/articles-{article_id}.csv"
                cursor.execute("""
                        INSERT INTO articles (article_id, title, body, source, published_date)
                        VALUES (%s, %s, %s, %s, %s)""", (article_id, article[0], article[1], article[2], article[3]))
                # Upload to S3
                print(f"Uploading CSV to S3: {csv_filename}")
                s3.put_object(
                    Bucket=BUCKET_NAME,
                    Key=csv_filename,
                    Body=output_csv.getvalue(),
                    ContentType='text/csv'
                )
                conn.commit() 
                print(f"Uploaded CSV to S3: {csv_filename}")
                s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{csv_filename}"
                s3_urls.append(s3_url)
        cursor.close()
        conn.close()
        return {"statusCode": 200, "status": "success", "count": len(articles), "data": articles, "s3_urls": s3_urls}
    except Exception as e:
        return {"statusCode": 500, "body": f"❌ Error: {str(e)}"}

def extract_articles(file_stream):
    doc = Document(file_stream)
    text = "\n".join(p.text for p in doc.paragraphs)
    pattern = re.compile(
        r'Title:\s*(.*?)\s*Source:\s*(.*?)\s*Date:\s*(.*?)\s*(?=(?:\d{1,2}\)|Title:)|\Z)',
        re.DOTALL
    )
    matches = pattern.findall(text)
    articles = []
    for match in matches:
        title = match[0].strip()
        source = match[1].strip()
        date_parts = match[2].strip().split("\n", 1)
        date = date_parts[0].strip()
        content = date_parts[1].strip() if len(date_parts) > 1 else ""
        articles.append([title, source, date, content])
    return articles