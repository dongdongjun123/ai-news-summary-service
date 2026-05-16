from typing import Any, Dict, List, Optional


def analyze_article_statistics(
    article: Dict[str, Any],
    corpus_articles: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    AI2 통계 분석 최종 진입 함수.

    현재 Issue에서는 기본 JSON 구조만 반환한다.
    이후 Issue에서 단어 수, 문장 수, 키워드, 연관어, 언급량 추이 기능을 순차적으로 추가한다.

    Parameters
    ----------
    article:
        선택된 뉴스 기사 1개
    corpus_articles:
        DB에 저장된 전체 기사 리스트

    Returns
    -------
    Dict[str, Any]
        프론트/백엔드 연동용 AI2 통계 분석 JSON
    """
    if corpus_articles is None:
        corpus_articles = []

    return {
        "article_id": article.get("article_id") or article.get("id"),
        "title": article.get("title", ""),
        "statistics": {
            "word_count": 0,
            "sentence_count": 0,
            "keyword_count": {},
            "corpus_keyword_count": {},
        },
        "mention_trend": [],
        "core_keyword": {
            "word": "",
            "score": 0,
        },
        "related_terms": [],
        "stat_analysis": "",
        "ai_insights": [],
        "model_info": {
            "keyword_model": "not_applied_yet",
            "related_terms_model": "not_applied_yet",
        },
    }