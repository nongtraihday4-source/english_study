<template>
  <div class="max-w-3xl mx-auto px-4 py-8">

    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 mb-6 text-sm" style="color:var(--color-text-muted)">
      <RouterLink to="/skill-practice" class="hover:opacity-70 transition">Luyện Kỹ Năng</RouterLink>
      <span>/</span>
      <RouterLink :to="`/skill-practice/topics/${levelQuery}`" class="hover:opacity-70 transition">{{ levelQuery }}</RouterLink>
      <span>/</span>
      <span class="truncate max-w-xs" style="color:var(--color-text-base)">{{ topicName }}</span>
    </div>

    <!-- Topic header -->
    <div class="mb-6">
      <h1 class="text-xl font-bold" style="color:var(--color-text-base)">{{ topicName || 'Bài luyện tập' }}</h1>
      <p v-if="passages.length" class="text-sm mt-1" style="color:var(--color-text-muted)">
        {{ passages.length }} bài · {{ dictationDone }}/{{ passages.length }} chính tả · {{ shadowingDone }}/{{ passages.length }} shadowing
      </p>
    </div>

    <!-- Sort control -->
    <div class="flex items-center gap-3 mb-5">
      <span class="text-xs" style="color:var(--color-text-muted)">Sắp xếp:</span>
      <div class="flex gap-1">
        <button
          v-for="opt in sortOptions"
          :key="opt.value"
          @click="sortBy = opt.value"
          class="px-3 py-1.5 rounded-lg text-xs font-medium transition"
          :style="sortBy === opt.value
            ? 'background:var(--color-primary-600);color:#fff'
            : 'background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)'"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 4" :key="i" class="h-24 rounded-2xl animate-pulse" style="background:var(--color-surface-03)" />
    </div>

    <!-- Empty state -->
    <div v-else-if="sortedPassages.length === 0" class="text-center py-16">
      <p class="text-4xl mb-3">📭</p>
      <p class="text-sm" style="color:var(--color-text-muted)">Chưa có bài nào cho chủ đề này.</p>
    </div>

    <!-- Passage list -->
    <div v-else class="space-y-3">
      <div
        v-for="passage in sortedPassages"
        :key="passage.id"
        class="rounded-2xl px-5 py-4 transition"
        style="background:var(--color-surface-02);border:1px solid var(--color-surface-04)"
      >
        <div class="flex items-start justify-between gap-4">
          <!-- Info -->
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2 mb-1 flex-wrap">
              <span
                class="text-[10px] px-2 py-0.5 rounded-full font-semibold"
                :style="difficultyStyle(passage.difficulty_tag)"
              >
                {{ difficultyLabel(passage.difficulty_tag) }}
              </span>
              <span class="text-[10px] px-2 py-0.5 rounded-full" style="background:var(--color-surface-04);color:var(--color-text-muted)">
                {{ passage.cefr_level }}
              </span>
              <span class="text-[10px]" style="color:var(--color-text-muted)">
                {{ passage.word_count }} từ
              </span>
            </div>
            <p class="text-sm font-semibold" style="color:var(--color-text-base)">{{ passage.title }}</p>

            <!-- Progress pills -->
            <div class="flex gap-3 mt-2">
              <StatusPill mode="dictation" :progress="passage.dictation_progress" />
              <StatusPill mode="shadowing" :progress="passage.shadowing_progress" />
            </div>
          </div>

          <!-- CTAs -->
          <div class="flex flex-col gap-2 shrink-0">
            <RouterLink
              :to="`/skill-practice/dictation/${passage.id}`"
              class="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold transition hover:opacity-80 whitespace-nowrap"
              :style="passage.dictation_progress?.status === 'completed'
                ? 'background:rgba(34,197,94,0.1);color:#86efac;border:1px solid rgba(34,197,94,0.2)'
                : 'background:rgba(6,182,212,0.1);color:#22d3ee;border:1px solid rgba(6,182,212,0.25)'"
            >
              🎧 Chính tả
            </RouterLink>
            <RouterLink
              :to="`/skill-practice/shadowing/${passage.id}`"
              class="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold transition hover:opacity-80 whitespace-nowrap"
              :style="passage.shadowing_progress?.status === 'completed'
                ? 'background:rgba(34,197,94,0.1);color:#86efac;border:1px solid rgba(34,197,94,0.2)'
                : 'background:rgba(99,102,241,0.1);color:#818cf8;border:1px solid rgba(99,102,241,0.25)'"
            >
              🎤 Shadowing
            </RouterLink>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { skillPracticeApi } from '@/api/skillPractice.js'

const route = useRoute()
const topicSlug = computed(() => route.params.topicSlug)
const levelQuery = computed(() => route.query.level || 'B1')
const topicName = computed(() => {
  if (!passages.value.length) return ''
  return passages.value[0].topic
})

const passages = ref([])
const loading = ref(true)
const sortBy = ref('difficulty')

const sortOptions = [
  { value: 'difficulty', label: 'Độ khó' },
  { value: 'newest', label: 'Mới nhất' },
  { value: 'progress', label: 'Tiến độ' },
]

const sortedPassages = computed(() => {
  const list = [...passages.value]
  if (sortBy.value === 'difficulty') {
    const order = { easy: 0, medium: 1, hard: 2 }
    list.sort((a, b) => (order[a.difficulty_tag] ?? 1) - (order[b.difficulty_tag] ?? 1))
  } else if (sortBy.value === 'newest') {
    list.sort((a, b) => b.id - a.id)
  } else if (sortBy.value === 'progress') {
    // Incomplete first, then sort by combined progress
    list.sort((a, b) => {
      const statusScore = (p) =>
        p?.status === 'completed' ? 2 : p?.status === 'in_progress' ? 1 : 0
      const aScore = statusScore(a.dictation_progress) + statusScore(a.shadowing_progress)
      const bScore = statusScore(b.dictation_progress) + statusScore(b.shadowing_progress)
      return aScore - bScore
    })
  }
  return list
})

const dictationDone = computed(() =>
  passages.value.filter(p => p.dictation_progress?.status === 'completed').length
)
const shadowingDone = computed(() =>
  passages.value.filter(p => p.shadowing_progress?.status === 'completed').length
)

function difficultyStyle(tag) {
  const map = {
    easy: 'background:rgba(34,197,94,0.1);color:#86efac',
    medium: 'background:rgba(251,191,36,0.1);color:#fbbf24',
    hard: 'background:rgba(239,68,68,0.1);color:#fca5a5',
  }
  return map[tag] || map.medium
}

function difficultyLabel(tag) {
  return { easy: 'Dễ', medium: 'Trung bình', hard: 'Khó' }[tag] || tag
}

const StatusPill = {
  props: ['mode', 'progress'],
  computed: {
    label() {
      const status = this.progress?.status
      const icon = this.mode === 'dictation' ? '🎧' : '🎤'
      if (status === 'completed') return `${icon} Hoàn thành`
      if (status === 'in_progress') {
        const done = this.progress?.sentences_completed || 0
        return `${icon} Đang học (${done}...)`
      }
      return `${icon} ${this.mode === 'dictation' ? 'Chính tả' : 'Shadowing'}`
    },
    style() {
      const s = this.progress?.status
      if (s === 'completed') return 'background:rgba(34,197,94,0.08);color:#86efac'
      if (s === 'in_progress') return 'background:rgba(251,191,36,0.08);color:#fbbf24'
      return 'color:var(--color-text-muted)'
    },
  },
  template: `<span class="text-[10px] px-2 py-0.5 rounded-full" :style="style">{{ label }}</span>`,
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await skillPracticeApi.getPassages({
      topic_slug: topicSlug.value,
      level: levelQuery.value,
    })
    passages.value = res.data
  } catch {
    passages.value = []
  } finally {
    loading.value = false
  }
})
</script>
