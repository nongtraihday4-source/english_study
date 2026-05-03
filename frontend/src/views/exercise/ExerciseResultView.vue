<template>
  <div class="p-6 max-w-2xl mx-auto">

    <!-- Unlock modal (shown when a new lesson becomes accessible) -->
    <UnlockModal
      :show="unlockModal.show"
      :lesson-title="unlockModal.lessonTitle"
      :xp-gained="unlockModal.xpGained"
      @close="unlockModal.show = false"
    />

    <!-- Chapter completion modal -->
    <Transition name="chapter-burst">
      <div v-if="chapterModal.show" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/72 p-4 backdrop-blur-sm">
        <div class="chapter-complete-card relative w-full max-w-md overflow-hidden rounded-[2rem] text-center shadow-2xl">
          <div class="chapter-complete-orb chapter-complete-orb-left"></div>
          <div class="chapter-complete-orb chapter-complete-orb-right"></div>
          <div class="chapter-complete-spark chapter-complete-spark-a">✦</div>
          <div class="chapter-complete-spark chapter-complete-spark-b">✦</div>
          <div class="chapter-complete-spark chapter-complete-spark-c">✦</div>

          <div class="relative px-7 pt-8 pb-7">
            <div class="chapter-complete-emblem mx-auto mb-4">
              <span>🏆</span>
            </div>

            <div class="inline-flex items-center gap-2 rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] chapter-complete-pill">
              <span>Chapter Complete</span>
            </div>

            <h2 class="mt-4 text-[1.65rem] font-extrabold leading-tight" style="color:#fff">Bạn đã chốt xong chương này</h2>

            <p class="mt-3 text-sm leading-6 chapter-complete-copy">
              Toàn bộ bài học trong
              <strong class="font-bold text-white">{{ chapterModal.chapterTitle }}</strong>
              đã được hoàn thành. Phần tiếp theo đã sẵn sàng để tiếp tục.
            </p>

            <div class="mt-6 grid grid-cols-2 gap-3 text-left">
              <div class="chapter-complete-stat">
                <div class="text-[11px] font-semibold uppercase tracking-[0.18em] chapter-complete-stat-label">Điểm trung bình</div>
                <div class="mt-2 text-3xl font-extrabold text-white">{{ chapterAverageLabel }}</div>
              </div>
              <div class="chapter-complete-stat">
                <div class="text-[11px] font-semibold uppercase tracking-[0.18em] chapter-complete-stat-label">Trạng thái</div>
                <div class="mt-3 inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold chapter-complete-chip">
                  Đã mở phần tiếp theo
                </div>
              </div>
            </div>

            <div class="mt-6 flex flex-col gap-3">
              <button @click="chapterModal.show = false; goToCourseDetail()"
                      class="w-full rounded-2xl px-5 py-3.5 text-sm font-semibold text-white transition hover:opacity-95 chapter-complete-button">
                Xem tiến độ chương tiếp theo →
              </button>
              <button @click="chapterModal.show = false"
                      class="w-full rounded-2xl px-5 py-3 text-sm font-semibold transition hover:opacity-85"
                      style="background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.86);border:1px solid rgba(255,255,255,0.12)">
                Ở lại xem kết quả
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Breadcrumb header -->
    <div class="flex items-center gap-2 mb-8 text-sm" style="color:var(--color-text-muted)">
      <RouterLink to="/dashboard" class="transition hover:opacity-80"
                  style="color:var(--color-text-muted)">← Dashboard</RouterLink>
      <span>/</span>
      <span style="color:var(--color-text-base)">Kết quả {{ submissionIdDisplay }}</span>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-6">
      <div class="h-72 rounded-2xl animate-pulse" style="background-color:var(--color-surface-02)"></div>
      <div class="h-52 rounded-2xl animate-pulse" style="background-color:var(--color-surface-02)"></div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="text-center py-16" style="color:var(--color-text-muted)">
      <p class="text-4xl mb-3">⚠️</p>
      <p>{{ error }}</p>
      <button @click="fetchResult" class="mt-4 px-4 py-2 rounded-lg text-sm transition hover:opacity-80"
              style="background:linear-gradient(135deg,#4f46e5,#7c3aed);color:white">Thử lại</button>
    </div>

    <!-- AI grading in progress (Speaking / Writing only) -->
    <div v-else-if="!isListeningOrReading && (status === 'pending' || status === 'processing')"
         class="flex flex-col items-center py-24 gap-5">
      <div class="w-14 h-14 border-4 rounded-full animate-spin"
           style="border-color:#7c3aed;border-top-color:transparent"></div>
      <p class="text-base font-semibold" style="color:var(--color-text-base)">Đang phân tích kết quả...</p>
      <p class="text-sm" style="color:var(--color-text-muted)">Trang sẽ tự cập nhật sau vài giây</p>
    </div>

    <!-- ExerciseResult component -->
    <ExerciseResult
      v-else
      :type="type"
      :score="resultScore"
      :passed="pass"
      :max-score="100"
      :answers="answersProp"
      :rubric="rubricProp"
      :error-list="errorList"
      :feedback-text="feedbackText"
      @retry="retry"
      @next-lesson="goNextLesson"
      @dashboard="goDashboard"
    />

  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { progressApi } from '@/api/progress.js'
import ExerciseResult from '@/components/exercise/ExerciseResult.vue'
import UnlockModal from '@/components/UnlockModal.vue'
import { writeCourseRefreshMarker } from '@/utils/courseProgressRefresh.js'

const route = useRoute()
const router = useRouter()

const submissionId = computed(() => route.params.submissionId)
const type = computed(() => (route.query.type || 'listening').toString())

const loading = ref(true)
const error = ref('')
const resultData = ref(null)
const status = ref('completed')
const pollTimer = ref(null)

// Unlock modal state
const unlockModal = reactive({ show: false, lessonTitle: '', xpGained: 0 })
const chapterModal = reactive({ show: false, chapterTitle: '', avgScore: 0 })

const score = computed(() => {
  if (!resultData.value) return null
  if (isListeningOrReading.value) return resultData.value.score ?? null
  return resultData.value.ai_score ?? null
})

const pass = computed(() => (score.value ?? 0) >= 60)
const displayScore = computed(() => score.value ?? 0)
const circumference = 2 * Math.PI * 52
const dashOffset = computed(() => {
  const val = Math.max(0, Math.min(displayScore.value, 100))
  return circumference * (1 - val / 100)
})

const cefrLabel = computed(() => {
  const s = displayScore.value || 0
  if (s <= 39) return 'Below A1'
  if (s <= 59) return 'A1'
  if (s <= 74) return 'A2'
  if (s <= 84) return 'B1'
  if (s <= 92) return 'B2'
  return 'C1/C2'
})

const isListeningOrReading = computed(() => ['listening', 'reading', 'exam'].includes(type.value))
const typeLabel = computed(() => {
  switch (type.value) {
    case 'listening': return 'Listening'
    case 'reading': return 'Reading'
    case 'exam': return 'Exam'
    case 'speaking': return 'Speaking'
    case 'writing': return 'Writing'
    default: return type.value
  }
})

const statusLabel = computed(() => {
  if (status.value === 'completed') return 'Đã chấm'
  if (status.value === 'pending' || status.value === 'processing') return 'Đang chấm'
  if (status.value === 'failed') return 'Thất bại'
  return status.value
})

const statusColor = computed(() => {
  if (status.value === 'completed') return '#16a34a'
  if (status.value === 'pending' || status.value === 'processing') return '#f59e0b'
  if (status.value === 'failed') return '#ef4444'
  return 'var(--color-text-muted)'
})

const detailRows = computed(() => {
  if (!resultData.value?.detail_json || !Array.isArray(resultData.value.detail_json)) return []
  return resultData.value.detail_json.map(item => ({
    q_id: item.q_id,
    question: item.question_text || item.question,
    user_ans: item.user_ans ?? item.user_answer,
    correct_ans: item.correct_ans ?? item.correct_answer,
    correct: item.correct === true || item.is_correct === true,
  }))
})

const totalQuestions = computed(() => detailRows.value.length)
const correctCount = computed(() => detailRows.value.filter(r => r.correct).length)

const rubricScores = computed(() => {
  if (type.value === 'speaking') {
    return [
      { key: 'score_pronunciation', label: 'Pronunciation (35%)', value: resultData.value?.score_pronunciation, color: '#22c55e' },
      { key: 'score_fluency', label: 'Fluency (25%)', value: resultData.value?.score_fluency, color: '#3b82f6' },
      { key: 'score_intonation', label: 'Intonation (20%)', value: resultData.value?.score_intonation, color: '#a855f7' },
      { key: 'score_vocabulary', label: 'Vocabulary (20%)', value: resultData.value?.score_vocabulary, color: '#f59e0b' },
    ]
  }
  if (type.value === 'writing') {
    return [
      { key: 'score_task_achievement', label: 'Task Achievement (25%)', value: resultData.value?.score_task_achievement, color: '#22c55e' },
      { key: 'score_grammar', label: 'Grammar (30%)', value: resultData.value?.score_grammar, color: '#3b82f6' },
      { key: 'score_vocabulary', label: 'Vocabulary (25%)', value: resultData.value?.score_vocabulary, color: '#a855f7' },
      { key: 'score_coherence', label: 'Coherence (20%)', value: resultData.value?.score_coherence, color: '#f59e0b' },
    ]
  }
  return []
})

const feedbackText = computed(() => resultData.value?.feedback_vi || resultData.value?.feedback_text || '')
const errorList = computed(() => resultData.value?.error_list_json || [])
const exerciseId = computed(() => resultData.value?.exercise_id || null)
const submissionIdDisplay = computed(() => `#${submissionId.value}`)
const chapterAverageLabel = computed(() => {
  const raw = Number(chapterModal.avgScore ?? 0)
  if (!Number.isFinite(raw)) return '0'
  return raw.toFixed(1).replace(/\.0$/, '')
})

// ── Props for ExerciseResult component ───────────────────────────────────────
const resultScore = computed(() => score.value ?? 0)

const answersProp = computed(() => {
  if (!isListeningOrReading.value) return []
  if (!Array.isArray(resultData.value?.detail_json)) return []
  return resultData.value.detail_json.map(item => ({
    question_id:    item.q_id,
    question:       item.question_text || item.question || null,
    user_answer:    item.user_ans  ?? item.user_answer  ?? null,
    correct_answer: item.correct_ans ?? item.correct_answer ?? null,
    is_correct:     item.correct === true || item.is_correct === true,
  }))
})

const rubricProp = computed(() => {
  if (type.value === 'speaking') {
    return [
      { criterion: 'Pronunciation', weight: 35, score: resultData.value?.score_pronunciation ?? null, feedback: '' },
      { criterion: 'Fluency',       weight: 25, score: resultData.value?.score_fluency       ?? null, feedback: '' },
      { criterion: 'Intonation',    weight: 20, score: resultData.value?.score_intonation    ?? null, feedback: '' },
      { criterion: 'Vocabulary',    weight: 20, score: resultData.value?.score_vocabulary    ?? null, feedback: '' },
    ]
  }
  if (type.value === 'writing') {
    return [
      { criterion: 'Task Achievement', weight: 25, score: resultData.value?.score_task_achievement ?? null, feedback: '' },
      { criterion: 'Grammar',          weight: 30, score: resultData.value?.score_grammar          ?? null, feedback: '' },
      { criterion: 'Vocabulary',       weight: 25, score: resultData.value?.score_vocabulary       ?? null, feedback: '' },
      { criterion: 'Coherence',        weight: 20, score: resultData.value?.score_coherence        ?? null, feedback: '' },
    ]
  }
  return []
})

function formatDate(ts) {
  const d = new Date(ts)
  return d.toLocaleString('vi-VN')
}

function formatError(err) {
  if (!err) return ''
  if (typeof err === 'string') return err
  if (err.word && err.feedback) return `${err.word}: ${err.feedback}`
  if (err.word && err.suggestion) return `${err.word}: ${err.suggestion}`
  if (err.type && err.suggestion) return `${err.type}: ${err.suggestion}`
  return JSON.stringify(err)
}

async function fetchResultOnce() {
  error.value = ''
  if (isListeningOrReading.value) {
    const res = type.value === 'listening'
      ? await progressApi.getListeningResult(submissionId.value)
      : (type.value === 'reading'
        ? await progressApi.getReadingResult(submissionId.value)
        : await progressApi.getExamResult(submissionId.value))
    const data = res.data?.data ?? res.data
    resultData.value = data
    status.value = 'completed'
  } else if (type.value === 'speaking') {
    const res = await progressApi.getSpeakingStatus(submissionId.value)
    const data = res.data?.data ?? res.data
    resultData.value = data
    status.value = data?.status || 'pending'
  } else if (type.value === 'writing') {
    const res = await progressApi.getWritingStatus(submissionId.value)
    const data = res.data?.data ?? res.data
    resultData.value = data
    status.value = data?.status || 'pending'
  }
}

function handleCompletedResultState() {
  if (resultData.value?.course_id) {
    writeCourseRefreshMarker({
      course_id: resultData.value.course_id,
      chapter_id: resultData.value.chapter_id,
      next_lesson_id: resultData.value.next_lesson_id,
      chapter_completed: resultData.value.chapter_completed,
      chapter_title: resultData.value.chapter_title,
      chapter_avg_score: resultData.value.chapter_avg_score,
    })
  }

  if (resultData.value?.chapter_completed) {
    chapterModal.chapterTitle = resultData.value.chapter_title || 'Chương này'
    chapterModal.avgScore = resultData.value.chapter_avg_score ?? 0
    chapterModal.show = true
    unlockModal.show = false
    return
  }

  if (resultData.value?.next_lesson_id) {
    const exType = resultData.value?.next_exercise_type || 'listening'
    const typeLabels = { listening: 'Listening', speaking: 'Speaking', reading: 'Reading', writing: 'Writing', vocabulary: 'Lesson', grammar: 'Lesson', assessment: 'Lesson' }
    unlockModal.lessonTitle = `Bài ${typeLabels[exType] || exType} tiếp theo đã mở khóa!`
    unlockModal.xpGained = 0
    unlockModal.show = true
  }
}

async function fetchResult() {
  loading.value = true
  try {
    await fetchResultOnce()
    if (!isListeningOrReading.value && status.value !== 'completed') {
      startPolling()
    } else {
      handleCompletedResultState()
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Không thể tải kết quả.'
  } finally {
    loading.value = false
  }
}

function startPolling() {
  stopPolling()
  pollTimer.value = setInterval(async () => {
    try {
      await fetchResultOnce()
      if (status.value === 'completed' || status.value === 'failed') {
        stopPolling()
        if (status.value === 'completed') {
          handleCompletedResultState()
        }
      }
    } catch (e) {
      // keep polling; optionally log
    }
  }, 3000)
}

function stopPolling() {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

function goToCourses() {
  router.push('/courses')
}

function goToCourseDetail() {
  if (resultData.value?.course_id) {
    router.push({
      name: 'course-detail',
      params: { id: resultData.value.course_id },
      query: {
        refresh: String(Date.now()),
        chapter: String(resultData.value?.chapter_id || ''),
      },
    })
    return
  }
  goToCourses()
}

function retry() {
  if (!exerciseId.value) {
    router.push('/dashboard')
    return
  }
  router.push(`/learn/${type.value}/${exerciseId.value}`)
}

function goNextLesson() {
  // Navigate to next lesson's exercise using next_exercise_type + next_exercise_id
  const exType = resultData.value?.next_exercise_type
  const exId   = resultData.value?.next_exercise_id
  const lessonId = resultData.value?.next_lesson_id
  if (exType && exId) {
    router.push({
      name: `learn-${exType}`,
      params: { id: exId },
      query: lessonId ? { lesson_id: lessonId } : undefined,
    })
  } else if (lessonId) {
    router.push({ name: 'lesson-detail', params: { id: lessonId } })
  } else {
    router.push('/dashboard')
  }
}

function goDashboard() {
  router.push('/dashboard')
}

onMounted(fetchResult)
onBeforeUnmount(stopPolling)
</script>

<style scoped>
.chapter-complete-card {
  background:
    radial-gradient(circle at top, rgba(255,255,255,0.14), transparent 34%),
    linear-gradient(160deg, #312e81 0%, #5b21b6 46%, #7c3aed 100%);
  border: 1px solid rgba(255,255,255,0.14);
}

.chapter-complete-orb {
  position: absolute;
  width: 13rem;
  height: 13rem;
  border-radius: 9999px;
  filter: blur(18px);
  opacity: 0.38;
}

.chapter-complete-orb-left {
  top: -4rem;
  left: -3rem;
  background: rgba(251, 191, 36, 0.4);
}

.chapter-complete-orb-right {
  right: -3.5rem;
  bottom: -4rem;
  background: rgba(125, 211, 252, 0.28);
}

.chapter-complete-emblem {
  width: 5.5rem;
  height: 5.5rem;
  display: grid;
  place-items: center;
  font-size: 2.4rem;
  border-radius: 9999px;
  background: linear-gradient(180deg, rgba(255,255,255,0.28), rgba(255,255,255,0.08));
  border: 1px solid rgba(255,255,255,0.22);
  box-shadow: 0 18px 50px rgba(15, 23, 42, 0.35);
  animation: chapter-crown-bob 2.2s ease-in-out infinite;
}

.chapter-complete-pill {
  background: rgba(255,255,255,0.12);
  color: rgba(255,255,255,0.8);
  border: 1px solid rgba(255,255,255,0.14);
}

.chapter-complete-copy {
  color: rgba(255,255,255,0.84);
}

.chapter-complete-stat {
  background: rgba(15,23,42,0.18);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 1.2rem;
  padding: 1rem;
  backdrop-filter: blur(6px);
}

.chapter-complete-stat-label {
  color: rgba(255,255,255,0.62);
}

.chapter-complete-chip {
  background: rgba(250,204,21,0.14);
  color: #fef08a;
  border: 1px solid rgba(250,204,21,0.24);
}

.chapter-complete-button {
  background: linear-gradient(135deg, #f59e0b, #fb7185);
  box-shadow: 0 16px 35px rgba(244, 114, 182, 0.28);
}

.chapter-complete-spark {
  position: absolute;
  color: rgba(255,255,255,0.82);
  animation: chapter-sparkle 2s ease-in-out infinite;
}

.chapter-complete-spark-a {
  top: 1.4rem;
  left: 1.8rem;
  font-size: 1rem;
}

.chapter-complete-spark-b {
  top: 4.2rem;
  right: 2.1rem;
  font-size: 1.2rem;
  animation-delay: .35s;
}

.chapter-complete-spark-c {
  bottom: 6rem;
  left: 2.6rem;
  font-size: 0.95rem;
  animation-delay: .7s;
}

.chapter-burst-enter-active,
.chapter-burst-leave-active {
  transition: opacity .34s ease;
}

.chapter-burst-enter-active .chapter-complete-card,
.chapter-burst-leave-active .chapter-complete-card {
  transition: transform .44s cubic-bezier(.22,1,.36,1), opacity .34s ease;
}

.chapter-burst-enter-from,
.chapter-burst-leave-to {
  opacity: 0;
}

.chapter-burst-enter-from .chapter-complete-card,
.chapter-burst-leave-to .chapter-complete-card {
  opacity: 0;
  transform: translateY(1rem) scale(.92) rotate(-1.2deg);
}

@keyframes chapter-crown-bob {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-0.35rem) scale(1.02); }
}

@keyframes chapter-sparkle {
  0%, 100% { transform: translateY(0) scale(.85); opacity: 0.45; }
  50% { transform: translateY(-0.35rem) scale(1.1); opacity: 1; }
}
</style>
