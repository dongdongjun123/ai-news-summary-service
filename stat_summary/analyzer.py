from typing import Any, Dict, List, Optional, Tuple

from stat_summary.corpus_analyzer import count_keywords_in_corpus
from stat_summary.insight_generator import (
    generate_ai_insights,
    generate_stat_analysis,
)
from stat_summary.keybert_related_terms import extract_related_terms_with_keybert
from stat_summary.keyword_extractor import (
    count_keyword_occurrences,
    extract_keywords,
    select_core_keyword,
)
from stat_summary.llm_keyword_extractor import extract_keywords_with_llm
from stat_summary.model_config import (
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_LLM_MODEL,
    KEYWORD_MODEL_FALLBACK,
    RELATED_TERMS_MODEL_FALLBACK,
)
from stat_summary.related_terms import extract_related_terms
from stat_summary.stat_calculator import count_sentences, count_words
from stat_summary.trend_analyzer import build_mention_trend


def get_keywords(
    content: str,
    top_n: int,
    use_llm: bool,
    llm_model_name: str,
) -> Tuple[List[str], str]:
    if use_llm:
        llm_keywords = extract_keywords_with_llm(
            content=content,
            top_n=top_n,
            model_name=llm_model_name,
        )

        if llm_keywords:
            return llm_keywords, llm_model_name

    return extract_keywords(content, top_n=top_n), KEYWORD_MODEL_FALLBACK


def get_related_terms(
    content: str,
    keywords: List[str],
    top_n: int,
    use_keybert: bool,
    embedding_model_name: str,
) -> Tuple[List[Dict[str, Any]], str]:
    if use_keybert:
        keybert_terms = extract_related_terms_with_keybert(
            content=content,
            keywords=keywords,
            top_n=top_n,
            embedding_model_name=embedding_model_name,
        )

        if keybert_terms:
            return keybert_terms, f"keybert_{embedding_model_name}"

    return (
        extract_related_terms(
            content=content,
            keywords=keywords,
            top_n=top_n,
        ),
        RELATED_TERMS_MODEL_FALLBACK,
    )


def analyze_article_statistics(
    article: Dict[str, Any],
    corpus_articles: Optional[List[Dict[str, Any]]] = None,
    top_n: int = 5,
    recent_n: int = 4,
    use_llm: bool = False,
    use_keybert: bool = False,
    llm_model_name: str = DEFAULT_LLM_MODEL,
    embedding_model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> Dict[str, Any]:
    """
    AI2 통계 분석 최종 진입 함수.

    use_llm=True이면 Qwen 기반 키워드 후보 추출을 시도한다.
    use_keybert=True이면 KeyBERT 기반 연관어 추출을 시도한다.

    모델 실행 실패 시 기존 rule-based 방식으로 fallback한다.
    """
    if corpus_articles is None:
        corpus_articles = []

    article_id = article.get("article_id") or article.get("id")
    title = article.get("title", "")
    content = article.get("content", "")

    word_count = count_words(content)
    sentence_count = count_sentences(content)

    keywords, keyword_model = get_keywords(
        content=content,
        top_n=top_n,
        use_llm=use_llm,
        llm_model_name=llm_model_name,
    )

    keyword_count = count_keyword_occurrences(content, keywords)

    corpus_keyword_count = count_keywords_in_corpus(
        corpus_articles=corpus_articles,
        keywords=keywords,
    )

    core_keyword = select_core_keyword(keyword_count)
    core_word = core_keyword.get("word", "")

    related_terms, related_terms_model = get_related_terms(
        content=content,
        keywords=keywords,
        top_n=6,
        use_keybert=use_keybert,
        embedding_model_name=embedding_model_name,
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
            "keyword_model": keyword_model,
            "related_terms_model": related_terms_model,
            "trend_model": "monthly_count_based",
            "insight_model": "rule_based",
        },
    }