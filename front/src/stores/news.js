import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchNewsByCategory, fetchCategories } from '@/api/newsApi'

export const useNewsStore = defineStore('news', () => {
  /** ['전체', ...백엔드 categories] — 더미 없음, 전부 DB `/api/categories` */
  const CATEGORIES = ref(['전체'])
  const newsList = ref([])
  const activeCategory = ref('전체')
  const isLoading = ref(false)
  const categoriesLoading = ref(false)
  const error = ref(null)
  const lastListFetchAt = ref(null)

  const totalCount = computed(() => newsList.value.length)

  const summarizedCount = computed(
    () => newsList.value.filter((n) => n.summary && String(n.summary).trim()).length,
  )

  const summaryProgressPercent = computed(() => {
    const t = newsList.value.length
    if (!t) return 0
    return Math.min(100, Math.round((summarizedCount.value / t) * 100))
  })

  /** 목록에 있는 기사 중 가장 늦은 published_at (ISO 문자열 비교) */
  const latestPublishedAt = computed(() => {
    const xs = newsList.value.map((n) => n.published_at).filter(Boolean)
    if (!xs.length) return ''
    return xs.reduce((a, b) => (String(a) > String(b) ? a : b))
  })

  async function loadCategories() {
    categoriesLoading.value = true
    try {
      const apiCats = await fetchCategories()
      const list = Array.isArray(apiCats) ? apiCats : []
      CATEGORIES.value = ['전체', ...list]
      if (!CATEGORIES.value.includes(activeCategory.value)) {
        activeCategory.value = '전체'
      }
    } catch (e) {
      console.error(e)
      CATEGORIES.value = ['전체']
    } finally {
      categoriesLoading.value = false
    }
  }

  async function loadNews() {
    isLoading.value = true
    error.value = null
    try {
      newsList.value = await fetchNewsByCategory(activeCategory.value)
      lastListFetchAt.value = new Date()
    } catch (e) {
      error.value = e.message
      newsList.value = []
    } finally {
      isLoading.value = false
    }
  }

  /** 홈 진입 시: 카테고리(API) → 뉴스 목록(API) */
  async function init() {
    await loadCategories()
    await loadNews()
  }

  async function setCategory(category) {
    activeCategory.value = category
    await loadNews()
  }

  return {
    CATEGORIES,
    newsList,
    activeCategory,
    isLoading,
    categoriesLoading,
    error,
    lastListFetchAt,
    totalCount,
    summarizedCount,
    summaryProgressPercent,
    latestPublishedAt,
    setCategory,
    loadNews,
    loadCategories,
    init,
  }
})
