from collections import defaultdict
from datetime import date as date_cls
from datetime import datetime, timedelta
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


def build_mention_trend_recent_weeks(
    corpus_articles: Optional[List[Dict[str, Any]]],
    core_keyword: str,
    anchor: Optional[datetime] = None,
    num_weeks: int = 4,
) -> List[Dict[str, Any]]:
    """
    프론트 카피 「최근 4주」에 맞춰, 기준일(보통 해당 기사 발행일) 이전 포함 4개 주간 구간의
    핵심 키워드 언급 합계를 반환한다. [{ \"month\": \"1주차\", \"count\": n }, ...] 형태 유지.

    corpus 가 비었거나 코어 키워드가 비면 각 주 0건으로 채운다.
    """
    labels = [f"{i + 1}주차" for i in range(num_weeks)]

    if not corpus_articles or not core_keyword:
        return [{"month": lab, "count": 0} for lab in labels]

    if anchor is None:
        anchor_dt = datetime.now()
    else:
        anchor_dt = anchor

    anchor_date: date_cls = (
        anchor_dt.date()
        if isinstance(anchor_dt, datetime)
        else anchor_dt  # type: ignore[arg-type]
    )

    newest_week_start = anchor_date - timedelta(days=6)
    buckets: List[tuple[date_cls, date_cls]] = []
    for ki in range(num_weeks):
        start_d = newest_week_start - timedelta(days=7 * (num_weeks - 1 - ki))
        end_d = start_d + timedelta(days=7)
        buckets.append((start_d, end_d))

    counts = [0] * num_weeks

    for article in corpus_articles:
        dt = parse_date(
            article.get("published_at")
            or article.get("date")
            or article.get("created_at"),
        )
        if not dt:
            continue
        article_d = dt.date() if isinstance(dt, datetime) else dt
        bucket_idx = -1
        for i, (s, e) in enumerate(buckets):
            if s <= article_d < e:
                bucket_idx = i
                break
        if bucket_idx < 0:
            continue

        content = str(article.get("content", ""))
        kwc = count_keyword_occurrences(content, [core_keyword])
        counts[bucket_idx] += int(kwc.get(core_keyword, 0) or 0)

    return [{"month": labels[i], "count": counts[i]} for i in range(num_weeks)]