<template>
  <div
    class="rounded-2xl p-5"
    style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
  >
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm font-semibold" style="color: var(--color-text-base)">Biểu đồ kỹ năng</h3>
      <span class="text-xs px-2 py-0.5 rounded-full font-medium"
            style="background-color: var(--color-primary-900); color: var(--color-primary-300)">
        {{ levelCode }}
      </span>
    </div>

    <!-- Chart canvas -->
    <div class="relative h-56 flex items-center justify-center">
      <Radar v-if="hasData" :data="chartData" :options="chartOptions" />
      <div v-else class="text-sm text-center" style="color: var(--color-text-soft)">
        Chưa có dữ liệu điểm<br>Hãy làm bài tập để thấy biểu đồ!
      </div>
    </div>

    <!-- Legend -->
    <div class="grid grid-cols-2 gap-2 mt-4">
      <div v-for="(skill, i) in skills" :key="skill.key"
           class="flex items-center gap-2">
        <div class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ backgroundColor: colors[i] }"></div>
        <span class="text-xs truncate" style="color: var(--color-text-muted)">
          {{ skill.label }}
          <span class="font-semibold ml-1" style="color: var(--color-text-base)">
            {{ fmtScore(score[skill.key]) }}
          </span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Radar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'
import { fmtScore } from '@/utils/formatters.js'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

const props = defineProps({
  cumulativeScore: { type: Object, default: null },
})

const skills = [
  { key: 'avg_listening',  label: 'Nghe' },
  { key: 'avg_speaking',   label: 'Nói' },
  { key: 'avg_reading',    label: 'Đọc' },
  { key: 'avg_writing',    label: 'Viết' },
]

const colors = ['#6366f1', '#f97316', '#22c55e', '#eab308']

const levelCode = computed(() => props.cumulativeScore?.level_code || '—')

const score = computed(() => props.cumulativeScore || {})

const hasData = computed(() =>
  props.cumulativeScore &&
  skills.some(s => props.cumulativeScore[s.key] != null && props.cumulativeScore[s.key] > 0)
)

const chartData = computed(() => ({
  labels: skills.map(s => s.label),
  datasets: [
    {
      label: 'Điểm kỹ năng',
      data: skills.map(s => score.value[s.key] || 0),
      fill: true,
      backgroundColor: 'rgba(99, 102, 241, 0.15)',
      borderColor: '#6366f1',
      borderWidth: 2,
      pointBackgroundColor: colors,
      pointBorderColor: '#fff',
      pointHoverRadius: 6,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx) => ` ${ctx.label}: ${ctx.raw?.toLocaleString('vi-VN', { minimumFractionDigits: 1 })}`,
      },
    },
  },
  scales: {
    r: {
      min: 0,
      max: 100,
      ticks: {
        stepSize: 25,
        color: '#64748b',
        backdropColor: 'transparent',
        font: { size: 10 },
      },
      grid: { color: 'rgba(255,255,255,0.06)' },
      angleLines: { color: 'rgba(255,255,255,0.06)' },
      pointLabels: {
        color: '#94a3b8',
        font: { size: 12, weight: '600' },
      },
    },
  },
}
</script>
