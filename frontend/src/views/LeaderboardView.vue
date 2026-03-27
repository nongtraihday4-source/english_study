<template>
    <div class="p-6 max-w-2xl mx-auto">
      <h1 class="text-2xl font-bold mb-1" style="color: var(--color-text-base)">Bảng xếp hạng</h1>
      <p class="text-sm mb-6" style="color: var(--color-text-muted)">Top học viên tuần này</p>

      <!-- Period toggle -->
      <div class="flex gap-2 mb-6">
        <button v-for="p in periods" :key="p.value" @click="period = p.value"
                class="px-4 py-2 rounded-lg text-xs font-semibold transition"
                :style="period === p.value
                  ? 'background-color: var(--color-primary-600); color: white'
                  : 'background-color: var(--color-surface-03); color: var(--color-text-soft)'">
          {{ p.label }}
        </button>
      </div>

      <div v-if="loading" class="space-y-2">
        <div v-for="i in 10" :key="i" class="rounded-xl h-14 animate-pulse"
             style="background-color: var(--color-surface-02)"></div>
      </div>

      <div v-else class="space-y-2">
        <div v-for="(entry, idx) in board" :key="entry.user_id"
             class="flex items-center gap-4 p-4 rounded-xl"
             :style="`background-color: ${idx < 3 ? 'var(--color-surface-03)' : 'var(--color-surface-02)'}; border: 1px solid var(--color-surface-04)`">
          <span class="w-8 text-center font-black text-lg"
                :style="idx === 0 ? 'color: #fbbf24' : idx === 1 ? 'color: #9ca3af' : idx === 2 ? 'color: #b45309' : 'color: var(--color-text-muted)'">
            {{ idx + 1 }}
          </span>
          <div class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold text-white flex-shrink-0"
               style="background: linear-gradient(135deg, #6366f1, #8b5cf6)">
            {{ (entry.full_name || entry.username || '?')[0].toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-semibold text-sm truncate" style="color: var(--color-text-base)">
              {{ entry.full_name || entry.username }}
            </p>
            <p class="text-xs" style="color: var(--color-text-muted)">Level {{ entry.level }}</p>
          </div>
          <div class="text-right">
            <p class="font-bold text-sm" style="color: var(--color-primary-400)">{{ entry.xp?.toLocaleString('vi-VN') }} XP</p>
          </div>
        </div>

        <div v-if="board.length === 0" class="text-center py-12" style="color: var(--color-text-muted)">
          <p class="text-3xl mb-2">🏆</p>
          <p>Chưa có dữ liệu xếp hạng.</p>
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { getLeaderboard } from '@/api/gamification.js'

const periods = [
  { label: 'Tuần này', value: 'weekly' },
  { label: 'Tháng này', value: 'monthly' },
  { label: 'Tất cả', value: 'all_time' },
]
const period = ref('weekly')
const board = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await getLeaderboard({ period: period.value, limit: 50 })
    const d = res.data?.data ?? res.data
    board.value = d?.results || (Array.isArray(d) ? d : [])
  } catch {
    board.value = []
  } finally {
    loading.value = false
  }
}

watch(period, load)
onMounted(load)
</script>
