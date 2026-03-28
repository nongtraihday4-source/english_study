<template>
  <div>
    <!-- Page header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-8">
      <div>
        <h1 class="text-2xl font-black" style="color: var(--color-text-base)">
          Xin chào, {{ firstName }} 👋
        </h1>
        <p class="text-sm mt-0.5" style="color: var(--color-text-soft)">
          {{ today }} · Cấp độ hiện tại:
          <span class="font-semibold" style="color: var(--color-primary-400)">{{ auth.user?.current_level || '—' }}</span>
        </p>
      </div>
      <div class="flex items-center gap-2 self-start sm:self-auto">
        <RouterLink
          to="/help/support-request"
          class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-90"
          style="background-color: color-mix(in srgb, #3b82f6 16%, transparent); color: #60a5fa"
        >
          🛟 Cần hỗ trợ
        </RouterLink>
        <RouterLink
          to="/courses"
          class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold text-white transition hover:opacity-90"
          style="background: linear-gradient(135deg, #4f46e5, #7c3aed)"
        >
          ▶ Học ngay
        </RouterLink>
      </div>
    </div>

    <!-- ── Teacher Portal Banner (chỉ hiển thị khi role = teacher/admin) ── -->
    <div v-if="auth.isTeacher" class="mb-6 rounded-2xl overflow-hidden"
      style="border: 1px solid color-mix(in srgb,#f59e0b 40%,transparent)"
    >
      <!-- Header bar -->
      <div class="flex items-center justify-between gap-4 px-5 py-3"
        style="background: linear-gradient(135deg,#92400e22,#78350f33)"
      >
        <div class="flex items-center gap-2.5">
          <span class="text-xl">🏫</span>
          <div>
            <p class="font-bold text-sm" style="color: #fcd34d">Chế độ Giáo viên</p>
            <p class="text-xs" style="color: var(--color-text-muted)">
              Role: <strong style="color:#fbbf24">{{ auth.user?.role }}</strong>
            </p>
          </div>
        </div>
        <RouterLink to="/teacher"
          class="shrink-0 px-4 py-2 rounded-xl text-xs font-bold hover:opacity-80 transition"
          style="background-color:#f59e0b;color:#000"
        >
          Vào Teacher Portal →
        </RouterLink>
      </div>

      <!-- Stats row -->
      <div class="grid grid-cols-2 sm:grid-cols-4 divide-x"
        style="background-color:var(--color-surface-02);divide-color:var(--color-surface-04)"
      >
        <RouterLink
          v-for="ts in teacherStatCards" :key="ts.label"
          :to="ts.to"
          class="flex flex-col items-center py-4 gap-1 hover:opacity-80 transition"
        >
          <p class="text-xs" style="color:var(--color-text-muted)">{{ ts.label }}</p>
          <p class="text-2xl font-black" :style="{color: ts.color}">
            {{ teacherStatsLoading ? '…' : ts.value }}
          </p>
        </RouterLink>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="dashboard.loading" class="space-y-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <div v-for="i in 4" :key="i" class="rounded-2xl h-28 animate-pulse"
             style="background-color: var(--color-surface-03)"></div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="rounded-2xl h-72 animate-pulse" style="background-color: var(--color-surface-03)"></div>
        <div class="rounded-2xl h-72 animate-pulse" style="background-color: var(--color-surface-03)"></div>
      </div>
    </div>

    <!-- Error state -->
    <div v-else-if="dashboard.error" class="rounded-2xl p-8 text-center"
         style="background-color: var(--color-surface-03)">
      <p class="text-4xl mb-3">⚠️</p>
      <p class="text-sm font-medium mb-2" style="color: var(--color-text-base)">{{ dashboard.error }}</p>
      <button @click="dashboard.fetch(true)"
              class="text-xs px-4 py-2 rounded-xl font-medium text-white transition hover:opacity-90"
              style="background-color: var(--color-primary-600)">Thử lại</button>
    </div>

    <!-- Dashboard content -->
    <div v-else>
      <!-- Row 1: KPI cards (4 across) -->
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
        <!-- Streak card -->
        <StreakCard :streak="dashboard.streak()" />

        <!-- XP card -->
        <XPCard
          :total-x-p="dashboard.totalXP()"
          :total-exercises="totalExercises"
        />

        <!-- Overall score card -->
        <div
          class="rounded-2xl p-5 flex items-center gap-4"
          style="background: linear-gradient(135deg, #1e1e35, #1e2835); border: 1px solid var(--color-surface-04)"
        >
          <div class="relative shrink-0">
            <div class="w-14 h-14 rounded-full flex items-center justify-center text-2xl"
                 style="background-color: rgba(34,197,94,0.15); border: 2px solid rgba(34,197,94,0.4)">
              🎯
            </div>
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-wider mb-1" style="color: var(--color-text-soft)">
              Điểm TB chung
            </p>
            <div class="flex items-baseline gap-1">
              <span class="text-3xl font-black" style="color: #22c55e">{{ overallDisplay }}</span>
            </div>
            <p class="text-xs mt-1" style="color: var(--color-text-soft)">
              CEFR tương đương: <span class="font-semibold" style="color: var(--color-text-muted)">{{ cefrEquivalent }}</span>
            </p>
          </div>
        </div>

        <!-- Courses card -->
        <div
          class="rounded-2xl p-5 flex items-center gap-4"
          style="background: linear-gradient(135deg, #1e1e35, #251e35); border: 1px solid var(--color-surface-04)"
        >
          <div class="relative shrink-0">
            <div class="w-14 h-14 rounded-full flex items-center justify-center text-2xl"
                 style="background-color: rgba(168,85,247,0.15); border: 2px solid rgba(168,85,247,0.4)">
              📚
            </div>
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-wider mb-1" style="color: var(--color-text-soft)">
              Khoá đang học
            </p>
            <div class="flex items-baseline gap-1">
              <span class="text-3xl font-black" style="color: #a855f7">{{ dashboard.enrolledCourses().length }}</span>
              <span class="text-sm" style="color: var(--color-text-muted)">khoá</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Row 2: Radar chart + Course progress -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <SkillRadar :cumulative-score="primaryScore" />
        <CourseProgressList :courses="dashboard.enrolledCourses()" />
      </div>

      <!-- Row 3: Skill score bars + Recent results -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <!-- Skill breakdown bars -->
        <div
          class="rounded-2xl p-5"
          style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
        >
          <h3 class="text-sm font-semibold mb-4" style="color: var(--color-text-base)">Điểm từng kỹ năng</h3>
          <div v-if="!primaryScore" class="py-8 text-center text-sm" style="color: var(--color-text-soft)">
            Chưa có dữ liệu
          </div>
          <div v-else class="space-y-4">
            <div v-for="skill in skillBreakdown" :key="skill.key">
              <div class="flex items-center justify-between mb-1.5">
                <div class="flex items-center gap-2">
                  <span>{{ skill.icon }}</span>
                  <span class="text-sm font-medium" style="color: var(--color-text-base)">{{ skill.label }}</span>
                </div>
                <span class="text-sm font-bold" :style="{ color: skill.color }">
                  {{ fmtScore(primaryScore[skill.key]) || '—' }}
                </span>
              </div>
              <div class="w-full h-2.5 rounded-full overflow-hidden" style="background-color: var(--color-surface-04)">
                <div
                  class="h-full rounded-full transition-all duration-700"
                  :style="{
                    width: `${primaryScore[skill.key] || 0}%`,
                    backgroundColor: skill.color,
                  }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <RecentResults :results="dashboard.recentResults()" />
      </div>

      <!-- Row 4: CumulativeScore table (all levels) -->
      <div
        v-if="dashboard.cumulativeScores().length > 1"
        class="rounded-2xl p-5"
        style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
      >
        <h3 class="text-sm font-semibold mb-4" style="color: var(--color-text-base)">Điểm tổng hợp theo cấp độ</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr style="color: var(--color-text-soft)">
                <th class="text-left pb-2 text-xs font-semibold">Cấp độ</th>
                <th class="text-right pb-2 text-xs font-semibold">🎧 Nghe</th>
                <th class="text-right pb-2 text-xs font-semibold">🎤 Nói</th>
                <th class="text-right pb-2 text-xs font-semibold">📖 Đọc</th>
                <th class="text-right pb-2 text-xs font-semibold">✍️ Viết</th>
                <th class="text-right pb-2 text-xs font-semibold">TB</th>
                <th class="text-right pb-2 text-xs font-semibold">Bài đã làm</th>
              </tr>
            </thead>
            <tbody class="divide-y" style="border-color: var(--color-surface-04)">
              <tr v-for="s in dashboard.cumulativeScores()" :key="s.level_code">
                <td class="py-2.5 font-bold" style="color: var(--color-primary-400)">{{ s.level_code }}</td>
                <td class="py-2.5 text-right" style="color: var(--color-text-muted)">{{ fmtScore(s.avg_listening) }}</td>
                <td class="py-2.5 text-right" style="color: var(--color-text-muted)">{{ fmtScore(s.avg_speaking) }}</td>
                <td class="py-2.5 text-right" style="color: var(--color-text-muted)">{{ fmtScore(s.avg_reading) }}</td>
                <td class="py-2.5 text-right" style="color: var(--color-text-muted)">{{ fmtScore(s.avg_writing) }}</td>
                <td class="py-2.5 text-right font-bold" style="color: #22c55e">{{ s.overall_display }}</td>
                <td class="py-2.5 text-right text-xs" style="color: var(--color-text-soft)">{{ s.total_exercises_done }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useDashboardStore } from '@/stores/dashboard.js'
import { fmtDate, fmtScore } from '@/utils/formatters.js'
import { teacherApi } from '@/api/teacher.js'
import StreakCard from '@/components/dashboard/StreakCard.vue'
import XPCard from '@/components/dashboard/XPCard.vue'
import SkillRadar from '@/components/dashboard/SkillRadar.vue'
import CourseProgressList from '@/components/dashboard/CourseProgressList.vue'
import RecentResults from '@/components/dashboard/RecentResults.vue'

const auth = useAuthStore()
const dashboard = useDashboardStore()

// ── Teacher quick-stats ────────────────────────────────────────────────────
const teacherStatsLoading = ref(false)
const _ts = ref({ pending_grading: 0, pending_speaking: 0, pending_writing: 0, total_students: 0, active_courses: 0 })

const teacherStatCards = computed(() => [
  { label: '⏳ Chờ chấm',     value: _ts.value.pending_grading,  color: '#fcd34d', to: '/teacher/grading?status=pending' },
  { label: '🎤 Speaking',     value: _ts.value.pending_speaking, color: '#fb923c', to: '/teacher/grading?type=speaking' },
  { label: '✍️ Writing',      value: _ts.value.pending_writing,  color: '#60a5fa', to: '/teacher/grading?type=writing' },
  { label: '👥 Học viên',     value: _ts.value.total_students,   color: 'var(--color-primary-400)', to: '/teacher/classes' },
])

function loadTeacherStats() {
  teacherStatsLoading.value = true
  teacherApi.getDashboard()
    .then(res => { _ts.value = res.data?.data ?? res.data })
    .catch(() => {})
    .finally(() => { teacherStatsLoading.value = false })
}

// Re-load teacher stats whenever isTeacher flips to true
// (handles the case where role was updated in Django admin mid-session)
watch(() => auth.isTeacher, (val) => {
  if (val) loadTeacherStats()
})

onMounted(async () => {
  // Always refresh user data from DB on dashboard load so role changes
  // made in Django admin are picked up without requiring logout/login
  await auth.refreshUser()
  dashboard.fetch()
  if (auth.isTeacher) loadTeacherStats()
})

// Display computed
const firstName = computed(() => {
  const name = auth.displayName || auth.user?.email || 'bạn'
  return name.split(' ')[0]
})

const today = computed(() => {
  return new Intl.DateTimeFormat('vi-VN', {
    weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric',
    timeZone: 'Asia/Ho_Chi_Minh',
  }).format(new Date())
})

// Primary score = first (or only) cumulative score
const primaryScore = computed(() => {
  const scores = dashboard.cumulativeScores()
  return scores.length ? scores[0] : null
})

const overallDisplay = computed(() => primaryScore.value?.overall_display || '—')
const cefrEquivalent = computed(() => primaryScore.value?.cefr_equivalent || '—')

const totalExercises = computed(() =>
  dashboard.cumulativeScores().reduce((a, s) => a + (s.total_exercises_done || 0), 0)
)

const skillBreakdown = [
  { key: 'avg_listening', label: 'Nghe',     icon: '🎧', color: '#6366f1' },
  { key: 'avg_speaking',  label: 'Nói',      icon: '🎤', color: '#f97316' },
  { key: 'avg_reading',   label: 'Đọc',      icon: '📖', color: '#22c55e' },
  { key: 'avg_writing',   label: 'Viết',     icon: '✍️', color: '#eab308' },
]
</script>
