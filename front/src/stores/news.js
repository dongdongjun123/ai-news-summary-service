import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchNewsByCategory } from '@/api/newsApi'

export const useNewsStore = defineStore('news', () => {
  const newsList = ref([])
  const activeCategory = ref('전체')
  const isLoading = ref(false)
  const error = ref(null)

  // 카테고리 확장
  const CATEGORIES = ['전체', '정치', '경제', '사회', '문화', '국제', '지역', '스포츠', 'IT과학']

  const totalCount = computed(() => newsList.value.length)

  async function setCategory(category) {
    activeCategory.value = category
    await loadNews()
  }

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

  return { newsList, activeCategory, isLoading, error, CATEGORIES, totalCount, setCategory, loadNews }
})