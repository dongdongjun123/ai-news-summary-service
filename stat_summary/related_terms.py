from collections import Counter
from typing import Any, Dict, List

from stat_summary.keyword_extractor import normalize_keyword
from stat_summary.stat_calculator import STOPWORDS, split_sentences, tokenize


def extract_related_terms(
    content: str,
    keywords: List[str],
    top_n: int = 6,
) -> List[Dict[str, Any]]:
    """
    핵심 키워드가 포함된 문장에서 함께 등장한 단어를 연관어로 추출한다.

    1차 구현에서는 모델을 사용하지 않고, 동시 등장 기반으로 계산한다.
    이후 KeyBERT 또는 임베딩 모델 기반 방식으로 개선할 수 있다.
    """
    if not content or not keywords:
        return []

    keyword_set = set(keywords)
    related_counter = Counter()

    for sentence in split_sentences(content):
        has_keyword = any(keyword in sentence for keyword in keywords)

        if not has_keyword:
            continue

        tokens = tokenize(sentence)

        for token in tokens:
            word = normalize_keyword(token)

            if len(word) < 2:
                continue

            if word in keyword_set:
                continue

            if word in STOPWORDS or word.lower() in STOPWORDS:
                continue

            related_counter[word] += 1

    related_terms = []

    for word, count in related_counter.most_common(top_n):
        score = calculate_related_score(count)

        related_terms.append({
            "word": word,
            "score": score,
            "count": count,
        })

    return related_terms


def calculate_related_score(count: int) -> int:
    """
    연관어 점수를 계산한다.

    현재는 등장 횟수 기반의 단순 점수이며,
    프론트에서 연관도 막대나 순위 표시용으로 사용할 수 있다.
    """
    if count <= 0:
        return 0

    return min(100, 60 + count * 10)