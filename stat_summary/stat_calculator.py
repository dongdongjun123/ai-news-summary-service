import re
from typing import List


STOPWORDS = {
    "그리고", "그러나", "하지만", "또한", "이번", "관련", "대한", "위해",
    "있는", "없는", "했다", "한다", "됐다", "된다", "것으로", "것이다",
    "에서", "으로", "에게", "까지", "부터", "보다", "뉴스", "기사", "기자",
    "통해", "밝혔다", "말했다", "전했다", "지난", "오늘", "내일", "최근",
    "수", "등", "및", "중", "더", "새", "첫", "것",
    "the", "and", "for", "with", "that", "this", "from", "are", "was", "were",
}


def split_sentences(text: str) -> List[str]:
    """
    뉴스 본문을 문장 단위로 분리한다.
    1차 구현에서는 마침표, 물음표, 느낌표, 줄바꿈을 기준으로 분리한다.
    """
    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+|[\n\r]+", text)

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def tokenize(text: str) -> List[str]:
    """
    뉴스 본문을 단어 단위로 나눈다.
    1차 구현에서는 외부 형태소 분석기 없이 한글/영문/숫자 덩어리를 토큰으로 본다.
    """
    if not text:
        return []

    raw_tokens = re.findall(r"[가-힣A-Za-z0-9]+", text)

    tokens = []
    for token in raw_tokens:
        token = token.strip()
        token_lower = token.lower()

        if len(token) < 2:
            continue

        if token in STOPWORDS or token_lower in STOPWORDS:
            continue

        tokens.append(token)

    return tokens


def count_words(text: str) -> int:
    """
    불용어와 한 글자 토큰을 제외한 단어 수를 계산한다.
    """
    return len(tokenize(text))


def count_sentences(text: str) -> int:
    """
    본문 문장 수를 계산한다.
    """
    return len(split_sentences(text))