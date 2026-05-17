# stat Summary Contract

## 1. 목적

stat-summary 모듈은 뉴스 본문을 기반으로 프론트 뉴스 상세 화면에 필요한 통계 분석 결과를 생성한다.

여기서는 본문 요약을 담당하지 않는다.  
통계량, 키워드, 연관어, 언급량 추이, 인사이트 생성을 담당한다.

---

## 2. 백엔드 호출 방식

```python
from stat_summary.analyzer import analyze_article_statistics

result = analyze_article_statistics(
    article=selected_article,
    corpus_articles=all_articles,
    top_n=5,
    recent_n=4,
)