<template>
  <div
    class="rounded-2xl p-5 flex items-center gap-4"
    style="background: linear-gradient(135deg, #1e1e35, #1e1e4a); border: 1px solid var(--color-surface-04)"
  >
    <!-- XP icon -->
    <div class="relative shrink-0">
      <div class="absolute inset-0 rounded-full blur-md opacity-40" style="background-color: #6366f1"></div>
      <div class="relative w-14 h-14 rounded-full flex items-center justify-center text-2xl font-black"
           style="background-color: rgba(99,102,241,0.15); border: 2px solid rgba(99,102,241,0.4); color: #818cf8">
        XP
      </div>
    </div>

    <div class="flex-1 min-w-0">
      <p class="text-xs font-semibold uppercase tracking-wider mb-1" style="color: var(--color-text-soft)">
        Tổng điểm XP
      </p>
      <div class="flex items-baseline gap-1.5">
        <span class="text-3xl font-black" style="color: var(--color-primary-400)">{{ fmtNumber(totalXP) }}</span>
        <span class="text-sm font-medium" style="color: var(--color-text-muted)">XP</span>
      </div>
      <p class="text-xs mt-1" style="color: var(--color-text-soft)">
        Hoàn thành <span class="font-semibold" style="color: var(--color-text-muted)">{{ totalExercises }}</span> bài tập
      </p>
    </div>
  </div>
</template>

<script setup>
import { fmtNumber } from '@/utils/formatters.js'

defineProps({
  totalXP: { type: Number, default: 0 },
  totalExercises: { type: Number, default: 0 },
})
</script>
