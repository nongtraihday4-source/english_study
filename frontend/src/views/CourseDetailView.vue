<template>
  <div class="p-6 max-w-4xl mx-auto">

    <!-- Toast notification -->
    <Transition name="toast">
      <div v-if="toast.show"
           class="fixed bottom-6 left-1/2 z-50 px-5 py-3 rounded-xl shadow-xl text-sm font-semibold"
           style="-webkit-transform:translateX(-50%);transform:translateX(-50%);
                  background:#1e1b4b; border:1px solid rgba(99,102,241,0.5); color:#a5b4fc;">
        {{ toast.message }}
      </div>
    </Transition>

    <!-- Breadcrumb -->
    <div class="flex items-center gap-3 mb-6">
      <RouterLink to="/courses" class="text-sm transition hover:opacity-80"
                  style="color: var(--color-text-muted)">← Tất cả khoá học</RouterLink>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-4">
      <div class="h-40 rounded-2xl animate-pulse" style="background-color: var(--color-surface-02)"></div>
      <div class="h-12 rounded-xl animate-pulse" style="background-color: var(--color-surface-02)"></div>
      <div class="space-y-2">
        <div v-for="i in 4" :key="i" class="h-14 rounded-xl animate-pulse"
             style="background-color: var(--color-surface-02)"></div>
      </div>
    </div>

    <!-- Course content -->
    <div v-else-if="course" class="space-y-5">

      <!-- ── Header card ──────────────────────────────────────────────── -->
      <div class="rounded-2xl p-6"
           style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
        <div class="flex items-start gap-4 flex-wrap">
          <div class="flex-1 min-w-0">
            <span class="px-2 py-0.5 rounded text-xs font-bold mb-2 inline-block"
                  style="background-color: var(--color-primary-600); color: white">
              {{ course.level?.code || course.cefr_level_name || course.cefr_level }}
            </span>
            <h1 class="text-2xl font-bold" style="color: var(--color-text-base)">{{ course.title }}</h1>
            <p class="text-sm mt-2" style="color: var(--color-text-muted)">{{ course.description }}</p>
          </div>
          <!-- Enroll / enrolled badge -->
          <button v-if="!course.is_enrolled" @click="enroll" :disabled="enrolling"
                  class="flex-shrink-0 px-5 py-2.5 rounded-xl font-semibold text-sm text-white transition hover:opacity-90 disabled:opacity-50"
                  style="background: linear-gradient(135deg, #4f46e5, #7c3aed)">
            {{ enrolling ? 'Đang đăng ký...' : 'Đăng ký học' }}
          </button>
          <span v-else class="flex-shrink-0 px-4 py-2 rounded-xl text-sm font-semibold"
                style="background-color: rgba(34,197,94,0.15); color: #86efac">
            ✓ Đã đăng ký
          </span>
        </div>
      </div>

      <!-- ── Course progress card (enrolled users) ────────────────────── -->
      <div v-if="course.is_enrolled"
           class="rounded-2xl p-5"
           style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
        <h3 class="text-sm font-semibold mb-3" style="color: var(--color-text-base)">📊 Tiến độ học tập</h3>
        <!-- Progress bar -->
        <div class="mb-3">
          <div class="flex justify-between text-xs mb-1.5" style="color: var(--color-text-muted)">
            <span>Hoàn thành khoá học</span>
            <span class="font-medium" style="color: var(--color-text-base)">{{ courseProgressPercent }}%</span>
          </div>
          <div class="w-full h-2.5 rounded-full overflow-hidden" style="background-color: var(--color-surface-04)">
            <div class="h-full rounded-full transition-all duration-700"
                 :style="`width: ${courseProgressPercent}%; background: linear-gradient(90deg,#6366f1,#8b5cf6)`"></div>
          </div>
        </div>
        <!-- Stats -->
        <div class="flex flex-wrap gap-5 text-xs" style="color: var(--color-text-muted)">
          <span>
            <span class="font-bold text-sm" style="color: var(--color-text-base)">
              {{ course.completed_lessons_count ?? 0 }}
            </span>
            / {{ course.total_lessons || '—' }} bài hoàn thành
          </span>
          <span v-if="course.average_score != null">
            Điểm trung bình:
            <span class="font-bold text-sm" :style="{ color: scoreColor(course.average_score) }">
              {{ course.average_score }}
            </span>
          </span>
        </div>
      </div>

      <!-- ── Chapter accordion ────────────────────────────────────────── -->
      <div>
        <h2 class="font-bold text-lg mb-3" style="color: var(--color-text-base)">Nội dung khoá học</h2>
        <div v-if="chaptersLoading" class="space-y-2">
          <div v-for="i in 4" :key="i" class="h-14 rounded-xl animate-pulse"
               style="background-color: var(--color-surface-02)"></div>
        </div>

        <div v-else class="space-y-2">
          <div v-for="chapter in chapters" :key="chapter.id"
               class="rounded-xl overflow-hidden"
               style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">

            <!-- Chapter header button -->
            <button @click="chapter._open = !chapter._open"
                    class="w-full flex items-center justify-between p-4 text-left transition hover:bg-white/5">
              <div>
                <p class="font-semibold text-sm" style="color: var(--color-text-base)">{{ chapter.title }}</p>
                <p class="text-xs mt-0.5" style="color: var(--color-text-muted)">
                  {{ chapter.lesson_count || chapter.lessons_count || 0 }} bài học
                </p>
              </div>
              <span style="color: var(--color-text-soft)">{{ chapter._open ? '▲' : '▼' }}</span>
            </button>

            <!-- Lessons list -->
            <div v-if="chapter._open" class="border-t" style="border-color: var(--color-surface-04)">

              <!-- Loading indicator -->
              <div v-if="!chapter.lessons"
                   class="p-4 text-sm animate-pulse" style="color: var(--color-text-muted)">
                Đang tải...
              </div>

              <template v-else>
                <div v-for="lesson in chapter.lessons" :key="lesson.id">

                  <!-- Available / Completed → clickable RouterLink.
                       is_unlocked=false means prerequisites not met.
                       progress_status is only used for visual badges, NOT for gating navigation. -->
                  <RouterLink
                    v-if="lesson.is_unlocked !== false && lesson.exercise_id"
                    :to="{
                      name: `learn-${lesson.exercise_type || lesson.lesson_type}`,
                      params: { id: lesson.exercise_id },
                      query: { lesson_id: lesson.id }
                    }"
                    class="lesson-row available flex items-center gap-3 px-4 py-3 md:py-4 transition hover:bg-white/5"
                    :class="lesson.progress_status === 'available' ? 'lesson-available' : ''"
                    style="border-top: 1px solid var(--color-surface-04); text-decoration: none; display: flex"
                  >
                    <span class="flex-shrink-0 text-base">{{ lessonIcon(lesson.exercise_type || lesson.lesson_type) }}</span>
                    <span class="flex-1 min-w-0 truncate text-sm"
                          :style="lesson.progress_status === 'completed'
                            ? 'color: #86efac'
                            : 'color: var(--color-text-base)'">
                      {{ lesson.title }}
                    </span>
                    <span class="ml-2 flex-shrink-0 text-xs">
                      <span v-if="lesson.progress_status === 'completed'" title="Đã hoàn thành">✅</span>
                      <span v-else title="Bắt đầu học" style="color:#818cf8">▶</span>
                    </span>
                  </RouterLink>

                  <!-- Locked → non-navigable div -->
                  <div
                    v-else
                    class="flex items-center gap-3 px-4 py-3 md:py-4 cursor-not-allowed select-none"
                    style="border-top: 1px solid var(--color-surface-04); opacity: 0.4"
                    :title="lessonLockTitle(lesson)"
                  >
                    <span class="flex-shrink-0 text-base">{{ lessonIcon(lesson.exercise_type || lesson.lesson_type) }}</span>
                    <span class="flex-1 min-w-0 truncate text-sm" style="color: var(--color-text-base)">
                      {{ lesson.title }}
                    </span>
                    <span class="ml-2 flex-shrink-0">🔒</span>
                  </div>

                </div>
              </template>
            </div>

          </div>
        </div>
      </div>

    </div>

    <!-- Not found -->
    <div v-else class="text-center py-16" style="color: var(--color-text-muted)">
      <p class="text-4xl mb-3">📚</p>
      <p>Không tìm thấy khoá học.</p>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { curriculumApi } from '@/api/curriculum.js'
import { progressApi } from '@/api/progress.js'
import { useDashboardStore } from '@/stores/dashboard.js'

const route = useRoute()
const dashboard = useDashboardStore()

const course = ref(null)
const chapters = ref([])
const loading = ref(false)
const chaptersLoading = ref(false)
const enrolling = ref(false)

// ── Toast ───────────────────────────────────────────────────────────────────
const toast = reactive({ show: false, message: '' })
let _toastTimer = null

function showToast(message) {
  clearTimeout(_toastTimer)
  toast.message = message
  toast.show = true
  _toastTimer = setTimeout(() => { toast.show = false }, 3000)
}

// ── Computed ────────────────────────────────────────────────────────────────
const courseProgressPercent = computed(() =>
  Math.round(Number(course.value?.progress_percent) || 0)
)

function scoreColor(score) {
  if (score >= 75) return '#86efac'
  if (score >= 60) return '#fde68a'
  return '#fca5a5'
}

// ── Helpers ─────────────────────────────────────────────────────────────────
function lessonIcon(type) {
  const icons = { listening: '🎧', speaking: '🎤', reading: '📄', writing: '✍️' }
  return icons[type] || '📚'
}

function lessonLockTitle(lesson) {
  if (lesson.is_unlocked === false) return 'Hoàn thành bài trước để mở khóa'
  if (!lesson.exercise_id) return 'Chưa có bài tập'
  return 'Hoàn thành bài trước để mở khóa'
}

// ── Enrollment ───────────────────────────────────────────────────────────────
async function enroll() {
  enrolling.value = true
  try {
    await progressApi.enrollCourse(course.value.id)
    course.value.is_enrolled = true
    dashboard.invalidate()
    showToast('✓ Đăng ký thành công!')
  } catch (e) {
    const msg = e?.response?.data?.detail || 'Đăng ký thất bại, vui lòng thử lại.'
    showToast('⚠ ' + msg)
  } finally {
    enrolling.value = false
  }
}

// ── Chapter auto-load lessons (with cache) ───────────────────────────────────
watch(chapters, (chs) => {
  chs.forEach(ch => {
    watch(() => ch._open, async (open) => {
      if (!open || ch.lessons !== null) return  // skip if closing or already cached
      try {
        const res = await curriculumApi.getLessons(route.params.id, ch.id)
        const ld = res.data?.data ?? res.data
        ch.lessons = ld?.results || (Array.isArray(ld) ? ld : [])
      } catch {
        ch.lessons = []
      }
    })
  })
}, { deep: false })

// ── Mount ────────────────────────────────────────────────────────────────────
onMounted(async () => {
  loading.value = true
  try {
    const courseRes = await curriculumApi.getCourse(route.params.id)
    course.value = courseRes.data?.data ?? courseRes.data

    chaptersLoading.value = true
    const chRes = await curriculumApi.getChapters(route.params.id)
    const chd = chRes.data?.data ?? chRes.data
    chapters.value = (chd?.results || (Array.isArray(chd) ? chd : [])).map(
      ch => reactive({ ...ch, _open: false, lessons: null })
    )
  } catch {
    course.value = null
  } finally {
    loading.value = false
    chaptersLoading.value = false
  }
})
</script>

<style scoped>
/* Toast slide-up animation */
.toast-enter-active,
.toast-leave-active { transition: opacity .3s ease, transform .3s ease; }
.toast-enter-from,
.toast-leave-to     { opacity: 0; transform: translateX(-50%) translateY(0.75rem); }
.toast-enter-to,
.toast-leave-from   { opacity: 1; transform: translateX(-50%) translateY(0); }

/* Available lesson: highlight left border */
.lesson-available {
  border-left: 2px solid #6366f1 !important;
}
</style>
