<script setup>
import { useNewsStore } from '@/stores/news'

const store = useNewsStore()
</script>

<template>
  <div class="stat-grid">
    <div class="stat-card">
      <div class="stat-label">📄 수집된 기사</div>
      <div class="stat-value">{{ store.totalCount }}</div>
      <div class="stat-sub">{{ store.activeCategory }} 카테고리</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">✨ AI 요약 완료</div>
      <div class="stat-value">{{ store.totalCount }}</div>
      <div class="stat-sub">처리율 100%</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">🕐 마지막 업데이트</div>
      <div class="stat-value last-update">크롤링 기준</div>
      <div class="stat-sub">수동 갱신</div>
    </div>
  </div>
</template>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
}
.stat-label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #111827;
}
.last-update {
  font-size: 16px;
  padding-top: 6px;
}
.stat-sub {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}
</style>
