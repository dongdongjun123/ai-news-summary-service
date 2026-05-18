from datetime import date as date_type, timedelta
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.news import NewsArticle


def list_news(
    db: Session,
    category: Optional[str],
    limit: Optional[int],
) -> List[NewsArticle]:
    stmt = select(NewsArticle)
    if category:
        stmt = stmt.where(NewsArticle.main_category == category)
    stmt = stmt.order_by(
        NewsArticle.date.desc(),
        NewsArticle.news_id.desc(),
    )
    if limit is not None:
        stmt = stmt.limit(limit)
    return list(db.execute(stmt).scalars().all())


def get_news(db: Session, news_id: str) -> Optional[NewsArticle]:
    return db.get(NewsArticle, news_id)


def get_corpus_for_category(
    db: Session,
    category: str,
    anchor_date: date_type,
    days: int,
) -> List[NewsArticle]:
    """기사 발행일을 기준으로 같은 카테고리의 ±days 범위 코퍼스를 반환.
    트렌드/언급량 계산용으로 쓰인다.
    """
    start = anchor_date - timedelta(days=days)
    end = anchor_date + timedelta(days=days)
    stmt = (
        select(NewsArticle)
        .where(NewsArticle.main_category == category)
        .where(NewsArticle.date >= start)
        .where(NewsArticle.date <= end)
        .order_by(NewsArticle.date.asc())
    )
    return list(db.execute(stmt).scalars().all())


def update_summary(db: Session, news_id: str, summary: str) -> None:
    article = db.get(NewsArticle, news_id)
    if article is None:
        return
    article.summary = summary
    db.commit()


def clear_summary(db: Session, news_id: str) -> None:
    """summary 컬럼을 NULL 로 비운다. 재요약 전에 사용."""
    article = db.get(NewsArticle, news_id)
    if article is None:
        return
    article.summary = None
    db.commit()
