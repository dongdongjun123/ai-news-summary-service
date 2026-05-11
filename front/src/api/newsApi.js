// ----------------------------------------------------------------
// newsApi.js
// 뉴스 데이터 fetch 담당 모듈
//
// [더미 모드] 로컬 JSON 파일을 직접 불러옴
// [실서버 연결 시] BASE_URL을 FastAPI 서버 주소로 교체하고
//   fetchNews() 내부의 import 방식을 fetch(url) 방식으로 바꾸면 됨
// ----------------------------------------------------------------

// TODO: FastAPI 연결 시 이 줄을 활성화하고 아래 더미 import 제거
// const BASE_URL = 'http://localhost:8000'

import dummyData from '@/data/dummy_news.json'

/**
 * 전체 뉴스 목록 조회
 * FastAPI 연결 시: GET /api/news
 * @returns {Promise<Array>} 뉴스 객체 배열
 */
export async function fetchNews() {
  // --- 더미 모드 ---
  return dummyData

  // --- FastAPI 연결 시 아래로 교체 ---
  // const res = await fetch(`${BASE_URL}/api/news`)
  // if (!res.ok) throw new Error('뉴스 데이터를 불러오지 못했습니다.')
  // return res.json()
}

/**
 * 카테고리별 뉴스 필터링
 * FastAPI 연결 시: GET /api/news?category=IT
 * @param {string} category - 카테고리명 ('전체' | 'IT' | '경제' | '시사' | '과학')
 * @returns {Promise<Array>}
 */
export async function fetchNewsByCategory(category) {
  const all = await fetchNews()
  if (category === '전체') return all
  return all.filter((item) => item.category === category)

  // --- FastAPI 연결 시 아래로 교체 ---
  // const url = category === '전체'
  //   ? `${BASE_URL}/api/news`
  //   : `${BASE_URL}/api/news?category=${encodeURIComponent(category)}`
  // const res = await fetch(url)
  // if (!res.ok) throw new Error('뉴스 데이터를 불러오지 못했습니다.')
  // return res.json()
}

/**
 * 단일 뉴스 상세 조회
 * FastAPI 연결 시: GET /api/news/:id
 * @param {number} id
 * @returns {Promise<Object>}
 */
export async function fetchNewsById(id) {
  const all = await fetchNews()
  return all.find((item) => item.id === id) ?? null

  // --- FastAPI 연결 시 아래로 교체 ---
  // const res = await fetch(`${BASE_URL}/api/news/${id}`)
  // if (!res.ok) throw new Error('해당 뉴스를 찾을 수 없습니다.')
  // return res.json()
}
