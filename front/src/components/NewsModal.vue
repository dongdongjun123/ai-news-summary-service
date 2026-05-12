<script setup>
import { computed } from 'vue'

const props = defineProps({
  news: { type: Object, default: null },
})
const emit = defineEmits(['close'])

const monthLabels = ['2월', '3월', '4월', '5월']

const chartWidth  = 520
const chartHeight = 200
const padL = 52, padR = 24, padT = 20, padB = 36

const points = computed(() => {
  if (!props.news) return []
  const data = props.news.mention_trend
  const maxVal = Math.max(...data)
  const minVal = Math.min(...data)
  const range  = maxVal - minVal || 1
  const xs = data.map((_, i) => padL + (i / (data.length - 1)) * (chartWidth - padL - padR))
  const ys = data.map(v => padT + (1 - (v - minVal) / range) * (chartHeight - padT - padB))
  return data.map((v, i) => ({ x: xs[i], y: ys[i], val: v }))
})

const polyline = computed(() =>
  points.value.map(p => `${p.x},${p.y}`).join(' ')
)

const yTicks = computed(() => {
  if (!props.news) return []
  const data = props.news.mention_trend
  const maxVal = Math.max(...data)
  const minVal = Math.min(...data)
  return [
    { label: maxVal.toLocaleString(), y: padT },
    { label: Math.round((maxVal + minVal) / 2).toLocaleString(), y: padT + (chartHeight - padT - padB) / 2 },
    { label: minVal.toLocaleString(), y: chartHeight - padB },
  ]
})

const badgeStyle = computed(() => {
  const map = {
    IT과학: { bg: '#eff6ff', text: '#1d4ed8' },
    경제:   { bg: '#f0fdf4', text: '#15803d' },
    정치:   { bg: '#fefce8', text: '#92400e' },
    사회:   { bg: '#fff1f2', text: '#be123c' },
    문화:   { bg: '#faf5ff', text: '#7e22ce' },
    국제:   { bg: '#f0f9ff', text: '#0369a1' },
    지역:   { bg: '#fff7ed', text: '#c2410c' },
    스포츠: { bg: '#f0fdf4', text: '#166534' },
  }
  const c = map[props.news?.category] ?? { bg: '#f3f4f6', text: '#374151' }
  return { backgroundColor: c.bg, color: c.text }
})

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return `${d.getFullYear()}.${String(d.getMonth()+1).padStart(2,'0')}.${String(d.getDate()).padStart(2,'0')}`
}

function onBackdrop(e) {
  if (e.target === e.currentTarget) emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="news" class="backdrop" @click="onBackdrop">
      <div class="modal" role="dialog" aria-modal="true">

        <!-- 헤더 -->
        <div class="modal-header">
          <div class="header-left">
            <span class="badge" :style="badgeStyle">{{ news.category }}</span>
            <span class="source-date">{{ news.source }} · {{ formatDate(news.published_at) }}</span>
          </div>
          <button class="close-btn" @click="emit('close')" aria-label="닫기">✕</button>
        </div>

        <!-- 제목 -->
        <h2 class="modal-title">{{ news.title }}</h2>

        <!-- 스크롤 영역 -->
        <div class="modal-scroll">

          <!-- AI 요약 -->
          <section class="panel">
            <div class="panel-label">🤖 AI 요약</div>
            <p class="summary-text">{{ news.summary }}</p>
          </section>

          <!-- 언급량 추이 -->
          <section class="panel">
            <div class="panel-label">📈 언급량 추이 (최근 4개월)</div>
            <svg :viewBox="`0 0 ${chartWidth} ${chartHeight}`" class="chart-svg">
              <!-- 가로 눈금선 + Y레이블 -->
              <g v-for="tick in yTicks" :key="tick.y">
                <line :x1="padL" :y1="tick.y" :x2="chartWidth - padR" :y2="tick.y"
                  stroke="#e5e7eb" stroke-width="1" stroke-dasharray="5 4"/>
                <text :x="padL - 8" :y="tick.y + 4"
                  text-anchor="end" font-size="11" fill="#9ca3af">{{ tick.label }}</text>
              </g>

              <!-- X 레이블 -->
              <text v-for="(p, i) in points" :key="'xl'+i"
                :x="p.x" :y="chartHeight - 8"
                text-anchor="middle" font-size="12" fill="#6b7280">
                {{ monthLabels[i] }}
              </text>

              <!-- 채우기 -->
              <polygon
                v-if="points.length"
                :points="`${points[0].x},${chartHeight - padB} ${polyline} ${points[points.length-1].x},${chartHeight - padB}`"
                fill="#6366f1" fill-opacity="0.08"
              />

              <!-- 꺾은선 -->
              <polyline v-if="points.length" :points="polyline"
                fill="none" stroke="#6366f1" stroke-width="2.5" stroke-linejoin="round"/>

              <!-- 포인트 + 값 레이블 -->
              <g v-for="(p, i) in points" :key="'pt'+i">
                <circle :cx="p.x" :cy="p.y" r="5" fill="#6366f1" stroke="#fff" stroke-width="2"/>
                <text :x="p.x" :y="p.y - 10"
                  text-anchor="middle" font-size="11" fill="#4f46e5" font-weight="600">
                  {{ p.val.toLocaleString() }}
                </text>
              </g>
            </svg>
          </section>

          <!-- 연관어 분석 -->
          <section class="panel">
            <div class="panel-label">🔗 연관어 분석</div>
            <div class="keywords">
              <span
                v-for="(kw, i) in news.related_keywords"
                :key="kw"
                class="kw"
                :style="{ fontSize: `${18 - i}px`, opacity: Math.max(1 - i * 0.07, 0.4) }"
              >
                {{ kw }}
              </span>
            </div>
          </section>

        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.backdrop {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
  padding: 32px;
}
.modal {
  background: #fff;
  border-radius: 16px;
  width: 100%;
  max-width: 680px;
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 24px 28px 0;
  flex-shrink: 0;
}
.header-left {
  display: flex; align-items: center; gap: 10px;
}
.badge {
  font-size: 12px; font-weight: 500;
  padding: 4px 12px; border-radius: 20px;
  white-space: nowrap;
}
.source-date {
  font-size: 13px; color: #9ca3af;
}
.close-btn {
  background: none; border: none;
  font-size: 18px; color: #9ca3af;
  cursor: pointer; padding: 4px 8px; border-radius: 6px;
  flex-shrink: 0;
}
.close-btn:hover { background: #f3f4f6; color: #374151; }

.modal-title {
  font-size: 20px; font-weight: 700; color: #111827;
  line-height: 1.5;
  padding: 14px 28px 0;
  flex-shrink: 0;
}

/* 스크롤 영역 */
.modal-scroll {
  overflow-y: auto;
  padding: 20px 28px 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.modal-scroll::-webkit-scrollbar { width: 6px; }
.modal-scroll::-webkit-scrollbar-track { background: transparent; }
.modal-scroll::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }

.panel {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
}
.panel-label {
  font-size: 14px; font-weight: 600; color: #374151;
  margin-bottom: 14px;
}
.summary-text {
  font-size: 14px; color: #4b5563; line-height: 1.85;
}

/* 차트 — 세로로 충분히 크게 */
.chart-svg {
  display: block;
  width: 100%;
  height: 200px;
}

.keywords {
  display: flex; flex-wrap: wrap;
  gap: 10px 14px; align-items: center;
  min-height: 80px;
}
.kw {
  color: #6366f1; font-weight: 600; cursor: default;
  transition: opacity 0.15s;
}
.kw:hover { opacity: 1 !important; text-decoration: underline; }
</style>