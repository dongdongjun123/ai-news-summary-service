<script setup>
import { computed } from 'vue'

const props = defineProps({
  news: { type: Object, default: null },
})
const emit = defineEmits(['close'])

// 주차 레이블 (4주)
const weekLabels = ['1주차', '2주차', '3주차', '4주차']

// SVG 차트 설정
const chartWidth  = 560
const chartHeight = 220
const padL = 56, padR = 28, padT = 24, padB = 40

const points = computed(() => {
  if (!props.news) return []
  const data = props.news.mention_trend
  const maxVal = Math.max(...data)
  const minVal = Math.min(...data)
  const range  = maxVal - minVal || 1
  const xs = data.map((_, i) =>
    padL + (i / (data.length - 1)) * (chartWidth - padL - padR)
  )
  const ys = data.map(v =>
    padT + (1 - (v - minVal) / range) * (chartHeight - padT - padB)
  )
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
  const mid = Math.round((maxVal + minVal) / 2)
  return [
    { label: maxVal.toLocaleString(), y: padT },
    { label: mid.toLocaleString(),    y: padT + (chartHeight - padT - padB) / 2 },
    { label: minVal.toLocaleString(), y: chartHeight - padB },
  ]
})

// 가장 많이 언급된 주차 찾기
const peakWeek = computed(() => {
  if (!props.news) return 0
  const data = props.news.mention_trend
  return data.indexOf(Math.max(...data))
})

const badgeStyle = computed(() => {
  const map = {
    IT과학: { bg: '#eff6ff', text: '#2563eb' },
    경제:   { bg: '#f0fdf4', text: '#16a34a' },
    정치:   { bg: '#fefce8', text: '#b45309' },
    사회:   { bg: '#fff1f2', text: '#be123c' },
    문화:   { bg: '#faf5ff', text: '#7e22ce' },
    국제:   { bg: '#f0f9ff', text: '#0369a1' },
    지역:   { bg: '#fff7ed', text: '#c2410c' },
    스포츠: { bg: '#f0fdf4', text: '#166534' },
  }
  const c = map[props.news?.category] ?? { bg: '#f3f4f6', text: '#374151' }
  return { backgroundColor: c.bg, color: c.text }
})

// 핵심 키워드 (첫 번째)
const topKeyword = computed(() => props.news?.related_keywords?.[0] ?? '')

// 중요도 점수 (더미: mention_trend 합산 기반 0~100)
const importanceScore = computed(() => {
  if (!props.news) return 0
  const total = props.news.mention_trend.reduce((a, b) => a + b, 0)
  return Math.min(Math.round(total / 120), 100)
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
    <Transition name="modal">
      <div v-if="news" class="backdrop" @click="onBackdrop">
        <div class="modal" role="dialog" aria-modal="true">

          <!-- 헤더 -->
          <div class="modal-header">
            <div class="header-meta">
              <span class="badge" :style="badgeStyle">{{ news.category }}</span>
              <span class="header-source">{{ news.source }}</span>
              <span class="header-dot">·</span>
              <span class="header-date">{{ formatDate(news.published_at) }}</span>
            </div>
            <button class="close-btn" @click="emit('close')" aria-label="닫기">✕</button>
          </div>

          <h2 class="modal-title">{{ news.title }}</h2>

          <!-- 스크롤 본문 -->
          <div class="modal-scroll">

            <!-- AI 요약 -->
            <section class="panel">
              <div class="panel-label">
                <span class="panel-icon">🤖</span> AI 요약
              </div>
              <p class="summary-text">{{ news.summary }}</p>
            </section>

            <!-- 언급량 추이 -->
            <section class="panel">
              <div class="panel-label-row">
                <div class="panel-label">
                  <span class="panel-icon">📈</span> 언급량 추이 (최근 4주)
                </div>
                <span class="chart-unit">단위: 건</span>
              </div>

              <svg :viewBox="`0 0 ${chartWidth} ${chartHeight}`" class="chart-svg">
                <!-- 그라디언트 정의 -->
                <defs>
                  <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#6366f1" stop-opacity="0.15"/>
                    <stop offset="100%" stop-color="#6366f1" stop-opacity="0.01"/>
                  </linearGradient>
                </defs>

                <!-- Y축 눈금선 -->
                <g v-for="tick in yTicks" :key="tick.y">
                  <line
                    :x1="padL" :y1="tick.y"
                    :x2="chartWidth - padR" :y2="tick.y"
                    stroke="#f0f0f8" stroke-width="1.5"
                  />
                  <text
                    :x="padL - 10" :y="tick.y + 4"
                    text-anchor="end" font-size="11" fill="#9ca3af"
                  >{{ tick.label }}</text>
                </g>

                <!-- X축 레이블 -->
                <text
                  v-for="(p, i) in points" :key="'xl'+i"
                  :x="p.x" :y="chartHeight - 10"
                  text-anchor="middle" font-size="12" fill="#9ca3af"
                >{{ weekLabels[i] }}</text>

                <!-- 채우기 영역 -->
                <polygon
                  v-if="points.length"
                  :points="`${points[0].x},${chartHeight - padB} ${polyline} ${points[points.length-1].x},${chartHeight - padB}`"
                  fill="url(#areaGrad)"
                />

                <!-- 꺾은선 -->
                <polyline
                  v-if="points.length"
                  :points="polyline"
                  fill="none" stroke="#6366f1" stroke-width="2.5"
                  stroke-linejoin="round" stroke-linecap="round"
                />

                <!-- 포인트 -->
                <g v-for="(p, i) in points" :key="'pt'+i">
                  <!-- 피크 주차 강조 -->
                  <circle v-if="i === peakWeek"
                    :cx="p.x" :cy="p.y" r="8"
                    fill="#6366f1" fill-opacity="0.15"
                  />
                  <circle
                    :cx="p.x" :cy="p.y" r="5"
                    :fill="i === peakWeek ? '#6366f1' : '#818cf8'"
                    stroke="#fff" stroke-width="2"
                  />
                  <text
                    :x="p.x" :y="p.y - 12"
                    text-anchor="middle" font-size="11"
                    :fill="i === peakWeek ? '#4f46e5' : '#818cf8'"
                    :font-weight="i === peakWeek ? '700' : '500'"
                  >{{ p.val.toLocaleString() }}</text>
                </g>
              </svg>
            </section>

            <!-- 연관어 분석 -->
            <section class="panel">
              <div class="panel-label">
                <span class="panel-icon">🔗</span> 연관어 분석
              </div>

              <div class="keyword-layout">
                <!-- 핵심 키워드 카드 -->
                <div class="kw-main">
                  <div class="kw-main-label">핵심 키워드</div>
                  <div class="kw-main-word">{{ topKeyword }}</div>
                  <div class="kw-score-label">중요도 점수</div>
                  <div class="kw-score">{{ importanceScore }}<span>/100</span></div>
                </div>

                <!-- 연관어 태그들 -->
                <div class="kw-tags">
                  <span
                    v-for="(kw, i) in news.related_keywords"
                    :key="kw"
                    class="kw-tag"
                    :style="{
                      fontSize: `${15 - i * 0.8}px`,
                      opacity: Math.max(1 - i * 0.08, 0.4),
                      fontWeight: i < 3 ? '700' : '500',
                    }"
                  >{{ kw }}</span>
                </div>

                <!-- 연관어 랭킹 -->
                <div class="kw-ranking">
                  <div class="ranking-title">연관어 랭킹 <span>(중요도 순)</span></div>
                  <div
                    v-for="(kw, i) in news.related_keywords.slice(0, 6)"
                    :key="'r'+kw"
                    class="ranking-row"
                  >
                    <span class="rank-num">{{ i + 1 }}</span>
                    <span class="rank-word">{{ kw }}</span>
                    <div class="rank-bar-wrap">
                      <div
                        class="rank-bar"
                        :style="{ width: `${100 - i * 13}%` }"
                      ></div>
                    </div>
                    <span class="rank-score">{{ 90 - i * 11 }}</span>
                  </div>
                </div>
              </div>
            </section>

          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* 트랜지션 */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.2s;
}
.modal-enter-active .modal, .modal-leave-active .modal {
  transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.2s;
}
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal { transform: scale(0.95) translateY(10px); opacity: 0; }

.backdrop {
  position: fixed; inset: 0;
  background: rgba(15, 15, 40, 0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
  padding: 32px;
  backdrop-filter: blur(2px);
}

.modal {
  background: #fff;
  border-radius: 20px;
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 80px rgba(30, 30, 80, 0.22);
  overflow: hidden;
}

.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 22px 28px 0;
  flex-shrink: 0;
}
.header-meta {
  display: flex; align-items: center; gap: 8px;
  flex-wrap: wrap;
}
.badge {
  font-size: 12px; font-weight: 600;
  padding: 4px 10px; border-radius: 6px;
}
.header-source { font-size: 13px; color: #374151; font-weight: 500; }
.header-dot    { color: #d1d5db; }
.header-date   { font-size: 13px; color: #9ca3af; }

.close-btn {
  background: #f9fafb; border: 1px solid #f3f4f6;
  width: 32px; height: 32px;
  border-radius: 8px;
  font-size: 15px; color: #9ca3af;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.15s; flex-shrink: 0;
}
.close-btn:hover { background: #fee2e2; border-color: #fca5a5; color: #ef4444; }

.modal-title {
  font-size: 20px; font-weight: 700; color: #111827;
  line-height: 1.5;
  padding: 14px 28px 0;
  flex-shrink: 0;
  word-break: keep-all;
}

.modal-scroll {
  overflow-y: auto;
  padding: 20px 28px 28px;
  display: flex; flex-direction: column; gap: 16px;
}
.modal-scroll::-webkit-scrollbar { width: 5px; }
.modal-scroll::-webkit-scrollbar-track { background: transparent; }
.modal-scroll::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 3px; }

.panel {
  border: 1px solid #f0f0f8;
  border-radius: 14px;
  padding: 20px;
  background: #fafafa;
}

.panel-label {
  display: flex; align-items: center; gap: 6px;
  font-size: 14px; font-weight: 700; color: #374151;
  margin-bottom: 14px;
}
.panel-label-row {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 14px;
}
.panel-label-row .panel-label { margin-bottom: 0; }
.panel-icon { font-size: 15px; }
.chart-unit { font-size: 11px; color: #9ca3af; }

.summary-text {
  font-size: 14px; color: #374151; line-height: 1.9;
}

/* 차트 */
.chart-svg {
  display: block;
  width: 100%;
  height: 220px;
}

/* 연관어 레이아웃 */
.keyword-layout {
  display: grid;
  grid-template-columns: 140px 1fr 180px;
  gap: 16px;
  align-items: start;
}

.kw-main {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 12px;
  padding: 16px;
  color: #fff;
}
.kw-main-label {
  font-size: 11px; opacity: 0.8; margin-bottom: 4px; font-weight: 500;
}
.kw-main-word {
  font-size: 20px; font-weight: 700; margin-bottom: 12px; word-break: break-all;
}
.kw-score-label {
  font-size: 11px; opacity: 0.8; margin-bottom: 2px;
}
.kw-score {
  font-size: 26px; font-weight: 700; line-height: 1;
}
.kw-score span { font-size: 13px; opacity: 0.7; margin-left: 2px; }

.kw-tags {
  display: flex; flex-wrap: wrap;
  gap: 8px 12px; align-items: center;
  align-content: center;
}
.kw-tag {
  color: #6366f1; font-weight: 600; cursor: default;
  transition: opacity 0.15s;
}
.kw-tag:hover { opacity: 1 !important; }

.kw-ranking { display: flex; flex-direction: column; gap: 6px; }
.ranking-title {
  font-size: 11px; font-weight: 600; color: #6b7280;
  margin-bottom: 4px;
}
.ranking-title span { font-weight: 400; }
.ranking-row {
  display: flex; align-items: center; gap: 6px;
}
.rank-num {
  font-size: 11px; font-weight: 700; color: #6366f1;
  width: 14px; flex-shrink: 0;
}
.rank-word {
  font-size: 12px; color: #374151; font-weight: 500;
  width: 52px; flex-shrink: 0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.rank-bar-wrap {
  flex: 1; height: 4px; background: #f3f4f6; border-radius: 2px; overflow: hidden;
}
.rank-bar {
  height: 100%; background: #a5b4fc; border-radius: 2px;
  transition: width 0.5s ease;
}
.rank-score {
  font-size: 11px; color: #9ca3af; width: 22px; text-align: right; flex-shrink: 0;
}
</style>
