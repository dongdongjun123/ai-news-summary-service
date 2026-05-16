from typing import Any, Dict, List, Optional

from stat_summary.keyword_extractor import count_keyword_occurrences


def join_corpus_contents(corpus_articles: Optional[List[Dict[str, Any]]]) -> str:
    """
    전체 기사 목록에서 본문 content만 모아 하나의 문자열로 합친다.

    corpus_articles 예시:
    [
        {"article_id": 1, "content": "뉴스 본문"},
        {"article_id": 2, "content": "뉴스 본문"}
    ]
    """
    if not corpus_articles:
        return ""

    contents = []

    for article in corpus_articles:
        content = article.get("content", "")
        if content:
            contents.append(str(content))

    return " ".join(contents)


def count_keywords_in_corpus(
    corpus_articles: Optional[List[Dict[str, Any]]],
    keywords: List[str],
) -> Dict[str, int]:
    """
    전체 기사 DB 기준으로 각 키워드가 몇 번 등장하는지 계산한다.
    """
    if not keywords:
        return {}

    corpus_text = join_corpus_contents(corpus_articles)

    if not corpus_text:
        return {keyword: 0 for keyword in keywords}

    return count_keyword_occurrences(corpus_text, keywords)