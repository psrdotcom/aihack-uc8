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
    try:
        with open("pg_config.json") as f:
            config = json.load(f)
        conn = psycopg2.connect(**config)
        return conn
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL database:", e)
        return None