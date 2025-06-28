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

@app.post("/upload/")
async def lambda_handler(file: UploadFile = File(...)):
    if not file.filename.endswith(".docx"):
        return JSONResponse(status_code=400, content={"error": "Only .docx files are supported"})

    try:
        s3_urls = []
        articles = extract_articles(file.file)
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
        for article in articles:
            output_csv = io.StringIO()
            writer = csv.DictWriter(output_csv, fieldnames=["Title", "Source", "Date", "Content"])
            writer.writeheader()
            writer.writerow(article)
            # Generate unique filename
            csv_filename = f"/input/articles-{uuid.uuid4()}.csv"
            articles_id = str(uuid.uuid4())  # Generate a unique ID for each article
            cursor.execute("""
                    INSERT INTO articles (articles_id, title, body, source, published_date)
                    VALUES (%s, %s, %s, %s, %s)""", (articles_id, article[0], article[1], article[2], article[3]))
            # Upload to S3
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=csv_filename,
                Body=output_csv.getvalue(),
                ContentType='text/csv'
            )
            s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{csv_filename}"
            s3_urls.append(s3_url)
        return {"status": "success", "count": len(articles), "data": articles, "s3_urls": s3_urls}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    

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