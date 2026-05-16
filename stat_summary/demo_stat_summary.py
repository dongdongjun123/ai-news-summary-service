import json

from stat_summary.analyzer import analyze_article_statistics


sample_articles = [
    {
        "article_id": 1,
        "title": "오픈AI, 새 모델 발표... 추론 능력 대폭 강화",
        "source": "연합뉴스",
        "published_at": "2025.02.01",
        "content": (
            "오픈AI가 최신 언어모델을 공개했다. "
            "오픈AI는 ChatGPT와 GPT 모델의 추론 능력 강화에 집중하고 있다."
        ),
    },
    {
        "article_id": 2,
        "title": "AI 서비스 시장, ChatGPT 중심으로 성장",
        "source": "테크뉴스",
        "published_at": "2025.03.03",
        "content": (
            "ChatGPT를 활용한 AI 서비스가 빠르게 늘어나고 있다. "
            "오픈AI API를 사용하는 기업도 증가하고 있다."
        ),
    },
    {
        "article_id": 3,
        "title": "GPT 모델 경쟁 심화",
        "source": "IT신문",
        "published_at": "2025.04.10",
        "content": (
            "GPT 모델과 추론 모델 경쟁이 심화되면서 오픈AI와 여러 AI 기업이 성능 개선에 집중하고 있다. "
            "오픈AI는 API 시장에서도 주목받고 있다."
        ),
    },
    {
        "article_id": 4,
        "title": "오픈AI API 생태계 확장",
        "source": "경제신문",
        "published_at": "2025.05.15",
        "content": (
            "오픈AI API 생태계가 확장되고 있다. "
            "ChatGPT와 오픈AI 관련 서비스가 기업 시장에서 빠르게 확산되고 있다."
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