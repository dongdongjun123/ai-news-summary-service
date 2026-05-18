<script setup>
defineProps({
  news: { type: Object, required: true },
})
const emit = defineEmits(['click'])

const badgeColor = {
  IT과학: { bg: '#eff6ff', text: '#2563eb' },
  경제:   { bg: '#f0fdf4', text: '#16a34a' },
  정치:   { bg: '#fefce8', text: '#b45309' },
  사회:   { bg: '#fff1f2', text: '#be123c' },
  문화:   { bg: '#faf5ff', text: '#7e22ce' },
  국제:   { bg: '#f0f9ff', text: '#0369a1' },
  지역:   { bg: '#fff7ed', text: '#c2410c' },
  스포츠: { bg: '#f0fdf4', text: '#166534' },
}

function getBadgeStyle(cat) {
  const c = badgeColor[cat] ?? { bg: '#f3f4f6', text: '#374151' }
  return { backgroundColor: c.bg, color: c.text }
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return `${d.getFullYear()}.${String(d.getMonth()+1).padStart(2,'0')}.${String(d.getDate()).padStart(2,'0')}`
}
</script>

<template>
  <div
    class="news-card"
    @click="emit('click', news)"
    tabindex="0"
    role="button"
    @keydown.enter="emit('click', news)"
  >
    <div class="card-content">
      <div class="card-text">
        <span class="badge" :style="getBadgeStyle(news.category)">{{ news.category }}</span>
        <h3 class="title">{{ news.title }}</h3>
        <p class="summary">{{ news.summary }}</p>
      </div>
      <div v-if="news.thumbnail" class="card-thumb">
        <img :src="news.thumbnail" :alt="news.title" />
      </div>
    </div>

    <div class="meta">
      <div class="meta-left">
        <span class="source-dot"></span>
        <span class="source">{{ news.source }}</span>
      </div>
      <div class="meta-right">
        <span class="date">{{ formatDate(news.published_at) }}</span>
        <span class="bookmark">🔖</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.news-card {
  background: #fff;
  border: 1px solid #f0f0f5;
  border-radius: 14px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  cursor: pointer;
  transition: box-shadow 0.18s, transform 0.18s, border-color 0.18s;
}
.news-card:hover {
  box-shadow: 0 6px 24px rgba(99, 102, 241, 0.1);
  border-color: #c7d2fe;
  transform: translateY(-2px);
}

.card-content {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}
.card-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}
.card-thumb {
  width: 90px;
  height: 70px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background: #f3f4f6;
}
.card-thumb img {
  width: 100%; height: 100%;
  object-fit: cover;
}

.badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 6px;
  align-self: flex-start;
  letter-spacing: 0.2px;
}
.title {
  font-size: 15px;
  font-weight: 700;
  color: #111827;
  line-height: 1.5;
  margin: 0;
  word-break: keep-all;
}
.summary {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.7;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
}
.meta-left {
  display: flex; align-items: center; gap: 6px;
}
.source-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #6366f1;
}
.source {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}
.meta-right {
  display: flex; align-items: center; gap: 10px;
}
.date {
  font-size: 12px;
  color: #9ca3af;
}
.bookmark {
  font-size: 13px;
  opacity: 0.4;
  cursor: pointer;
  transition: opacity 0.15s;
}
.bookmark:hover { opacity: 1; }
</style>
