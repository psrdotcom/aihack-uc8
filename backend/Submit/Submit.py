import base64
import json
from requests_toolbelt.multipart import decoder
import uuid
from Utils import get_postgresql_connection
from fastapi import FastAPI
from docx import Document
import csv
import io
import re
import boto3
import traceback

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
            file_stream = io.BytesIO(part.content)
            file_stream.seek(0)
            file_id = str(uuid.uuid4())
            s3_key = f"raw_data/{file_id}"
            # Upload to S3
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=file_stream,
                ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "status": "success",
                "s3_urls": s3_urls
            })
        }
    except Exception as e:
        traceback.print_exc() 
        return {"statusCode": 500, "body": f"❌ Error: {str(e)}"}