from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from stat_summary.keyword_extractor import count_keyword_occurrences


def parse_date(value: Any) -> Optional[datetime]:
    """
    기사 날짜 문자열을 datetime 객체로 변환한다.

    지원 예시:
    - 2025.06.01
    - 2025-06-01
    - 2025/06/01
    - 2025-06-01 10:30:00
    """
    if not value:
        return None

    text = str(value).strip()

    formats = [
        "%Y.%m.%d",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y.%m.%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(text.replace("Z", ""))
    except ValueError:
        return None


def build_mention_trend(
    corpus_articles: Optional[List[Dict[str, Any]]],
    core_keyword: str,
    recent_n: int = 4,
) -> List[Dict[str, Any]]:
    """
    전체 기사 목록에서 핵심 키워드의 월별 언급량을 계산한다.

    프론트의 언급량 추이 그래프에 사용할 수 있도록
    [{ "month": "3월", "count": 10 }] 형태로 반환한다.
    """
    if not corpus_articles or not core_keyword:
        return []

    monthly_count = defaultdict(int)

    for article in corpus_articles:
        content = str(article.get("content", ""))
        published_at = (
            article.get("published_at")
            or article.get("date")
            or article.get("created_at")
        )

        date_obj = parse_date(published_at)

        if not date_obj:
            continue

        month_key = f"{date_obj.year}-{date_obj.month:02d}"
        keyword_count = count_keyword_occurrences(content, [core_keyword])
        monthly_count[month_key] += keyword_count.get(core_keyword, 0)

    sorted_items = sorted(monthly_count.items())

    if recent_n > 0:
        sorted_items = sorted_items[-recent_n:]

    trend = []

    for month_key, count in sorted_items:
        _, month = month_key.split("-")

        trend.append({
            "month": f"{int(month)}월",
            "count": count,
        })

    return trend