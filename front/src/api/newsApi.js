// ----------------------------------------------------------------
// newsApi.js
// 백엔드(FastAPI :8000) 호출 모듈
// ----------------------------------------------------------------

// 기본값은 127.0.0.1: Windows 등에서 localhost → IPv6(::1) 우선 해석 시
// 백엔드가 127.0.0.1 에만 바인딩되어 있으면 연결 거부 → 브라우저는 'Failed to fetch' 만 표시
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

/**
 * 전체 뉴스 목록 조회
 * GET /api/news
 */
export async function fetchNews() {
  const res = await fetch(`${BASE_URL}/api/news`)
  if (!res.ok) throw new Error('뉴스 데이터를 불러오지 못했습니다.')
  return res.json()
}

/**
 * 카테고리별 뉴스 필터링
 * GET /api/news?category=정치
 * '전체' 또는 빈 값일 때는 파라미터를 붙이지 않는다.
 */
export async function fetchNewsByCategory(category) {
  const url =
    !category || category === '전체'
      ? `${BASE_URL}/api/news`
      : `${BASE_URL}/api/news?category=${encodeURIComponent(category)}`
  const res = await fetch(url)
  if (!res.ok) throw new Error('뉴스 데이터를 불러오지 못했습니다.')
  return res.json()
}

/**
 * 단일 뉴스 상세 조회
 * GET /api/news/:id
 *   - 본문(content) + 요약(summary, 온디맨드)
 *   - mention_trend(number[4]) + related_keywords(string[]) 포함
 */
export async function fetchNewsById(id) {
  const res = await fetch(`${BASE_URL}/api/news/${encodeURIComponent(id)}`)
  if (!res.ok) throw new Error('해당 뉴스를 찾을 수 없습니다.')
  return res.json()
}
