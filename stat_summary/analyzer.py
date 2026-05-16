from typing import Any, Dict, List, Optional

from stat_summary.corpus_analyzer import count_keywords_in_corpus
from stat_summary.keyword_extractor import (
    count_keyword_occurrences,
    extract_keywords,
    select_core_keyword,
)
from stat_summary.stat_calculator import count_sentences, count_words


def analyze_article_statistics(
    article: Dict[str, Any],
    corpus_articles: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    AI2 통계 분석 최종 진입 함수.

    현재 Issue에서는 선택 기사 기준 keyword_count와
    전체 기사 기준 corpus_keyword_count를 함께 계산한다.
    """
    if corpus_articles is None:
        corpus_articles = []

    content = article.get("content", "")

    keywords = extract_keywords(content, top_n=5)
    keyword_count = count_keyword_occurrences(content, keywords)
    corpus_keyword_count = count_keywords_in_corpus(corpus_articles, keywords)
    core_keyword = select_core_keyword(keyword_count)

    return {
        "article_id": article.get("article_id") or article.get("id"),
        "title": article.get("title", ""),
        "statistics": {
            "word_count": count_words(content),
            "sentence_count": count_sentences(content),
            "keyword_count": keyword_count,
            "corpus_keyword_count": corpus_keyword_count,
        },
        "mention_trend": [],
        "core_keyword": core_keyword,
        "related_terms": [],
        "stat_analysis": "",
        "ai_insights": [],
        "model_info": {
            "keyword_model": "frequency_based",
            "related_terms_model": "not_applied_yet",
        },
    }