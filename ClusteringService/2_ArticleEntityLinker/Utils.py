import json
import psycopg2
from psycopg2 import sql

def get_postgresql_connection():
    '''get the creds from local config'''

    """
    Establish a connection to a PostgreSQL database.

    Parameters:
    host (str): The hostname of the PostgreSQL server.
    database (str): The name of the database to connect to.
    user (str): The username to connect with.
    password (str): The password for the user.

    Returns:
    psycopg2.extensions.connection: A connection object to the PostgreSQL database.
    """
    import os
    try:
        # Always use the path relative to this file's location
        config_path = os.path.join(os.path.dirname(__file__), "pg_config.json")
        with open(config_path) as f:
            config = json.load(f)
        conn = psycopg2.connect(**config)
        return conn
    except FileNotFoundError as fnf:
        print(f"Config file not found: {fnf}")
        return None
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL database:", e)
        return None
    
# Function to read a specific column from the articles table in Aurora RDS PostgreSQL
def read_column_from_db(table_name, column_name):
    conn = get_postgresql_connection()
    cursor = conn.cursor()
    try:
        query = f"SELECT {column_name} FROM {table_name};"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error reading column {column_name}: {e}")
    finally:
        cursor.close()
        conn.close()


def get_entity_linked_phrases(relevantEntities):
    conn = get_postgresql_connection()
    cursor = conn.cursor()
    try:
        query = f"SELECT article_id FROM phrases where relevance_category in [{relevantEntities}];"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error reading articles : {e}")
    finally:
        cursor.close()
        conn.close()

def get_phrases_linked_articles(relevantPhrases):
    conn = get_postgresql_connection()
    cursor = conn.cursor()
    try:
        query = f"SELECT article_id FROM articles where relevance_category in [{relevantPhrases}];"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error reading articles : {e}")
    finally:
        cursor.close()
        conn.close()

def get_entity_linked_articles(relevantEntities):
    conn = get_postgresql_connection()
    cursor = conn.cursor()
    try:
        query = f"SELECT article_id FROM articles where relevance_category in [{relevantEntities}];"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error reading articles : {e}")
    finally:
        cursor.close()
        conn.close()

# Example usage: read the 'title' column from the articles table
if __name__ == "__main__":
    read_column_from_db('bedrock_integration.entity')