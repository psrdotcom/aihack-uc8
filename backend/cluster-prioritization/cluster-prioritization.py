import boto3
import tarfile
import json
import io
from Utils import get_postgresql_connection
import datetime



def lambda_handler(event, context):
    try:
        conn = get_postgresql_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM clusters WHERE TO_DATE(startdate, 'DD/MM/YYYY') >= CURRENT_DATE ORDER BY clusters.referencecount DESC limit 20;"
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(f"ID: {row[0]}, Priority: {row[1]}")
            update_query = """
            WITH ranked AS (
                SELECT id,
                    21 - ROW_NUMBER() OVER (ORDER BY clusters.referencecount DESC) AS priority
                FROM clusters
                WHERE TO_DATE(startdate, 'DD/MM/YYYY') >= CURRENT_DATE
                LIMIT 20
            )
            UPDATE clusters t
            SET priority = r.priority
            FROM ranked r
            WHERE t.id = r.id;
            """
            cursor.execute(update_query)
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