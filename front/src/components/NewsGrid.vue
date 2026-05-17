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
    <div class="section-header">
      <div class="section-title">
        <span class="title-bar"></span>
        최신 AI 요약 뉴스
      </div>
      <button class="refresh-btn" @click="store.loadNews()">
        🔄 새로고침
      </button>
    </div>

    <div v-if="store.isLoading" class="status-msg">
      <span class="loading-spinner"></span> 불러오는 중...
    </div>
    <div v-else-if="store.error" class="status-msg error">{{ store.error }}</div>
    <div v-else-if="store.newsList.length === 0" class="status-msg">
      해당 카테고리의 뉴스가 없습니다.
    </div>

    <div v-else class="grid">
      <NewsCard
        v-for="item in store.newsList"
        :key="item.id"
        :news="item"
        @click="selectedNews = item"
      />
    </div>

    <NewsModal :news="selectedNews" @close="selectedNews = null" />
  </div>
</template>

<style scoped>
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #1a1a2e;
}
.title-bar {
  display: inline-block;
  width: 4px; height: 16px;
  background: #6366f1;
  border-radius: 2px;
}
.refresh-btn {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px;
  color: #6b7280;
  background: none;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 6px 12px;
  cursor: pointer;
  transition: all 0.15s;
}
.refresh-btn:hover {
  border-color: #6366f1;
  color: #6366f1;
  background: #f5f5ff;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.status-msg {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 60px 0;
  color: #9ca3af;
  font-size: 14px;
}
.error { color: #ef4444; }

.loading-spinner {
  display: inline-block;
  width: 16px; height: 16px;
  border: 2px solid #e5e7eb;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
