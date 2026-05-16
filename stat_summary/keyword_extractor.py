import re
from collections import Counter
from typing import Dict, List

from stat_summary.stat_calculator import STOPWORDS, tokenize


PARTICLE_PATTERN = re.compile(
    r"(은|는|이|가|을|를|과|와|도|만|로|으로|에서|에게|부터|까지|보다)$"
)


def normalize_keyword(token: str) -> str:
    """
    토큰에서 간단한 조사와 불필요한 기호를 제거한다.
    예: 오픈AI가 -> 오픈AI, 모델은 -> 모델
    """
    token = token.strip()
    token = re.sub(r"^[\"'`]+|[\"'`]+$", "", token)
    token = PARTICLE_PATTERN.sub("", token)

    return token


def extract_keywords(content: str, top_n: int = 5) -> List[str]:
    """
    빈도 기반 핵심 키워드 후보를 추출한다.

    1차 구현에서는 외부 모델 없이 토큰 빈도를 기준으로 키워드를 선정한다.
    이후 Qwen, KeyBERT 등을 활용한 방식으로 개선할 수 있다.
    """
    tokens = tokenize(content)

    normalized_tokens = []
    for token in tokens:
        keyword = normalize_keyword(token)

        if len(keyword) < 2:
            continue

        if keyword in STOPWORDS or keyword.lower() in STOPWORDS:
            continue

        normalized_tokens.append(keyword)

    counter = Counter(normalized_tokens)

    keywords = []
    for keyword, _ in counter.most_common(top_n * 2):
        if keyword not in keywords:
            keywords.append(keyword)

        if len(keywords) >= top_n:
            break

    return keywords


def count_keyword_occurrences(text: str, keywords: List[str]) -> Dict[str, int]:
    """
    선택 기사 본문에서 각 키워드가 몇 번 등장하는지 계산한다.
    숫자 계산은 모델이 아니라 코드로 처리한다.
    """
    result = {}

    for keyword in keywords:
        if not keyword:
            result[keyword] = 0
            continue

        pattern = re.escape(keyword)
        count = len(re.findall(pattern, text, flags=re.IGNORECASE))
        result[keyword] = count

    return result


def select_core_keyword(keyword_count: Dict[str, int]) -> Dict[str, int | str]:
    """
    가장 많이 등장한 키워드를 core_keyword로 선정한다.
    score는 프론트 표시용 점수이며, 현재는 빈도 기반으로 계산한다.
    """
    if not keyword_count:
        return {
            "word": "",
            "score": 0,
        }

    max_count = max(keyword_count.values())

    if max_count == 0:
        return {
            "word": "",
            "score": 0,
        }

    core_word = max(keyword_count, key=keyword_count.get)

    # 가장 많이 등장한 단어는 90점대가 나오도록 단순 점수화
    score = min(100, 70 + max_count * 10)

    return {
        "word": core_word,
        "score": score,
    }