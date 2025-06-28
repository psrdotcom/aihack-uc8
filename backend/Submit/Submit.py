import base64
from json import decoder
import uuid
from Utils import get_postgresql_connection
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from docx import Document
import csv
import io
import re
import boto3

app = FastAPI()

s3 = boto3.client('s3')
BUCKET_NAME = 'awstraindata'

def lambda_handler(event):
    try:
        # Decode base64-encoded body (API Gateway encodes binary automatically)
        body = base64.b64decode(event['body'])

        # Get content-type header
        content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type')
        if not content_type:
            return {"statusCode": 400, "body": "Missing Content-Type header"}

        # Parse multipart form
        multipart_data = decoder.MultipartDecoder(body, content_type)
        s3_urls = []
        conn = get_postgresql_connection()
        cursor = conn.cursor()
        for part in multipart_data.parts:
            # Extract file name from content-disposition
            cd = part.headers.get(b'Content-Disposition', b'').decode()
            if 'filename=' not in cd:
                continue
            filename = cd.split('filename="')[1].split('"')[0]
            articles = extract_articles(io.BytesIO(part.content))
            for article in articles:
                output_csv = io.StringIO()
                writer = csv.DictWriter(output_csv, fieldnames=["Title", "Source", "Date", "Content"])
                writer.writeheader()
                writer.writerow(article)
                # Generate unique filename
                csv_filename = f"/input/articles-{uuid.uuid4()}.csv"
                article_id = str(uuid.uuid4())  # Generate a unique ID for each article
                cursor.execute("""
                        INSERT INTO articles (article_id, title, body, source, published_date)
                        VALUES (%s, %s, %s, %s, %s)""", (article_id, article[0], article[1], article[2], article[3]))
                # Upload to S3
                s3.put_object(
                    Bucket=BUCKET_NAME,
                    Key=csv_filename,
                    Body=output_csv.getvalue(),
                    ContentType='text/csv'
                )
                s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{csv_filename}"
                s3_urls.append(s3_url)
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