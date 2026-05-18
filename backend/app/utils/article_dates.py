"""기사 표시용 날짜.

기본: **DB news_articles.date** 그대로 (pgAdmin 과 동일).

구 파이프라인에서만 `DISPLAY_DATE_FALLBACK=true` 로 두고 본문/ID 보조 가능.

fallback 시 순서:
1) news_id 내 `.{YYYYMMDD}...` (기사별로 다름)
2) 본문 앞 한국어 날짜 (공통 문구에 걸리면 모두 같은 날로 보일 수 있음 → ID 우선)
3) DB date
"""

from __future__ import annotations

import re
from datetime import date as date_cls
from typing import Optional, TYPE_CHECKING

from app.core.config import settings

if TYPE_CHECKING:
    from app.models.news import NewsArticle

_LEAD_LEN = 800
_KR_DATE = re.compile(r"(20\d{2})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일")


def parse_korean_lead_date(content: Optional[str]) -> Optional[date_cls]:
    if not content:
        return None
    m = _KR_DATE.search(content[:_LEAD_LEN])
    if not m:
        return None
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    try:
        return date_cls(y, mo, d)
    except ValueError:
        return None


def parse_date_from_news_id(news_id: str) -> Optional[date_cls]:
    """`06101302.2026040812345678901` 같은 ID에서 첫 8자리 날짜 추출 시도."""
    if not news_id or "." not in news_id:
        return None
    suffix = news_id.split(".", 1)[1]
    if len(suffix) < 8 or not suffix[:8].isdigit():
        return None
    ymd = suffix[:8]
    try:
        return date_cls(int(ymd[:4]), int(ymd[4:6]), int(ymd[6:8]))
    except ValueError:
        return None


def resolve_display_date(article: "NewsArticle") -> date_cls:
    if not settings.DISPLAY_DATE_FALLBACK:
        return article.date

    # news_id 내 날짜가 기사별로 다름. 본문 선두의 한글 날짜는 '사이트 공통 안내 4월 30일' 등에
    # 잡혀 전 기사가 같은 날짜로 보이는 경우가 있어 ID 를 먼저 본다.
    for candidate in (
        parse_date_from_news_id(article.news_id),
        parse_korean_lead_date(article.content),
    ):
        if candidate is not None:
            return candidate
    return article.date
