<template>
  <div
    class="rounded-2xl p-5"
    style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
  >
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm font-semibold" style="color: var(--color-text-base)">Khoá học đang học</h3>
      <RouterLink to="/courses" class="text-xs font-medium transition hover:opacity-80"
                  style="color: var(--color-primary-400)">Xem tất cả →</RouterLink>
    </div>

    <div v-if="courses.length === 0" class="py-8 text-center text-sm" style="color: var(--color-text-soft)">
      Bạn chưa đăng ký khoá học nào.
      <RouterLink to="/courses" class="block mt-2 font-medium" style="color: var(--color-primary-400)">
        Khám phá khoá học →
      </RouterLink>
    </div>

    <div v-else class="space-y-4">
      <div v-for="c in courses" :key="c.id" class="group">
        <div class="flex items-center justify-between mb-1">
          <p class="text-sm font-medium truncate" style="color: var(--color-text-base)">
            {{ c.course_title }}
          </p>
          <span class="text-xs shrink-0 ml-2 font-semibold" style="color: var(--color-primary-400)">
            {{ fmtPercent(c.progress_percent) }}
          </span>
        </div>

        <!-- Progress bar -->
        <div class="w-full h-2 rounded-full overflow-hidden" style="background-color: var(--color-surface-04)">
          <div
            class="h-full rounded-full transition-all duration-700"
            :style="{
              width: `${c.progress_percent || 0}%`,
              background: progressGradient(c.progress_percent),
            }"
          ></div>
        </div>

        <p class="text-xs mt-1" style="color: var(--color-text-soft)">
          Đăng ký: {{ fmtDate(c.enrolled_at) }}
          <span v-if="c.completed_at"> · ✅ Hoàn thành: {{ fmtDate(c.completed_at) }}</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { fmtDate, fmtPercent } from '@/utils/formatters.js'

defineProps({
  courses: { type: Array, default: () => [] },
})

function progressGradient(pct) {
  if (pct >= 80) return 'linear-gradient(90deg, #6366f1, #22c55e)'
  if (pct >= 50) return 'linear-gradient(90deg, #6366f1, #818cf8)'
  return 'linear-gradient(90deg, #4f46e5, #6366f1)'
}
</script>
