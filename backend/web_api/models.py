# models.py
from typing import Optional
from sqlmodel import Field, SQLModel

class Articles(SQLModel, table=True):
    articles_id: Optional[str] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    body: str
    source: str
    published_date: Optional[str] = Field(default=None, index=True)
    # location_mentions: Optional[str] = Field(default=None, index=True)
    # officials_involved: Optional[str] = Field(default=None, index=True)
    # relenace_category: Optional[str] = Field(default=None, index=True)
    sentiment: Optional[str] = Field(default=None, index=True)
    # name: str = Field(index=True)
    # secret_name: str
    # age: Optional[int] = Field(default=None, index=True)


class ArticleCreate(Articles):
    pass

class ArticleRead(Articles):
    articles_id: str
    
    
class Clusters(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    linkedarticles: Optional[str] = Field(default=None, index=True)
    startdate: Optional[str] = Field(default=None, index=True)
    enddate: Optional[str] = Field(default=None, index=True)
    
class ClusterCreate(Clusters):
    pass
    
class ClusterRead(Clusters):
    id: str
    
