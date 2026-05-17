<script setup>
import { onMounted } from 'vue'
import { useNewsStore } from '@/stores/news'
import NavBar from '@/components/NavBar.vue'
import StatCards from '@/components/StatCards.vue'
import NewsGrid from '@/components/NewsGrid.vue'

const store = useNewsStore()

onMounted(() => {
  store.loadNews()
})
</script>

<template>
  <div class="page">
    <NavBar />
    <main class="container">
      <StatCards />
      <NewsGrid />
    </main>

    <!-- 하단 알림 배너 -->
    <div class="banner">
      <div class="banner-inner">
        <div class="banner-left">
          <span class="banner-icon">🔔</span>
          <div>
            <div class="banner-title">관심 뉴스만 놓치지 마세요</div>
            <div class="banner-sub">관심 카테고리와 키워드를 설정하면 실시간 알림을 받아볼 수 있어요.</div>
          </div>
        </div>
        <button class="banner-btn">알림 설정하기 →</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f7f7fc;
}
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 28px 28px 40px;
  width: 100%;
  flex: 1;
}

/* 하단 배너 */
.banner {
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  padding: 0 28px;
}
.banner-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 0;
  gap: 16px;
}
.banner-left {
  display: flex; align-items: center; gap: 14px;
}
.banner-icon {
  font-size: 24px;
  background: rgba(255,255,255,0.15);
  width: 44px; height: 44px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.banner-title {
  font-size: 14px; font-weight: 700; color: #fff; margin-bottom: 2px;
}
.banner-sub {
  font-size: 12px; color: rgba(255,255,255,0.75);
}
.banner-btn {
  background: #fff;
  color: #4f46e5;
  font-size: 13px; font-weight: 700;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  white-space: nowrap;
  transition: transform 0.15s, box-shadow 0.15s;
  flex-shrink: 0;
}
.banner-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
</style>
