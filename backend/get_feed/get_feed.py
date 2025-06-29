
import json
from Utils import get_postgresql_connection


def lambda_handler(event, context):
    conn = get_postgresql_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM articles order by article_id asc"
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    result = [dict(zip(columns, row)) for row in rows]
    return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(result)
    }