<template>
  <div
    class="rounded-2xl p-5"
    style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
  >
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm font-semibold" style="color: var(--color-text-base)">Kết quả gần đây</h3>
      <span class="text-xs" style="color: var(--color-text-soft)">{{ results.length }} bài</span>
    </div>

    <div v-if="results.length === 0" class="py-8 text-center text-sm" style="color: var(--color-text-soft)">
      Chưa có kết quả nào.
    </div>

    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr style="color: var(--color-text-soft)">
            <th class="text-left pb-2 text-xs font-semibold uppercase tracking-wide">Kỹ năng</th>
            <th class="text-right pb-2 text-xs font-semibold uppercase tracking-wide">Điểm</th>
            <th class="text-right pb-2 text-xs font-semibold uppercase tracking-wide">Trạng thái</th>
            <th class="text-right pb-2 text-xs font-semibold uppercase tracking-wide">Thời gian</th>
          </tr>
        </thead>
        <tbody class="divide-y" style="--tw-divide-opacity:1; border-color: var(--color-surface-04)">
          <tr v-for="r in results" :key="r.id" class="hover:opacity-80 transition">
            <td class="py-2.5">
              <span class="flex items-center gap-2">
                <span class="text-base">{{ skillIcon(r.exercise_type) }}</span>
                <span style="color: var(--color-text-base)">{{ skillLabel(r.exercise_type) }}</span>
              </span>
            </td>
            <td class="py-2.5 text-right font-bold"
                :style="{ color: r.passed ? '#22c55e' : '#ef4444' }">
              {{ r.score_display || fmtScore(r.score) }}
            </td>
            <td class="py-2.5 text-right">
              <span
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
                :style="r.passed
                  ? 'background-color:rgba(34,197,94,0.15); color:#22c55e'
                  : 'background-color:rgba(239,68,68,0.15); color:#ef4444'"
              >
                {{ r.passed ? '✓ Đạt' : '✗ Chưa đạt' }}
              </span>
            </td>
            <td class="py-2.5 text-right text-xs" style="color: var(--color-text-soft)">
              {{ fmtRelative(r.created_at) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { fmtScore, fmtRelative } from '@/utils/formatters.js'

defineProps({
  results: { type: Array, default: () => [] },
})

const SKILL_MAP = {
  listening:  { label: 'Nghe',     icon: '🎧' },
  speaking:   { label: 'Nói',      icon: '🎤' },
  reading:    { label: 'Đọc',      icon: '📖' },
  writing:    { label: 'Viết',     icon: '✍️' },
  grammar:    { label: 'Ngữ pháp', icon: '📚' },
  vocabulary: { label: 'Từ vựng',  icon: '🔤' },
}

function skillLabel(type) { return SKILL_MAP[type]?.label || type }
function skillIcon(type)  { return SKILL_MAP[type]?.icon  || '📝' }
</script>
