<script setup>
defineProps({
  news: { type: Object, required: true },
})
const emit = defineEmits(['click'])

const badgeColor = {
  IT과학: { bg: '#eff6ff', text: '#1d4ed8' },
  경제:   { bg: '#f0fdf4', text: '#15803d' },
  정치:   { bg: '#fefce8', text: '#92400e' },
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
  <div class="news-card" @click="emit('click', news)" tabindex="0" role="button"
    @keydown.enter="emit('click', news)">
    <span class="badge" :style="getBadgeStyle(news.category)">{{ news.category }}</span>
    <h3 class="title">{{ news.title }}</h3>
    <p class="summary">{{ news.summary }}</p>
    <div class="meta">
      <span>{{ news.source }}</span>
      <span>{{ formatDate(news.published_at) }}</span>
    </div>
    <div class="more-hint">클릭해서 자세히 보기 →</div>
  </div>
</template>

<style scoped>
.news-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  display: flex; flex-direction: column; gap: 10px;
  cursor: pointer;
  transition: box-shadow 0.15s, border-color 0.15s;
}
.news-card:hover {
  box-shadow: 0 4px 16px rgba(99,102,241,0.12);
  border-color: #a5b4fc;
}
.badge {
  display: inline-block; font-size: 12px; font-weight: 500;
  padding: 3px 10px; border-radius: 20px; align-self: flex-start;
}
.title {
  font-size: 15px; font-weight: 600; color: #111827;
  line-height: 1.5; margin: 0;
}
.summary {
  font-size: 13px; color: #4b5563; line-height: 1.7; margin: 0;
  display: -webkit-box; -webkit-line-clamp: 3; line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}
.meta {
  display: flex; justify-content: space-between;
  font-size: 12px; color: #9ca3af;
  padding-top: 8px; border-top: 1px solid #f3f4f6; margin-top: auto;
}
.more-hint {
  font-size: 12px; color: #a5b4fc; text-align: right;
}
</style>