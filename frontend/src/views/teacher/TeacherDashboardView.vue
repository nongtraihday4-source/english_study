<template>
  <div class="max-w-5xl space-y-6">

    <!-- Stats row -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div v-for="stat in stats" :key="stat.label"
        class="rounded-2xl p-4 flex flex-col gap-1"
        style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
      >
        <p class="text-2xl">{{ stat.icon }}</p>
        <p class="text-2xl font-black leading-none" :style="{ color: stat.color }">
          {{ loading ? '–' : stat.value }}
        </p>
        <p class="text-xs" style="color: var(--color-text-muted)">{{ stat.label }}</p>
      </div>
    </div>

    <!-- Pending banner -->
    <div v-if="!loading && dash.pending_grading > 0"
      class="flex items-center justify-between gap-4 rounded-2xl px-5 py-4"
      style="background-color: color-mix(in srgb,#f59e0b 12%,transparent); border: 1px solid color-mix(in srgb,#f59e0b 35%,transparent)"
    >
      <div class="flex items-center gap-3">
        <span class="text-2xl">⏳</span>
        <div>
          <p class="font-bold text-sm" style="color: #fcd34d">
            {{ dash.pending_grading }} bài đang chờ chấm
          </p>
          <p class="text-xs mt-0.5" style="color: var(--color-text-muted)">
            {{ dash.pending_speaking }} Speaking · {{ dash.pending_writing }} Writing
          </p>
        </div>
      </div>
      <RouterLink to="/teacher/grading"
        class="shrink-0 px-4 py-2 rounded-xl text-sm font-semibold hover:opacity-80 transition"
        style="background-color: #f59e0b; color: #000"
      >
        Chấm ngay →
      </RouterLink>
    </div>

    <!-- Score distribution charts -->
    <div class="grid md:grid-cols-2 gap-4">
      <ScoreDistCard
        title="Điểm Speaking"
        icon="🎤"
        :avg="dash.avg_speaking_score"
        :dist="dash.speaking_score_distribution"
        :loading="loading"
      />
      <ScoreDistCard
        title="Điểm Writing"
        icon="✍️"
        :avg="dash.avg_writing_score"
        :dist="dash.writing_score_distribution"
        :loading="loading"
      />
    </div>

    <!-- Quick actions -->
    <div class="grid sm:grid-cols-3 gap-4">
      <RouterLink
        v-for="action in QUICK_ACTIONS"
        :key="action.to"
        :to="action.to"
        class="rounded-2xl p-5 flex items-center gap-4 hover:-translate-y-0.5 transition"
        style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
      >
        <span class="text-3xl">{{ action.icon }}</span>
        <div>
          <p class="font-semibold text-sm" style="color: var(--color-text-base)">{{ action.label }}</p>
          <p class="text-xs mt-0.5" style="color: var(--color-text-muted)">{{ action.desc }}</p>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineComponent, h } from 'vue'
import { teacherApi } from '@/api/teacher.js'

const loading = ref(false)
const dash = ref({
  pending_grading: 0, pending_speaking: 0, pending_writing: 0,
  total_students: 0, active_courses: 0,
  avg_speaking_score: 0, avg_writing_score: 0,
  speaking_score_distribution: [], writing_score_distribution: [],
})

async function load() {
  loading.value = true
  try {
    const res = await teacherApi.getDashboard()
    dash.value = res.data?.data ?? res.data
  } catch { /* silent */ }
  finally { loading.value = false }
}

const stats = computed(() => [
  { icon: '⏳', label: 'Cần chấm',       value: dash.value.pending_grading,  color: '#fcd34d' },
  { icon: '👥', label: 'Học viên',        value: dash.value.total_students,   color: 'var(--color-primary-400)' },
  { icon: '📚', label: 'Khoá học',        value: dash.value.active_courses,   color: '#86efac' },
  { icon: '🎤', label: 'TB Điểm Speaking',value: dash.value.avg_speaking_score + '%', color: '#fb923c' },
])

const QUICK_ACTIONS = [
  { to: '/teacher/grading', icon: '✏️',  label: 'Chấm bài', desc: 'Xem hàng đợi bài nộp' },
  { to: '/teacher/classes', icon: '👥',  label: 'Lớp học',  desc: 'Quản lý học viên' },
  { to: '/teacher/grading?status=completed', icon: '📋', label: 'Đã chấm', desc: 'Xem lịch sử chấm bài' },
]

// ── ScoreDistCard inline component ─────────────────────────────────────────
const ScoreDistCard = defineComponent({
  props: ['title', 'icon', 'avg', 'dist', 'loading'],
  setup(props) {
    return () => h('div',
      { class: 'rounded-2xl p-5', style: 'background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)' },
      [
        h('div', { class: 'flex items-center gap-2 mb-4' }, [
          h('span', { class: 'text-xl' }, props.icon),
          h('p', { class: 'font-bold text-sm', style: 'color: var(--color-text-base)' }, props.title),
          h('span', {
            class: 'ml-auto text-2xl font-black',
            style: 'color: var(--color-primary-400)'
          }, props.loading ? '–' : props.avg),
        ]),
        props.loading
          ? h('div', { class: 'space-y-2' }, [1,2,3,4].map(i =>
              h('div', { key: i, class: 'h-5 rounded animate-pulse', style: 'background-color: var(--color-surface-03)' })
            ))
          : (!props.dist?.length
              ? h('p', { class: 'text-xs text-center py-4', style: 'color: var(--color-text-muted)' }, 'Chưa có dữ liệu')
              : h('div', { class: 'space-y-2' }, (props.dist || []).map(b =>
                  h('div', { key: b.label }, [
                    h('div', { class: 'flex justify-between text-xs mb-1', style: 'color: var(--color-text-muted)' }, [
                      h('span', b.label),
                      h('span', `${b.count} bài (${b.percent}%)`),
                    ]),
                    h('div', { class: 'w-full h-2 rounded-full overflow-hidden', style: 'background-color: var(--color-surface-04)' }, [
                      h('div', {
                        class: 'h-full rounded-full transition-all',
                        style: `width: ${b.percent}%; background-color: var(--color-primary-500)`,
                      }),
                    ]),
                  ])
                ))
            ),
      ]
    )
  },
})

onMounted(load)
</script>
