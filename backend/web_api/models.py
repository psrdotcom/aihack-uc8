# models.py
from typing import Optional
from sqlmodel import Field, SQLModel
import datetime

class Articles(SQLModel, table=True):
    article_id: str = Field(primary_key=True)
    title: Optional[str] = None
    body: Optional[str] = None
    source: Optional[str] = Field(default=None, alias="source")
    published_date: Optional[str] = None
    location_mentions: Optional[str] = None
    officials_involved: Optional[str] = None
    relevance_category: Optional[str] = None
    sentiment: Optional[str] = None

class ArticleCreate(SQLModel):
    title: Optional[str] = None
    body: Optional[str] = None
    source: Optional[str] = None
    published_date: Optional[str] = None
    location_mentions: Optional[str] = None
    officials_involved: Optional[str] = None
    relevance_category: Optional[str] = None
    sentiment: Optional[str] = None

class ArticleRead(SQLModel):
    article_id: str
    title: Optional[str] = None
    body: Optional[str] = None
    source: Optional[str] = None
    published_date: Optional[str] = None
    location_mentions: Optional[str] = None
    officials_involved: Optional[str] = None
    relevance_category: Optional[str] = None
    sentiment: Optional[str] = None

class Clusters(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: Optional[datetime.date] = None
    linkedarticles: Optional[str] = None
    startdate: Optional[str] = None
    enddate: Optional[str] = None

class ClusterCreate(SQLModel):
    title: Optional[datetime.date] = None
    linkedarticles: Optional[str] = None
    startdate: Optional[str] = None
    enddate: Optional[str] = None

class ClusterRead(SQLModel):
    id: int
    title: Optional[datetime.date] = None
    linkedarticles: Optional[str] = None
    startdate: Optional[str] = None
    enddate: Optional[str] = None

