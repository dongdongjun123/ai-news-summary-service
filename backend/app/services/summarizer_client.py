"""
summarizer 서비스(`http://localhost:8001`)에 요약을 요청하는 클라이언트.

summarizer/main.py 의 `POST /summarize/batch` 스펙:
  Request : {"articles": [{"id": int, "text": str}, ...]}
  Response: {"summaries": [{"id": int, "summary": Optional[str]}, ...]}
"""

import logging
from typing import Optional

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


async def summarize_article(content: str) -> Optional[str]:
    """summarizer 서비스에 단건 요약을 요청한다.
    실패/타임아웃 시 None 반환 (호출 측에서 본문만 응답하도록 분기).
    """
    if not content:
        return None

    payload = {
        "articles": [
            {"id": 1, "text": content},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=settings.SUMMARIZER_TIMEOUT) as client:
            response = await client.post(
                f"{settings.SUMMARIZER_URL}/summarize/batch",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
    except httpx.TimeoutException:
        logger.warning("summarizer timeout (>= %ss)", settings.SUMMARIZER_TIMEOUT)
        return None
    except httpx.HTTPError as e:
        logger.warning("summarizer http error: %s", e)
        return None
    except Exception as e:
        logger.exception("summarizer unexpected error: %s", e)
        return None

    summaries = data.get("summaries") or []
    if not summaries:
        return None

    first = summaries[0] or {}
    summary = first.get("summary")
    if summary and isinstance(summary, str):
        return summary.strip() or None
    return None
