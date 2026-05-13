<script setup>
import { ref } from 'vue'
import { useNewsStore } from '@/stores/news'
import NewsCard from './NewsCard.vue'
import NewsModal from './NewsModal.vue'

const store = useNewsStore()
const selectedNews = ref(null)
</script>

<template>
  <div>
    <div v-if="store.isLoading" class="status-msg">불러오는 중...</div>
    <div v-else-if="store.error" class="status-msg error">{{ store.error }}</div>
    <div v-else-if="store.newsList.length === 0" class="status-msg">해당 카테고리의 뉴스가 없습니다.</div>
    <div v-else class="grid">
      <NewsCard
        v-for="item in store.newsList"
        :key="item.id"
        :news="item"
        @click="selectedNews = item"
      />
    </div>

    <!-- 모달 -->
    <NewsModal :news="selectedNews" @close="selectedNews = null" />
  </div>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.status-msg { text-align: center; padding: 60px 0; color: #9ca3af; font-size: 14px; }
.error { color: #ef4444; }
</style>