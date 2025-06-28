# main.py
import os
from typing import List
import uuid
from fastapi import FastAPI, Depends, HTTPException, Response
from sqlmodel import Session, select

from backend.web_api.database import get_session
from backend.web_api.models import Articles, ArticleCreate, ArticleRead, Clusters, ClusterCreate, ClusterRead
from typing import List, Dict, Any

from contextlib import asynccontextmanager, closing
# from typing import List, Dict, Any

# from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from psycopg2 import ProgrammingError
import psycopg2
from contextlib import closing
from mangum import Mangum

# # Import our new Bedrock agent function
# from bedrock_agent import generate_sql_from_prompt
# namasthe
# Import our new agent invoker function
from backend.web_api.bedrock_agent_invoke import invoke_bedrock_agent_to_get_sql

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# --- Agent Configuration ---
# Load from environment variables for security and flexibility
AGENT_ID = os.environ.get("BEDROCK_AGENT_ID")
AGENT_ALIAS_ID = os.environ.get("BEDROCK_AGENT_ALIAS_ID", "TSTALIASID") # TSTALIASID is a common default

app = FastAPI(
    title="FastAPI with Bedrock Agents",
    redirect_slashes=True,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup...")
    yield
    print("Application shutdown...")
    # pool.close()


# This event handler runs once when the application starts.
# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()

@app.post("/articles/", response_model=ArticleRead)
def create_article(hero: ArticleCreate, session: Session = Depends(get_session)):
    db_article = Articles.model_validate(hero)
    session.add(db_article)
    session.commit()
    session.refresh(db_article)
    return db_article

@app.get("/articles/", response_model=List[ArticleRead])
def read_articles(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    heroes = session.exec(select(Articles).offset(skip).limit(limit)).all()
    return heroes

@app.get("/articles/{hero_id}", response_model=ArticleRead)
def read_article(hero_id: int, session: Session = Depends(get_session)):
    article = session.get(Articles, hero_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@app.post("/clusters/", response_model=ClusterRead)
def create_cluster(cluster: ClusterCreate, session: Session = Depends(get_session)):
    db_cluster = Clusters.model_validate(cluster)
    session.add(db_cluster)
    session.commit()
    session.refresh(db_cluster)
    return db_cluster

@app.get("/clusters/", response_model=List[ClusterRead])
def read_clusters(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    clusters = session.exec(select(Clusters).offset(skip).limit(limit)).all()
    return clusters

@app.get("/clusters/{cluster_id}", response_model=ClusterRead)
def read_cluster(cluster_id: str, session: Session = Depends(get_session)):
    cluster = session.get(Clusters, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster

@app.get("/groupedClusters/")
def grouped_clusters(session: Session = Depends(get_session)):
    clusters = session.exec(select(Clusters)).all()
    articles = session.exec(select(Articles)).all()
    # Build a mapping from cluster id to articles
    cluster_map = {cluster.id: [] for cluster in clusters}
    for article in articles:
        # Assuming 'linkedarticles' in Clusters is a comma-separated list of article ids
        for cluster in clusters:
            if cluster.linkedarticles:
                linked_ids = [x.strip() for x in cluster.linkedarticles.split(",") if x.strip()]
                if article.articles_id in linked_ids:
                    cluster_map[cluster.id].append(article)
    # Build the response
    result = []
    for cluster in clusters:
        cluster_dict = cluster.dict()
        cluster_dict["articles"] = cluster_map[cluster.id]
        result.append(cluster_dict)
    return result
    
    
# --- Pydantic Models ---
class NaturalLanguageQuery(BaseModel):
    question: str = Field(..., example="How many heroes are there?")
    session_id: str | None = Field(default=None, description="Conversation session ID. A new one is generated if not provided.")

# --- Database Connection ---
# IMPORTANT: Use a read-only user for the database connection.
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://your_user:your_password@your_aurora_endpoint/myappdb")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

@app.post("/queryagent", response_model=List[Dict[str, Any]])
def query_with_bedrock_agent(query: NaturalLanguageQuery, conn=Depends(get_db_connection)):
    """
    Takes a natural language question, sends it to a pre-configured Bedrock Agent,
    executes the returned SQL, and returns the results.
    """
    session_id = query.session_id or str(uuid.uuid4())
    print(f"Invoking agent for question: '{query.question}' with session_id: {session_id}")

    # 1. Invoke the agent to get the SQL query
    try:
        generated_sql = invoke_bedrock_agent_to_get_sql(
            question=query.question,
            agent_id=AGENT_ID,
            agent_alias_id=AGENT_ALIAS_ID,
            session_id=session_id
        )
        print("Generated SQL from agent:", generated_sql)  # Debug print
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to invoke Bedrock Agent: {e}")

    if not generated_sql:
        raise HTTPException(status_code=404, detail="Agent did not return a SQL query.")

    # 2. *** CRITICAL SECURITY CHECK ***
    if not generated_sql.strip().upper().startswith("SELECT"):
        raise HTTPException(
            status_code=400,
            detail="Agent returned a non-SELECT query. Execution aborted."
        )

    # 3. Execute the SQL from the agent
    try:
        with conn.cursor() as cur:
            cur.execute(generated_sql)
            if cur.description is None:
                return []
            
            column_names = [desc[0] for desc in cur.description]
            results = cur.fetchall()
            return [dict(zip(column_names, row)) for row in results]
            
    except ProgrammingError as e:
        raise HTTPException(status_code=400, detail=f"Invalid SQL Query from Agent: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database execution error: {e}")

handler = Mangum(app)

def lambda_handler(event, context):
    """
    AWS Lambda handler for FastAPI app using Mangum adapter.
    """
    return handler(event, context)
