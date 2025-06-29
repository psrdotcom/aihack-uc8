
import json
from Utils import get_postgresql_connection


def lambda_handler(event, context):
    conn = get_postgresql_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM articles order by article_id asc"
    cursor.execute(query)
    articles = cursor.fetchall()
    return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "status": "success",
                "data": articles
            })
    }