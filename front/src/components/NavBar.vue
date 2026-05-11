<script setup>
import { useNewsStore } from '@/stores/news'

const store = useNewsStore()
</script>

<template>
  <nav class="navbar">
    <div class="brand">실시간 뉴스 요약</div>
    <div class="tabs">
      <button
        v-for="cat in store.CATEGORIES"
        :key="cat"
        :class="['tab', { active: store.activeCategory === cat }]"
        @click="store.setCategory(cat)"
      >
        {{ cat }}
      </button>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
}
.brand {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}
.tabs {
  display: flex;
  gap: 8px;
}
.tab {
  padding: 6px 16px;
  border-radius: 20px;
  border: 1px solid #e5e7eb;
  background: transparent;
  color: #6b7280;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.15s;
}
.tab:hover {
  border-color: #6366f1;
  color: #6366f1;
}
.tab.active {
  background: #6366f1;
  border-color: #6366f1;
  color: #fff;
  font-weight: 500;
}
</style>
