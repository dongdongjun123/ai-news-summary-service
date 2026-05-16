from typing import Any, Dict, List, Optional

from stat_summary.stat_calculator import count_sentences, count_words


def analyze_article_statistics(
    article: Dict[str, Any],
    corpus_articles: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    AI2 통계 분석 최종 진입 함수.

    현재 Issue에서는 word_count, sentence_count를 계산한다.
    이후 Issue에서 키워드, 연관어, 언급량 추이 기능을 순차적으로 추가한다.
    """
    if corpus_articles is None:
        corpus_articles = []

    content = article.get("content", "")

    return {
        "article_id": article.get("article_id") or article.get("id"),
        "title": article.get("title", ""),
        "statistics": {
            "word_count": count_words(content),
            "sentence_count": count_sentences(content),
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