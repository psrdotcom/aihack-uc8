import csv
import io
import pandas as pd
import boto3
import time
import uuid
from Utils import get_postgresql_connection
from Utils import read_column_from_db

# Read CSV into DataFrame
conn = get_postgresql_connection()
cursor = conn.cursor()

#STEP - 1 | GET ALL CURRENT ENTITIES
entities = read_column_from_db('entities', 'entity')

for entity in entities:
    entity = entity[0]  # Extract the string from the tuple
    print(f"Processing entity: {entity}")

    #STEP - 2 | GET SEMANTIC KEYWORDS FOR EACH ENTITY    
    # Here you would typically call a function to get semantic keywords for the entity
    # For example:
    # keywords = get_semantic_keywords(entity)
    

    #STEP - 3 | SEARCH FOR LINKED ARTICLES
    # Then search for linked articles using those keywords
    # For example:
    # linked_articles = search_linked_articles(keywords)

    #STEP - 4 | REVIEW LINKS

    #STEP - 5 | CREATE\UPDATE CLUSTERS

# FOLLOW UP STEPS
#1. PRIORITIZE CLUSTERS
#2. LINK TO OLD CLUSTERS
#3. CLEAN UP REMAINING OLD CLUSTERS
#4. CHAIN UP LAMBDAS FOR ABOVE ACTIVITIES

cursor.close()
conn.close()