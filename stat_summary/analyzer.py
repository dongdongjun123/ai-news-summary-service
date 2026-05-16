from typing import Any, Dict, List, Optional

from stat_summary.corpus_analyzer import count_keywords_in_corpus
from stat_summary.insight_generator import (
    generate_ai_insights,
    generate_stat_analysis,
)
from stat_summary.keyword_extractor import (
    count_keyword_occurrences,
    extract_keywords,
    select_core_keyword,
)
from stat_summary.related_terms import extract_related_terms
from stat_summary.stat_calculator import count_sentences, count_words
from stat_summary.trend_analyzer import build_mention_trend


def analyze_article_statistics(
    article: Dict[str, Any],
    corpus_articles: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    AI2 통계 분석 최종 진입 함수.

    현재 Issue에서는 stat_analysis와 ai_insights까지 계산한다.
    """
    if corpus_articles is None:
        corpus_articles = []

    content = article.get("content", "")

    keywords = extract_keywords(content, top_n=5)
    keyword_count = count_keyword_occurrences(content, keywords)
    corpus_keyword_count = count_keywords_in_corpus(corpus_articles, keywords)
    core_keyword = select_core_keyword(keyword_count)
    core_word = core_keyword.get("word", "")

    related_terms = extract_related_terms(content, keywords, top_n=6)

    mention_trend = build_mention_trend(
        corpus_articles=corpus_articles,
        core_keyword=core_word,
        recent_n=4,
    )

    stat_analysis = generate_stat_analysis(
        core_keyword=core_keyword,
        related_terms=related_terms,
        mention_trend=mention_trend,
    )

    ai_insights = generate_ai_insights(
        core_keyword=core_keyword,
        related_terms=related_terms,
        mention_trend=mention_trend,
    )

    return {
        "article_id": article.get("article_id") or article.get("id"),
        "title": article.get("title", ""),
        "statistics": {
            "word_count": count_words(content),
            "sentence_count": count_sentences(content),
            "keyword_count": keyword_count,
            "corpus_keyword_count": corpus_keyword_count,
        },
        "mention_trend": mention_trend,
        "core_keyword": core_keyword,
        "related_terms": related_terms,
        "stat_analysis": stat_analysis,
        "ai_insights": ai_insights,
        "model_info": {
            "keyword_model": "frequency_based",
            "related_terms_model": "co_occurrence_based",
            "trend_model": "monthly_count_based",
            "insight_model": "rule_based",
        },
    }