<script setup>
import { useNewsStore } from '@/stores/news'

const store = useNewsStore()

const CATEGORY_ICONS = {
  '전체':  '󰕰',  // 그냥 텍스트 이모지로 대체
}

// 카테고리별 아이콘 (유니코드 이모지)
const icons = {
  '전체': '⊞',
  '정치': '🏛',
  '경제': '📊',
  '사회': '👥',
  '문화': '🎭',
  '국제': '🌐',
  '지역': '📍',
  '스포츠': '⚽',
  'IT과학': '💻',
}
</script>

<template>
  <header class="navbar">
    <div class="brand">
      <div class="brand-icon">
        <span>📰</span>
      </div>
      <div class="brand-text">
        <div class="brand-title">실시간 뉴스 요약</div>
        <div class="brand-sub">AI가 중요한 뉴스를 실시간으로 요약해드립니다</div>
      </div>
    </div>

    <nav class="tabs">
      <button
        v-for="cat in store.CATEGORIES"
        :key="cat"
        :class="['tab', { active: store.activeCategory === cat }]"
        @click="store.setCategory(cat)"
      >
        <span class="tab-icon">{{ icons[cat] }}</span>
        {{ cat }}
      </button>
    </nav>
  </header>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  gap: 32px;
  padding: 0 32px;
  height: 72px;
  background: #fff;
  border-bottom: 1px solid #f0f0f5;
  position: sticky;
  top: 0;
  z-index: 50;
  box-shadow: 0 1px 12px rgba(80, 80, 180, 0.06);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}
.brand-icon {
  width: 42px; height: 42px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(99,102,241,0.3);
}
.brand-title {
  font-size: 17px;
  font-weight: 700;
  color: #1a1a2e;
  letter-spacing: -0.3px;
}
.brand-sub {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 1px;
}

.tabs {
  display: flex;
  gap: 4px;
  overflow-x: auto;
  flex: 1;
}
.tabs::-webkit-scrollbar { display: none; }

.tab {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 14px;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: #6b7280;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.18s;
}
.tab:hover {
  background: #f5f5ff;
  color: #6366f1;
}
.tab.active {
  background: #6366f1;
  color: #fff;
  box-shadow: 0 3px 10px rgba(99,102,241,0.3);
}
.tab-icon { font-size: 14px; }
</style>
