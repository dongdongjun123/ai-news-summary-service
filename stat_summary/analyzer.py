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
    top_n: int = 5,
    recent_n: int = 4,
) -> Dict[str, Any]:
    """
    AI2 통계 분석 최종 진입 함수.

    백엔드는 DB에서 선택 기사와 전체 기사 목록을 가져온 뒤
    이 함수 하나를 호출하면 된다.
    """
    if corpus_articles is None:
        corpus_articles = []

    article_id = article.get("article_id") or article.get("id")
    title = article.get("title", "")
    content = article.get("content", "")

    word_count = count_words(content)
    sentence_count = count_sentences(content)

    keywords = extract_keywords(content, top_n=top_n)
    keyword_count = count_keyword_occurrences(content, keywords)

    corpus_keyword_count = count_keywords_in_corpus(
        corpus_articles=corpus_articles,
        keywords=keywords,
    )

    core_keyword = select_core_keyword(keyword_count)
    core_word = core_keyword.get("word", "")

    related_terms = extract_related_terms(
        content=content,
        keywords=keywords,
        top_n=6,
    )

    mention_trend = build_mention_trend(
        corpus_articles=corpus_articles,
        core_keyword=core_word,
        recent_n=recent_n,
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
        "article_id": article_id,
        "title": title,
        "statistics": {
            "word_count": word_count,
            "sentence_count": sentence_count,
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