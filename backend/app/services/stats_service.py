"""
stat_summary.analyzer.analyze_article_statistics 호출 + 프론트가 기대하는
mention_trend(number[]) / related_keywords(string[]) 형태로 변환하는 서비스.
"""

import logging
from typing import Any, Dict, List, Tuple

from app.core.config import settings
from app.models.news import NewsArticle
from app.utils.article_dates import resolve_display_date


logger = logging.getLogger(__name__)


def _article_to_dict(article: NewsArticle) -> Dict[str, Any]:
    """stat_summary 에 넘기는 dict 형태. trend_analyzer 가 date/published_at 키를
    참조하므로 'date' 와 'published_at' 둘 다 채워준다.
    """
    logical_date = resolve_display_date(article)
    date_str = logical_date.isoformat()
    return {
        "id": article.news_id,
        "article_id": article.news_id,
        "title": article.title or "",
        "content": article.content or "",
        "date": date_str,
        "published_at": date_str,
        "main_category": article.main_category,
        "category": article.main_category,
    }


def _trend_to_int_list(trend: List[Dict[str, Any]]) -> List[int]:
    """`[{"month": "3월", "count": 10}, ...]` → `[10, ...]`"""
    values: List[int] = []
    for item in trend or []:
        if isinstance(item, dict):
            try:
                values.append(int(item.get("count") or 0))
            except (TypeError, ValueError):
                values.append(0)
        elif isinstance(item, (int, float)):
            values.append(int(item))
    return values


def _related_to_word_list(related: List[Dict[str, Any]]) -> List[str]:
    """`[{"word": "...", "score": ..., "count": ...}, ...]` → `["...", ...]`"""
    words: List[str] = []
    for item in related or []:
        if isinstance(item, dict):
            word = item.get("word") or item.get("term")
            if word:
                words.append(str(word))
        elif item:
            words.append(str(item))
    return words


def analyze_for_response(
    article: NewsArticle,
    corpus: List[NewsArticle],
) -> Tuple[List[int], List[str]]:
    """기사 + 코퍼스를 받아 프론트 응답용 (mention_trend, related_keywords) 를 반환.
    실패 시 ([], []) 로 안전하게 빠짐.
    """
    try:
        from stat_summary.analyzer import analyze_article_statistics
    except Exception as e:
        logger.exception("stat_summary import 실패: %s", e)
        return [], []

    try:
        result: Dict[str, Any] = analyze_article_statistics(
            article=_article_to_dict(article),
            corpus_articles=[_article_to_dict(a) for a in corpus],
            top_n=settings.STATS_TOP_N,
            recent_n=settings.STATS_RECENT_N,
            use_llm=settings.STATS_USE_LLM,
            use_keybert=settings.STATS_USE_KEYBERT,
        )
    except Exception as e:
        logger.exception("analyze_article_statistics 실패: %s", e)
        return [], []

    mention_trend = _trend_to_int_list(result.get("mention_trend") or [])
    related_keywords = _related_to_word_list(result.get("related_terms") or [])
    return mention_trend, related_keywords
