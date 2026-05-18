from datetime import date as date_type
from typing import List, Optional

from pydantic import BaseModel


class NewsListItem(BaseModel):
    id: str
    title: str
    summary: Optional[str] = None
    category: str
    source: Optional[str] = None
    published_at: date_type
    url: Optional[str] = None
    thumbnail: Optional[str] = None


class NewsDetail(BaseModel):
    id: str
    title: str
    summary: Optional[str] = None
    content: str
    category: str
    source: Optional[str] = None
    published_at: date_type
    url: Optional[str] = None
    thumbnail: Optional[str] = None
    mention_trend: List[int] = []
    related_keywords: List[str] = []
