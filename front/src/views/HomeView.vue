<script setup>
import { onMounted } from 'vue'
import { useNewsStore } from '@/stores/news'
import NavBar from '@/components/NavBar.vue'
import StatCards from '@/components/StatCards.vue'
import NewsGrid from '@/components/NewsGrid.vue'

const store = useNewsStore()

// 페이지 진입 시 뉴스 최초 로드
onMounted(() => {
  store.loadNews()
})
</script>

<template>
  <div>
    <NavBar />
    <main class="container">
      <StatCards />
      <h2 class="section-title">최신 AI 요약 뉴스</h2>
      <NewsGrid />
    </main>
  </div>
</template>

<style scoped>
.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 24px;
}
.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 16px;
}
</style>
