<template>
  <div class="deck-history">
    <!-- Header -->
    <div class="flex items-center justify-between mb-3">
      <h4 class="text-xs font-semibold uppercase tracking-wider"
          style="color: var(--color-text-muted)">
        Lịch sử 14 ngày
      </h4>
      <span class="text-xs" style="color: var(--color-text-muted)">
        Tổng: {{ totalCards.toLocaleString() }} thẻ
      </span>
    </div>

    <!-- Bar chart -->
    <div v-if="loading" class="h-16 rounded-xl animate-pulse"
         style="background-color: var(--color-surface-04)"></div>

    <div v-else class="flex items-end gap-0.5" style="height: 64px">
      <div v-for="day in history" :key="day.date"
           class="flex-1 flex flex-col items-center gap-0.5 group relative">
        <!-- Tooltip -->
        <div class="absolute bottom-full mb-1 left-1/2 -translate-x-1/2 z-10
                    px-2 py-1 rounded-lg text-[10px] whitespace-nowrap pointer-events-none
                    opacity-0 group-hover:opacity-100 transition-opacity duration-150"
             style="background-color: var(--color-surface-01); color: var(--color-text-base);
                    border: 1px solid var(--color-surface-04); box-shadow: 0 4px 12px rgba(0,0,0,0.2)">
          <div class="font-semibold">{{ formatDate(day.date) }}</div>
          <div v-if="day.total_cards > 0">
            {{ day.total_cards }} thẻ · {{ day.avg_accuracy }}% chính xác
          </div>
          <div v-else style="color: var(--color-text-muted)">Không học</div>
        </div>

        <!-- Bar -->
        <div class="w-full rounded-t-sm transition-all duration-300"
             :style="{
               height: barHeight(day) + 'px',
               backgroundColor: barColor(day),
               minHeight: day.total_cards > 0 ? '3px' : '1px',
             }"></div>

        <!-- Day label -->
        <span class="text-[9px] leading-none mt-0.5"
              :style="{ color: isToday(day.date) ? 'var(--color-primary-400)' : 'var(--color-text-muted)' }">
          {{ dayLabel(day.date) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { vocabularyApi } from '@/api/vocabulary.js'

const props = defineProps({
  deckId: { type: [Number, String], required: true },
})

const history = ref([])
const loading = ref(false)

const maxCards = computed(() => Math.max(...history.value.map((d) => d.total_cards), 1))
const totalCards = computed(() => history.value.reduce((s, d) => s + d.total_cards, 0))

const BAR_MAX_H = 48 // px

function barHeight(day) {
  if (!day.total_cards) return 0
  return Math.max(Math.round((day.total_cards / maxCards.value) * BAR_MAX_H), 3)
}

function barColor(day) {
  if (!day.total_cards) return 'var(--color-surface-04)'
  const acc = day.avg_accuracy
  if (acc >= 80) return '#22c55e99'       // green — high accuracy
  if (acc >= 60) return '#3b82f699'       // blue — good accuracy
  if (acc >= 40) return '#f59e0b99'       // amber — medium
  return '#ef444499'                       // red — low accuracy
}

function isToday(dateStr) {
  return dateStr === new Date().toISOString().slice(0, 10)
}

function dayLabel(dateStr) {
  const d = new Date(dateStr)
  return String(d.getDate()).padStart(2, '0')
}

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return `${d.getDate()}/${d.getMonth() + 1}`
}

async function loadHistory() {
  loading.value = true
  try {
    const res = await vocabularyApi.getDeckHistory(props.deckId)
    const data = res.data?.data ?? res.data
    history.value = data?.history ?? []
  } catch {
    history.value = []
  } finally {
    loading.value = false
  }
}

watch(() => props.deckId, loadHistory)
onMounted(loadHistory)
</script>
