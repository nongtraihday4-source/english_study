<template>
  <!-- Streak card: fire emoji, streak days, progress ring -->
  <div
    class="rounded-2xl p-5 flex items-center gap-4"
    style="background: linear-gradient(135deg, #1e1e35, #252550); border: 1px solid var(--color-surface-04)"
  >
    <!-- Fire icon with glow -->
    <div class="relative shrink-0">
      <div class="absolute inset-0 rounded-full blur-md opacity-50" style="background-color: #fb923c"></div>
      <div class="relative w-14 h-14 rounded-full flex items-center justify-center text-3xl"
           style="background-color: rgba(251,146,60,0.15); border: 2px solid rgba(251,146,60,0.4)">
        🔥
      </div>
    </div>

    <div class="flex-1 min-w-0">
      <p class="text-xs font-semibold uppercase tracking-wider mb-1" style="color: var(--color-text-soft)">
        Chuỗi ngày
      </p>
      <div class="flex items-baseline gap-1.5">
        <span class="text-3xl font-black" style="color: #fb923c">{{ streak?.current_streak || 0 }}</span>
        <span class="text-sm font-medium" style="color: var(--color-text-muted)">ngày</span>
      </div>
      <p class="text-xs mt-1" style="color: var(--color-text-soft)">
        Kỷ lục: <span class="font-semibold" style="color: var(--color-text-muted)">{{ streak?.longest_streak || 0 }} ngày</span>
      </p>
    </div>

    <!-- Protected indicator -->
    <div v-if="streak?.streak_protected_until" class="shrink-0 text-yellow-400 text-xl" title="Streak được bảo vệ">🛡️</div>
  </div>
</template>

<script setup>
defineProps({
  streak: { type: Object, default: null },
})
</script>
