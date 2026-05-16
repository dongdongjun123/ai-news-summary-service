import json

from stat_summary.analyzer import analyze_article_statistics


sample_articles = [
    {
        "article_id": 1,
        "title": "오픈AI, 새 모델 발표... 추론 능력 대폭 강화",
        "source": "연합뉴스",
        "published_at": "2025.06.01",
        "content": (
            "오픈AI가 최신 언어모델을 공개하며 수학과 코딩 분야 성능이 크게 향상됐다고 밝혔다. "
            "오픈AI는 ChatGPT와 GPT 모델의 추론 능력 강화에 집중하고 있다. "
            "특히 복잡한 추론 문제에서 전문가 수준의 정확도를 보였으며, 기업용 API도 함께 공개됐다. "
            "ChatGPT와 GPT 모델은 추론 능력 강화와 API 생태계 확장을 중심으로 주목받고 있다. "
            "오픈AI와 ChatGPT는 AI 서비스 시장에서 계속 주목받고 있다."
        ),
    },
    {
        "article_id": 2,
        "title": "AI 서비스 시장, ChatGPT 중심으로 성장",
        "source": "테크뉴스",
        "published_at": "2025.06.02",
        "content": (
            "ChatGPT를 활용한 AI 서비스가 빠르게 늘어나고 있다. "
            "OpenAI API를 사용하는 기업도 증가하면서 생성형 AI 생태계가 확대되고 있다."
        ),
    },
    {
        "article_id": 3,
        "title": "GPT 모델 경쟁 심화",
        "source": "IT신문",
        "published_at": "2025.06.03",
        "content": (
            "GPT 모델과 추론 모델 경쟁이 심화되면서 OpenAI와 여러 AI 기업이 성능 개선에 집중하고 있다. "
            "API 시장에서도 개발자와 기업 고객을 중심으로 수요가 증가하고 있다."
        ),
    },
]


def main():
    selected_article = sample_articles[0]

    result = analyze_article_statistics(
        article=selected_article,
        corpus_articles=sample_articles,
    )

    print("=== 최종 JSON 결과 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()