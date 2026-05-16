from typing import Any, Dict, List


def generate_stat_analysis(
    core_keyword: Dict[str, Any],
    related_terms: List[Dict[str, Any]],
    mention_trend: List[Dict[str, Any]],
) -> str:
    """
    통계 결과를 한 문장으로 요약한다.

    1차 구현에서는 LLM을 사용하지 않고 규칙 기반 문장을 생성한다.
    """
    core_word = core_keyword.get("word", "")

    if not core_word:
        return "분석 가능한 핵심 키워드가 충분하지 않습니다."

    if related_terms:
        top_related = related_terms[0].get("word", "")
        return (
            f"본문에서는 '{core_word}' 키워드가 중심적으로 나타나며, "
            f"'{top_related}'와 함께 언급되어 주요 이슈의 흐름을 보여줍니다."
        )

    if mention_trend:
        return (
            f"본문에서는 '{core_word}' 키워드가 핵심적으로 등장하며, "
            f"전체 기사 데이터에서도 월별 언급량 추이를 확인할 수 있습니다."
        )

    return f"본문에서는 '{core_word}' 키워드가 주요 주제로 나타납니다."


def generate_ai_insights(
    core_keyword: Dict[str, Any],
    related_terms: List[Dict[str, Any]],
    mention_trend: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """
    프론트의 AI 인사이트 카드에 들어갈 문장을 생성한다.
    최대 3개 인사이트를 반환한다.
    """
    insights = []

    core_word = core_keyword.get("word", "")
    core_score = core_keyword.get("score", 0)

    if core_word:
        insights.append({
            "title": "핵심 키워드 집중",
            "description": f"선택한 기사에서는 '{core_word}'가 핵심 키워드로 나타나며, 중요도 점수는 {core_score}점입니다.",
        })

    if related_terms:
        related_words = ", ".join(
            term.get("word", "")
            for term in related_terms[:3]
            if term.get("word", "")
        )

        if related_words:
            insights.append({
                "title": "연관어 흐름 확인",
                "description": f"'{related_words}' 등이 함께 등장해 기사 맥락을 보완합니다.",
            })

    trend_insight = make_trend_insight(mention_trend)

    if trend_insight:
        insights.append(trend_insight)

    while len(insights) < 3:
        insights.append({
            "title": "추가 분석 대기",
            "description": "더 많은 기사 데이터가 쌓이면 키워드 흐름과 연관어 분석을 더 정교하게 제공할 수 있습니다.",
        })

    return insights[:3]


def make_trend_insight(
    mention_trend: List[Dict[str, Any]],
) -> Dict[str, str] | None:
    """
    월별 언급량 추이를 기반으로 인사이트 문장을 만든다.
    """
    if len(mention_trend) < 2:
        return None

    first_count = mention_trend[0].get("count", 0)
    last_count = mention_trend[-1].get("count", 0)

    if last_count > first_count:
        description = "최근 월 기준 핵심 키워드 언급량이 증가하는 흐름을 보입니다."
    elif last_count < first_count:
        description = "최근 월 기준 핵심 키워드 언급량이 감소하는 흐름을 보입니다."
    else:
        description = "최근 월 기준 핵심 키워드 언급량이 비교적 유지되는 흐름을 보입니다."

    return {
        "title": "언급량 추이 분석",
        "description": description,
    }
