<script setup>
import { computed } from 'vue'
import { useNewsStore } from '@/stores/news'
import { formatPublishedDate } from '@/utils/formatPublishedDate'

const store = useNewsStore()

const ringCirc = 2 * Math.PI * 26
const ringDashOffset = computed(
  () => ringCirc * (1 - store.thumbnailPercent / 100),
)

const latestPublishedLabel = computed(() =>
  store.latestPublishedAt ? formatPublishedDate(store.latestPublishedAt) : '—',
)

const listRefreshedLabel = computed(() => {
  if (!store.lastListFetchAt) return '—'
  return new Intl.DateTimeFormat('ko-KR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(store.lastListFetchAt)
})
</script>

<template>
  <div class="stat-grid">
    <!-- 수집된 기사 -->
    <div class="stat-card card-blue">
      <div class="card-inner">
        <div class="stat-icon">📄</div>
        <div class="stat-info">
          <div class="stat-label">수집된 기사</div>
          <div class="stat-value">{{ store.totalCount }}</div>
          <div class="stat-sub">
            {{ store.activeCategory === '전체' ? '전체 카테고리' : `${store.activeCategory} · API 목록` }}
          </div>
        </div>
      </div>
      <div class="card-deco">
        <div class="deco-circle c1"></div>
        <div class="deco-circle c2"></div>
      </div>
    </div>

    <!-- 썸네일(image_url) 보유 -->
    <div class="stat-card card-purple">
      <div class="card-inner">
        <div class="stat-icon">🖼️</div>
        <div class="stat-info">
          <div class="stat-label">이미지 있는 기사</div>
          <div class="stat-value">{{ store.thumbnailCount }}</div>
          <div class="stat-sub">표시 목록 중 비율 {{ store.thumbnailPercent }}%</div>
        </div>
        <div class="ring-wrap">
          <svg width="64" height="64" viewBox="0 0 64 64">
            <circle
              cx="32"
              cy="32"
              r="26"
              fill="none"
              stroke="rgba(255,255,255,0.2)"
              stroke-width="6"
            />
            <circle
              cx="32"
              cy="32"
              r="26"
              fill="none"
              stroke="#fff"
              stroke-width="6"
              :stroke-dasharray="ringCirc"
              :stroke-dashoffset="ringDashOffset"
              stroke-linecap="round"
              transform="rotate(-90 32 32)"
            />
            <text
              x="32"
              y="37"
              text-anchor="middle"
              font-size="11"
              font-weight="700"
              fill="#fff"
            >{{ store.thumbnailPercent }}%</text>
          </svg>
        </div>
      </div>
      <div class="card-deco">
        <div class="deco-circle c1"></div>
        <div class="deco-circle c2"></div>
      </div>
    </div>

    <!-- 목록 기준 최신 발행일 + 마지막 fetch -->
    <div class="stat-card card-violet">
      <div class="card-inner">
        <div class="stat-icon">🕐</div>
        <div class="stat-info">
          <div class="stat-label">목록 내 최신 발행일</div>
          <div class="stat-value sm">{{ latestPublishedLabel }}</div>
          <div class="stat-sub">목록 갱신 시각 {{ listRefreshedLabel }}</div>
        </div>
      </div>
      <div class="card-deco">
        <div class="deco-circle c1"></div>
        <div class="deco-circle c2"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}

.stat-card {
  border-radius: 16px;
  padding: 24px;
  position: relative;
  overflow: hidden;
  color: #fff;
  min-height: 120px;
}
.card-blue {
  background: linear-gradient(135deg, #4f6ef7, #6366f1);
}
.card-purple {
  background: linear-gradient(135deg, #7c3aed, #a855f7);
}
.card-violet {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
}

.card-inner {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  position: relative;
  z-index: 1;
}

.stat-icon {
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.stat-label {
  font-size: 12px;
  opacity: 0.85;
  margin-bottom: 4px;
  font-weight: 500;
}
.stat-value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}
.stat-value.sm {
  font-size: 18px;
  padding-top: 6px;
}
.stat-sub {
  font-size: 11px;
  opacity: 0.75;
}

.ring-wrap {
  margin-left: auto;
  flex-shrink: 0;
}

.card-deco {
  position: absolute;
  inset: 0;
  z-index: 0;
}
.deco-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.07);
}
.c1 {
  width: 120px;
  height: 120px;
  right: -30px;
  top: -30px;
}
.c2 {
  width: 80px;
  height: 80px;
  right: 50px;
  bottom: -20px;
}
</style>
