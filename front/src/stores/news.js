// ----------------------------------------------------------------
// stores/news.js  (Pinia)
// 뉴스 데이터 & 카테고리 상태 전역 관리
// ----------------------------------------------------------------

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchNewsByCategory } from '@/api/newsApi'

export const useNewsStore = defineStore('news', () => {
  // ── 상태 ──────────────────────────────────────────────────────
  const newsList = ref([])          // 현재 카테고리의 뉴스 목록
  const activeCategory = ref('전체') // 선택된 카테고리
  const isLoading = ref(false)
  const error = ref(null)

  const CATEGORIES = ['전체', 'IT', '경제', '시사', '과학']

  // ── 계산 속성 ─────────────────────────────────────────────────
  // 수집된 전체 기사 수 (카테고리 무관)
  const totalCount = computed(() => newsList.value.length)

  // ── 액션 ──────────────────────────────────────────────────────
  /**
   * 카테고리를 바꾸고 뉴스를 다시 불러옴
   * @param {string} category
   */
  async function setCategory(category) {
    activeCategory.value = category
    await loadNews()
  }

  /**
   * 현재 activeCategory 기준으로 뉴스 로드
   */
  async function loadNews() {
    isLoading.value = true
    error.value = null
    try {
      newsList.value = await fetchNewsByCategory(activeCategory.value)
    } catch (e) {
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }

  return {
    newsList,
    activeCategory,
    isLoading,
    error,
    CATEGORIES,
    totalCount,
    setCategory,
    loadNews,
  }
})
