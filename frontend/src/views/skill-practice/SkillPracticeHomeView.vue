<template>
  <div class="max-w-5xl mx-auto px-4 py-8">

    <!-- Hero Header -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-2">
        <span class="text-3xl">🎯</span>
        <div>
          <h1 class="text-2xl font-bold" style="color:var(--color-text-base)">Luyện Kỹ Năng</h1>
          <p class="text-sm mt-0.5" style="color:var(--color-text-muted)">
            Luyện Chính tả và Shadowing theo chủ đề — giúp bạn thành thạo ngữ pháp, phát âm và tự tin hơn khi giao tiếp.
          </p>
        </div>
      </div>
    </div>

    <!-- Stats bar -->
    <div v-if="summary" class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
      <StatCard icon="📄" :value="summary.total_passages_started" label="Bài đã học" color="indigo" />
      <StatCard icon="🎧" :value="summary.dictation_completed" label="Chính tả xong" color="cyan" />
      <StatCard icon="🎤" :value="summary.shadowing_completed" label="Shadowing xong" color="purple" />
      <StatCard icon="⏱" :value="formatTime(summary.total_time_seconds)" label="Thời gian luyện" color="amber" />
    </div>
    <div v-else-if="loadingStats" class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
      <div v-for="i in 4" :key="i" class="h-20 rounded-2xl animate-pulse" style="background:var(--color-surface-03)" />
    </div>

    <!-- Skill cards -->
    <div class="grid md:grid-cols-2 gap-4 mb-8">
      <!-- Dictation card -->
      <div class="rounded-2xl p-6" style="background:linear-gradient(135deg,rgba(6,182,212,0.08),rgba(6,182,212,0.03));border:1px solid rgba(6,182,212,0.2)">
        <div class="flex items-start justify-between mb-4">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="text-2xl">🎧</span>
              <span class="text-lg font-bold" style="color:#22d3ee">Chính tả</span>
            </div>
            <p class="text-sm" style="color:var(--color-text-muted)">
              Nghe từng câu và gõ lại chính xác. Luyện tập theo câu hoặc cả đoạn văn để nâng cao khả năng nghe, chính tả và hiểu từ trong ngữ cảnh.
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2 text-xs mb-4" style="color:var(--color-text-soft)">
          <span class="px-2 py-0.5 rounded-full" style="background:rgba(6,182,212,0.12);color:#22d3ee">Theo câu</span>
          <span class="px-2 py-0.5 rounded-full" style="background:rgba(6,182,212,0.12);color:#22d3ee">Cả bài (nâng cao)</span>
          <span class="px-2 py-0.5 rounded-full" style="background:rgba(6,182,212,0.12);color:#22d3ee">Gợi ý thông minh</span>
        </div>
        <RouterLink
          to="/skill-practice/topics/B1"
          class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
          style="background:rgba(6,182,212,0.15);color:#22d3ee;border:1px solid rgba(6,182,212,0.3)"
        >
          Bắt đầu Chính tả →
        </RouterLink>
      </div>

      <!-- Shadowing card -->
      <div class="rounded-2xl p-6" style="background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(99,102,241,0.03));border:1px solid rgba(99,102,241,0.2)">
        <div class="flex items-start justify-between mb-4">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="text-2xl">🎤</span>
              <span class="text-lg font-bold" style="color:#818cf8">Shadowing</span>
            </div>
            <p class="text-sm" style="color:var(--color-text-muted)">
              Nghe và đọc theo để làm quen với nhịp điệu, ngữ điệu và phát âm tự nhiên. Ghi âm và so sánh giọng của bạn với mẫu để cải thiện nhanh hơn.
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2 text-xs mb-4" style="color:var(--color-text-soft)">
          <span class="px-2 py-0.5 rounded-full" style="background:rgba(99,102,241,0.12);color:#818cf8">Ghi âm</span>
          <span class="px-2 py-0.5 rounded-full" style="background:rgba(99,102,241,0.12);color:#818cf8">So sánh audio</span>
          <span class="px-2 py-0.5 rounded-full" style="background:rgba(99,102,241,0.12);color:#818cf8">Tự đánh giá</span>
        </div>
        <RouterLink
          to="/skill-practice/topics/B1"
          class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
          style="background:rgba(99,102,241,0.15);color:#818cf8;border:1px solid rgba(99,102,241,0.3)"
        >
          Bắt đầu Shadowing →
        </RouterLink>
      </div>
    </div>

    <!-- Level selector -->
    <div class="mb-6">
      <h2 class="text-base font-bold mb-3" style="color:var(--color-text-base)">Chọn cấp độ</h2>
      <div class="flex flex-wrap gap-2">
        <RouterLink
          v-for="level in levels"
          :key="level.code"
          :to="`/skill-practice/topics/${level.code}`"
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
          :style="level.style"
        >
          <span>{{ level.emoji }}</span>
          <span>{{ level.code }}</span>
          <span class="font-normal text-xs opacity-75">{{ level.label }}</span>
        </RouterLink>
      </div>
    </div>

    <!-- Recent activity -->
    <div v-if="summary?.recent_passages?.length">
      <h2 class="text-base font-bold mb-3" style="color:var(--color-text-base)">Gần đây</h2>
      <div class="space-y-2">
        <div
          v-for="passage in summary.recent_passages"
          :key="passage.id"
          class="flex items-center justify-between px-4 py-3 rounded-xl"
          style="background:var(--color-surface-02);border:1px solid var(--color-surface-04)"
        >
          <div class="flex items-center gap-3 min-w-0">
            <span class="text-base shrink-0">📄</span>
            <div class="min-w-0">
              <p class="text-sm font-medium truncate" style="color:var(--color-text-base)">{{ passage.title }}</p>
              <p class="text-xs truncate" style="color:var(--color-text-muted)">{{ passage.topic }} · {{ passage.cefr_level }}</p>
            </div>
          </div>
          <div class="flex gap-2 shrink-0 ml-3">
            <RouterLink
              :to="`/skill-practice/dictation/${passage.id}`"
              class="px-3 py-1.5 rounded-lg text-xs font-medium transition hover:opacity-80"
              :style="passage.dictation_progress?.status === 'completed'
                ? 'background:rgba(34,197,94,0.12);color:#86efac;border:1px solid rgba(34,197,94,0.2)'
                : 'background:rgba(6,182,212,0.1);color:#22d3ee;border:1px solid rgba(6,182,212,0.2)'"
            >
              {{ passage.dictation_progress?.status === 'completed' ? '✓ Chính tả' : '🎧 Chính tả' }}
            </RouterLink>
            <RouterLink
              :to="`/skill-practice/shadowing/${passage.id}`"
              class="px-3 py-1.5 rounded-lg text-xs font-medium transition hover:opacity-80"
              :style="passage.shadowing_progress?.status === 'completed'
                ? 'background:rgba(34,197,94,0.12);color:#86efac;border:1px solid rgba(34,197,94,0.2)'
                : 'background:rgba(99,102,241,0.1);color:#818cf8;border:1px solid rgba(99,102,241,0.2)'"
            >
              {{ passage.shadowing_progress?.status === 'completed' ? '✓ Shadowing' : '🎤 Shadowing' }}
            </RouterLink>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { skillPracticeApi } from '@/api/skillPractice.js'

const summary = ref(null)
const loadingStats = ref(true)

const levels = [
  {
    code: 'A2',
    label: 'Sơ - Trung cấp',
    emoji: '🌱',
    style: 'background:rgba(34,197,94,0.1);color:#86efac;border:1px solid rgba(34,197,94,0.2)',
  },
  {
    code: 'B1',
    label: 'Trung cấp',
    emoji: '⭐',
    style: 'background:rgba(251,191,36,0.1);color:#fbbf24;border:1px solid rgba(251,191,36,0.2)',
  },
  {
    code: 'B2',
    label: 'Trên trung cấp',
    emoji: '🌟',
    style: 'background:rgba(251,146,60,0.1);color:#fb923c;border:1px solid rgba(251,146,60,0.2)',
  },
  {
    code: 'C1',
    label: 'Cao cấp',
    emoji: '🔥',
    style: 'background:rgba(239,68,68,0.1);color:#fca5a5;border:1px solid rgba(239,68,68,0.2)',
  },
  {
    code: 'C2',
    label: 'Thành thạo',
    emoji: '💎',
    style: 'background:rgba(168,85,247,0.1);color:#c084fc;border:1px solid rgba(168,85,247,0.2)',
  },
]

function formatTime(seconds) {
  if (!seconds) return '0 phút'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  if (h > 0) return `${h}g ${m}p`
  return `${m} phút`
}

onMounted(async () => {
  try {
    const res = await skillPracticeApi.getProgressSummary()
    summary.value = res.data
  } catch {
    // summary stays null — non-blocking
  } finally {
    loadingStats.value = false
  }
})
</script>

<script>
const StatCard = {
  props: ['icon', 'value', 'label', 'color'],
  template: `
    <div class="rounded-2xl px-5 py-4" style="background:var(--color-surface-02);border:1px solid var(--color-surface-04)">
      <div class="flex items-center gap-2 mb-1">
        <span class="text-xl">{{ icon }}</span>
      </div>
      <p class="text-2xl font-bold" style="color:var(--color-text-base)">{{ value }}</p>
      <p class="text-xs mt-0.5" style="color:var(--color-text-muted)">{{ label }}</p>
    </div>
  `,
}
export default {
  components: { StatCard },
}
</script>
