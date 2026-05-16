import json

from stat_summary.analyzer import analyze_article_statistics
from stat_summary.stat_calculator import split_sentences, tokenize


sample_article = {
    "article_id": 1,
    "title": "오픈AI, 새 모델 발표... 추론 능력 대폭 강화",
    "source": "연합뉴스",
    "published_at": "2025.06.01",
    "content": (
        "오픈AI가 최신 언어모델을 공개하며 수학과 코딩 분야 성능이 크게 향상됐다고 밝혔다. "
        "특히 복잡한 추론 문제에서 전문가 수준의 정확도를 보였으며, 기업용 API도 함께 공개됐다. "
        "ChatGPT와 GPT 모델은 추론 능력 강화와 API 생태계 확장을 중심으로 주목받고 있다."
    ),
}


def main():
    result = analyze_article_statistics(article=sample_article)

    print("=== 문장 분리 결과 ===")
    print(split_sentences(sample_article["content"]))

    print("\n=== 토큰화 결과 ===")
    print(tokenize(sample_article["content"]))

    print("\n=== 최종 JSON 결과 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()