from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, List, Optional
from datetime import datetime

app = FastAPI()

# Enable CORS for all origins (for dev; restrict in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Mangum handler for AWS Lambda compatibility
try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    handler = None  # Local dev fallback

# --- Models ---
class NewsArticle(BaseModel):
    id: Optional[int] = None
    title: str
    body: str
    source: str
    publishedDate: str  # DD/MM/YYYY
    extractedLocations: Optional[List[str]] = None
    districtMapping: Optional[str] = None
    tags: Optional[List[str]] = None

class NewsIngestRequest(BaseModel):
    articles: List[NewsArticle]

class ClusteredNews(BaseModel):
    cluster_id: int
    summary: str
    articles: List[NewsArticle]

class TaskRequest(BaseModel):
    task: str
    params: dict[str, Any] = {}

class TaskResult(BaseModel):
    outcome: str
    details: dict[str, Any] = {}

news_db: List[NewsArticle] = []

@app.post("/news/ingest")
def ingest_news(req: NewsIngestRequest):
    start_id = len(news_db)
    for i, article in enumerate(req.articles):
        article.id = start_id + i + 1
        news_db.append(article)
    return {"status": "success", "ingested": len(req.articles)}

@app.get("/news/clustered", response_model=List[ClusteredNews])
def get_clustered_news():
    clusters = {}
    for article in news_db:
        key = article.districtMapping or 'Unknown'
        clusters.setdefault(key, []).append(article)
    result = []
    for idx, (district, articles) in enumerate(clusters.items(), 1):
        summary = articles[0].body[:60] + ("..." if len(articles[0].body) > 60 else "")
        result.append(ClusteredNews(cluster_id=idx, summary=summary, articles=articles))
    return result

# --- Outcome Agents ---
@app.post("/agent/relevance", response_model=TaskResult)
def agent_relevance(request: TaskRequest):
    """Relevance Filtering: filter articles by keywords/themes in params['criteria'] (list of str)"""
    criteria = request.params.get('criteria', [])
    relevant = [a for a in news_db if any(
        (a.tags and any(c in a.tags for c in criteria)) or
        any(c.lower() in a.title.lower() or c.lower() in a.body.lower() for c in criteria)
    )]
    return TaskResult(outcome="success", details={"relevant_articles": [a.dict() for a in relevant]})

@app.post("/agent/cluster", response_model=TaskResult)
def agent_cluster(request: TaskRequest):
    """Clustering & Linking: group articles by districtMapping and date (stub logic)"""
    clusters = {}
    for article in news_db:
        key = (article.districtMapping or 'Unknown', article.publishedDate)
        clusters.setdefault(key, []).append(article)
    result = [
        {
            "cluster_id": idx,
            "district": k[0],
            "date": k[1],
            "articles": [a.dict() for a in v]
        }
        for idx, (k, v) in enumerate(clusters.items(), 1)
    ]
    return TaskResult(outcome="success", details={"clusters": result})

@app.post("/agent/comparative", response_model=TaskResult)
def agent_comparative(request: TaskRequest):
    """Comparative Insights: compare how different sources report the same event (stub: group by title)"""
    groups = {}
    for article in news_db:
        key = article.title.strip().lower()
        groups.setdefault(key, []).append(article)
    comparisons = []
    for title, articles in groups.items():
        if len(articles) > 1:
            comparisons.append({
                "title": title,
                "sources": [a.source for a in articles],
                "bodies": [a.body for a in articles]
            })
    return TaskResult(outcome="success", details={"comparisons": comparisons})

@app.post("/agent/digest", response_model=TaskResult)
def agent_digest(request: TaskRequest):
    """Digest Rendering: output a simple HTML digest (stub)"""
    html = "<h2>News Digest</h2>"
    for article in news_db:
        html += f"<div><b>{article.title}</b> ({article.publishedDate}, {article.source})<br>"
        html += f"{article.body[:120]}{'...' if len(article.body) > 120 else ''}</div><hr>"
    return TaskResult(outcome="success", details={"digest_html": html})

@app.post("/agent/execute", response_model=TaskResult)
def execute_agent(request: TaskRequest):
    if request.task == "echo":
        return TaskResult(outcome="success", details={"echo": request.params})
    return TaskResult(outcome="unknown_task", details={})

@app.get("/")
def read_root():
    return {"message": "Backend is running. Use /news/ingest and /news/clustered for news workflow."}


