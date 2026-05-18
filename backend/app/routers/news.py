from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.models.news import NewsArticle
from app.repositories import news as news_repo
from app.schemas.news import NewsDetail, NewsListItem
from app.services.stats_service import analyze_for_response
from app.services.summarizer_client import summarize_article
from app.utils.category_mapping import to_db_category, to_front_category


router = APIRouter(prefix="/api", tags=["news"])


def _to_list_item(article: NewsArticle) -> NewsListItem:
    return NewsListItem(
        id=article.news_id,
        title=article.title,
        summary=article.summary,
        category=to_front_category(article.main_category),
        source=article.press,
        published_at=article.date,
        url=None,
        thumbnail=None,
    )


def _to_detail(
    article: NewsArticle,
    mention_trend: List[int],
    related_keywords: List[str],
) -> NewsDetail:
    return NewsDetail(
        id=article.news_id,
        title=article.title,
        summary=article.summary,
        content=article.content,
        category=to_front_category(article.main_category),
        source=article.press,
        published_at=article.date,
        url=None,
        thumbnail=None,
        mention_trend=mention_trend,
        related_keywords=related_keywords,
    )


@router.get("/news", response_model=List[NewsListItem])
def list_news(
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=None, ge=1, le=500),
    db: Session = Depends(get_db),
):
    db_category: Optional[str] = None
    if category and category.strip() and category.strip() != "전체":
        db_category = to_db_category(category.strip())

    fetched = news_repo.list_news(
        db=db,
        category=db_category,
        limit=limit or settings.NEWS_DEFAULT_LIMIT,
    )
    return [_to_list_item(a) for a in fetched]


@router.get("/news/{news_id}", response_model=NewsDetail)
async def get_news(news_id: str, db: Session = Depends(get_db)):
    article = news_repo.get_news(db, news_id)
    if article is None:
        raise HTTPException(status_code=404, detail="news not found")

    if not article.summary:
        new_summary = await summarize_article(article.content)
        if new_summary:
            news_repo.update_summary(db, article.news_id, new_summary)
            article.summary = new_summary

    corpus = news_repo.get_corpus_for_category(
        db=db,
        category=article.main_category,
        anchor_date=article.date,
        days=settings.STATS_CORPUS_DAYS,
    )

    mention_trend, related_keywords = analyze_for_response(article, corpus)

    return _to_detail(article, mention_trend, related_keywords)


@router.post("/news/{news_id}/summary", response_model=NewsDetail)
async def regenerate_summary(news_id: str, db: Session = Depends(get_db)):
    article = news_repo.get_news(db, news_id)
    if article is None:
        raise HTTPException(status_code=404, detail="news not found")

    new_summary = await summarize_article(article.content)
    if not new_summary:
        raise HTTPException(status_code=502, detail="summarizer failed")

    news_repo.update_summary(db, article.news_id, new_summary)
    article.summary = new_summary

    return _to_detail(article, mention_trend=[], related_keywords=[])
