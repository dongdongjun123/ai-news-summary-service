from typing import List, Optional

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.models.news import NewsArticle
from app.repositories import news as news_repo
from app.schemas.news import NewsDetail, NewsListItem
from app.services.stats_service import analyze_for_response
from app.services.summarizer_client import summarize_article
from app.utils.article_dates import resolve_display_date
from app.utils.category_mapping import to_db_category, to_front_category


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["news"])


def _article_needs_fresh_summary(article: NewsArticle) -> bool:
    """summary 가 NULL 이거나 공백뿐이면 summarizer 를 호출한다."""
    s = article.summary
    if s is None:
        return True
    return len(str(s).strip()) == 0


def _to_list_item(article: NewsArticle) -> NewsListItem:
    pub = resolve_display_date(article)
    return NewsListItem(
        id=article.news_id,
        title=article.title,
        summary=article.summary,
        category=to_front_category(article.main_category),
        source=article.press,
        published_at=pub,
        url=None,
        thumbnail=None,
    )


def _to_detail(
    article: NewsArticle,
    mention_trend: List[int],
    related_keywords: List[str],
) -> NewsDetail:
    pub = resolve_display_date(article)
    return NewsDetail(
        id=article.news_id,
        title=article.title,
        summary=article.summary,
        content=article.content,
        category=to_front_category(article.main_category),
        source=article.press,
        published_at=pub,
        url=None,
        thumbnail=None,
        mention_trend=mention_trend,
        related_keywords=related_keywords,
    )


@router.get("/news", response_model=List[NewsListItem])
def list_news(
    category: Optional[str] = Query(default=None),
    # 생략 시 LIMIT 없이 전부 조회. 대량 DB는 ?limit= 으로 상한만 걸 것.
    limit: Optional[int] = Query(default=None, ge=1, le=200_000),
    db: Session = Depends(get_db),
):
    db_category: Optional[str] = None
    if category and category.strip() and category.strip() != "전체":
        db_category = to_db_category(category.strip())

    fetched = news_repo.list_news(
        db=db,
        category=db_category,
        limit=limit,
    )
    return [_to_list_item(a) for a in fetched]


@router.get("/news/{news_id}", response_model=NewsDetail)
async def get_news(
    news_id: str,
    force_summarize: bool = Query(
        False,
        description=(
            "true 이면 DB 의 summary 를 비운 뒤 요약 서비스를 호출해 다시 채웁니다. "
            "브라우저/포스트맨에서 재요약 테스트할 때 사용."
        ),
    ),
    db: Session = Depends(get_db),
):
    article = news_repo.get_news(db, news_id)
    if article is None:
        raise HTTPException(status_code=404, detail="news not found")

    if force_summarize:
        news_repo.clear_summary(db, news_id)
        db.refresh(article)
        logger.warning("[news] force_summarize=1 → summary 비움 후 재요약 시도 (news_id=%s)", news_id)

    need_summary = _article_needs_fresh_summary(article)
    logger.warning(
        "[news] GET /api/news/%s detail — db_date=%s display_date=%s need_summarizer_call=%s",
        news_id,
        article.date.isoformat() if article.date else None,
        resolve_display_date(article).isoformat(),
        need_summary,
    )

    if need_summary:
        new_summary = await summarize_article(article.content)
        if new_summary:
            news_repo.update_summary(db, article.news_id, new_summary)
            article.summary = new_summary
        else:
            logger.warning(
                "[news] summarizer 가 빈 요약을 반환했거나 연결 실패 (news_id=%s)",
                news_id,
            )

    corpus = news_repo.get_corpus_for_category(
        db=db,
        category=article.main_category,
        anchor_date=resolve_display_date(article),
        days=settings.STATS_CORPUS_DAYS,
    )

    mention_trend, related_keywords = analyze_for_response(article, corpus)

    return _to_detail(article, mention_trend, related_keywords)


@router.post("/news/{news_id}/summary", response_model=NewsDetail)
async def regenerate_summary(news_id: str, db: Session = Depends(get_db)):
    article = news_repo.get_news(db, news_id)
    if article is None:
        raise HTTPException(status_code=404, detail="news not found")

    # 기존 요약을 무시하고 새로 생성 (DB 먼저 비우면 목록/로그에서도 '재생성' 의도가 분명함)
    news_repo.clear_summary(db, news_id)
    db.refresh(article)

    new_summary = await summarize_article(article.content)
    if not new_summary:
        raise HTTPException(status_code=502, detail="summarizer failed")

    news_repo.update_summary(db, article.news_id, new_summary)
    article.summary = new_summary

    return _to_detail(article, mention_trend=[], related_keywords=[])
