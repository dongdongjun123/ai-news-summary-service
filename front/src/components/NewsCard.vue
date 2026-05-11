<script setup>
// 부모(NewsGrid)로부터 뉴스 1개 객체를 받음
defineProps({
  news: {
    type: Object,
    required: true,
  },
})

// 카테고리별 배지 색상
const badgeColor = {
  IT:   { bg: '#eff6ff', text: '#1d4ed8' },
  경제:  { bg: '#f0fdf4', text: '#15803d' },
  시사:  { bg: '#fefce8', text: '#92400e' },
  과학:  { bg: '#faf5ff', text: '#7e22ce' },
}

function getBadgeStyle(category) {
  const color = badgeColor[category] ?? { bg: '#f3f4f6', text: '#374151' }
  return {
    backgroundColor: color.bg,
    color: color.text,
  }
}

// "2025-06-01T09:12:00" → "2025.06.01 09:12" 포맷
function formatDate(dateStr) {
  const d = new Date(dateStr)
  const ymd = `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
  const hm  = `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  return `${ymd} ${hm}`
}
</script>

<template>
  <div class="news-card">
    <!-- 카테고리 배지 -->
    <span class="badge" :style="getBadgeStyle(news.category)">
      {{ news.category }}
    </span>

    <!-- 제목 -->
    <h3 class="title">{{ news.title }}</h3>

    <!-- AI 요약 본문 -->
    <p class="summary">{{ news.summary }}</p>

    <!-- 하단 메타 -->
    <div class="meta">
      <span class="source">{{ news.source }}</span>
      <span class="date">{{ formatDate(news.published_at) }}</span>
    </div>
  </div>
</template>

<style scoped>
.news-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: box-shadow 0.15s;
}
.news-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
.badge {
  display: inline-block;
  font-size: 12px;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: 20px;
  align-self: flex-start;
}
.title {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  line-height: 1.5;
  margin: 0;
}
.summary {
  font-size: 13px;
  color: #4b5563;
  line-height: 1.7;
  margin: 0;
}
.meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #9ca3af;
  margin-top: auto;
  padding-top: 8px;
  border-top: 1px solid #f3f4f6;
}
</style>
