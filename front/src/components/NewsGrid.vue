<script setup>
import { useNewsStore } from '@/stores/news'
import NewsCard from './NewsCard.vue'

const store = useNewsStore()
</script>

<template>
  <div>
    <!-- 로딩 -->
    <div v-if="store.isLoading" class="status-msg">불러오는 중...</div>

    <!-- 에러 -->
    <div v-else-if="store.error" class="status-msg error">
      {{ store.error }}
    </div>

    <!-- 결과 없음 -->
    <div v-else-if="store.newsList.length === 0" class="status-msg">
      해당 카테고리의 뉴스가 없습니다.
    </div>

    <!-- 뉴스 카드 그리드 -->
    <div v-else class="grid">
      <NewsCard
        v-for="item in store.newsList"
        :key="item.id"
        :news="item"
      />
    </div>
  </div>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.status-msg {
  text-align: center;
  padding: 60px 0;
  color: #9ca3af;
  font-size: 14px;
}
.error {
  color: #ef4444;
}
</style>
