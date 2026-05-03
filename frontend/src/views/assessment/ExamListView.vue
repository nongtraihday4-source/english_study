<template>
  <div class="p-6 max-w-7xl">
    <section
      class="rounded-3xl p-6 mb-6"
      style="background: linear-gradient(145deg, color-mix(in srgb, var(--color-primary-600) 28%, transparent), color-mix(in srgb, var(--color-surface-02) 80%, transparent)); border: 1px solid var(--color-surface-04)"
    >
      <div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 class="text-3xl font-bold" style="color: var(--color-text-base)">Assessment / Exam</h1>
          <p class="mt-1 text-sm" style="color: var(--color-text-soft)">Làm bài kiểm tra theo lộ trình học tập của bạn</p>
        </div>
        <div class="grid grid-cols-2 gap-2 text-xs md:text-sm">
          <div class="rounded-xl px-3 py-2" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <p style="color: var(--color-text-muted)">Tổng bài thi</p>
            <p class="font-semibold" style="color: var(--color-text-base)">{{ stats.total }}</p>
          </div>
          <div class="rounded-xl px-3 py-2" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <p style="color: var(--color-text-muted)">Đã hoàn thành</p>
            <p class="font-semibold" style="color: var(--color-text-base)">{{ stats.completed }}</p>
          </div>
        </div>
      </div>
    </section>

    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div
        v-for="i in 6"
        :key="i"
        class="rounded-2xl h-48 animate-pulse"
        style="background-color: var(--color-surface-02)"
      />
    </div>

    <div v-else-if="error" class="text-center py-16 rounded-2xl" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
      <p class="text-4xl mb-3">⚠️</p>
      <p style="color: #fca5a5">{{ error }}</p>
    </div>

    <div v-else class="space-y-8">
      <section
        v-for="group in grouped"
        :key="group.type"
        class="rounded-2xl p-5"
        style="background-color: color-mix(in srgb, var(--color-surface-02) 86%, transparent); border: 1px solid var(--color-surface-04)"
      >
        <div class="mb-4 flex flex-wrap items-center gap-2">
          <h2 class="text-xl font-bold" style="color: var(--color-text-base)">{{ group.title }}</h2>
          <span class="rounded-full px-2.5 py-1 text-xs font-semibold" style="background-color: var(--color-surface-03); color: var(--color-text-muted)">
            {{ group.items.length }} bài thi
          </span>
          <span
            v-if="group.type === 'progress_check'"
            class="rounded-full px-2.5 py-1 text-xs font-semibold"
            style="background-color: rgba(248, 113, 113, 0.18); color: #fca5a5"
          >
            Bắt buộc
          </span>
        </div>

        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <article
            v-for="exam in group.items"
            :key="exam.id"
            class="rounded-2xl p-5 flex flex-col gap-4 transition hover:-translate-y-0.5"
            style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <h3 class="text-base font-bold leading-snug" style="color: var(--color-text-base)">{{ exam.title }}</h3>
                <p class="text-xs mt-1" style="color: var(--color-text-muted)">
                  {{ skillLabel(exam.skill) }} · {{ exam.time_limit_minutes }} phút · {{ questionCount(exam) }} câu
                </p>
              </div>
              <span
                class="shrink-0 rounded-full px-2 py-0.5 text-xs font-bold"
                style="background-color: var(--color-primary-600)22; color: var(--color-primary-400)"
              >
                {{ exam.cefr_level || 'A1' }}
              </span>
            </div>

            <div class="w-full h-1.5 rounded-full overflow-hidden" style="background-color: var(--color-surface-04)">
              <div
                class="h-full rounded-full transition-all"
                style="background-color: var(--color-primary-500)"
                :style="{ width: examStatus(exam.id).done ? `${examStatus(exam.id).score || 0}%` : '0%' }"
              />
            </div>

            <div class="flex items-center justify-between gap-2 text-xs">
              <span
                v-if="examStatus(exam.id).done"
                class="rounded-lg px-2.5 py-1 font-semibold"
                style="background-color: rgba(74, 222, 128, 0.16); color: #86efac"
              >
                Hoàn thành · {{ examStatus(exam.id).score }}%
              </span>
              <span
                v-else
                class="rounded-lg px-2.5 py-1 font-semibold"
                style="background-color: var(--color-surface-03); color: var(--color-text-muted)"
              >
                Chưa làm
              </span>

              <span style="color: var(--color-text-muted)">#{{ exam.id }}</span>
            </div>

            <RouterLink
              :to="`/assessments/${exam.id}`"
              class="inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold transition hover:opacity-80"
              style="background-color: var(--color-primary-600); color: #fff"
            >
              Bắt đầu làm bài
            </RouterLink>
          </article>
        </div>
      </section>

      <div v-if="allExams.length === 0" class="text-center py-16 rounded-2xl" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
        <p class="text-5xl mb-3">📝</p>
        <p class="font-semibold" style="color: var(--color-text-base)">Chưa có bài thi nào.</p>
        <p class="text-sm mt-1" style="color: var(--color-text-muted)">Hệ thống sẽ hiển thị bài thi ngay khi được mở cho cấp độ của bạn.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { exercisesApi } from '@/api/exercises'

const loading = ref(true)
const error = ref('')
const allExams = ref([])
const completedMap = ref({})

const GROUP_META = {
  progress_check: { title: 'Progress Check', order: 1 },
  mock_test: { title: 'Mock Test', order: 2 },
  placement: { title: 'Placement Test', order: 3 },
}

const grouped = computed(() => {
  const buckets = Object.keys(GROUP_META).map((k) => ({
    type: k,
    title: GROUP_META[k].title,
    order: GROUP_META[k].order,
    items: [],
  }))
  const map = Object.fromEntries(buckets.map((b) => [b.type, b]))

  allExams.value.forEach((exam) => {
    const t = exam.exam_type || 'mock_test'
    ;(map[t] || map.mock_test).items.push(exam)
  })

  return buckets.filter((b) => b.items.length > 0).sort((a, b) => a.order - b.order)
})

const stats = computed(() => {
  const total = allExams.value.length
  const completed = allExams.value.reduce((acc, exam) => (examStatus(exam.id).done ? acc + 1 : acc), 0)
  return { total, completed }
})

function skillLabel(skill) {
  if (skill === 'listening') return 'Listening'
  if (skill === 'reading') return 'Reading'
  return 'Mixed'
}

function examStatus(examId) {
  return completedMap.value[examId] || { done: false, score: null }
}

function questionCount(exam) {
  return exam.question_count || exam.total_questions || 0
}

onMounted(async () => {
  try {
    const res = await exercisesApi.getExams()
    const payload = res.data?.data ?? res.data
    // Support raw array, DRF pagination object, and nested envelope formats.
    if (Array.isArray(payload)) {
      allExams.value = payload
    } else if (Array.isArray(payload?.results)) {
      allExams.value = payload.results
    } else if (Array.isArray(payload?.data?.results)) {
      allExams.value = payload.data.results
    } else {
      allExams.value = []
    }

    const saved = localStorage.getItem('exam_scores_v1')
    completedMap.value = saved ? JSON.parse(saved) : {}
  } catch (e) {
    error.value = 'Không thể tải danh sách bài thi.'
  } finally {
    loading.value = false
  }
})
</script>
