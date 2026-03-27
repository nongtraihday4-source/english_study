<template>
  <div class="p-6 max-w-2xl mx-auto">
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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { progressApi } from '@/api/progress.js'
import ExerciseResult from '@/components/exercise/ExerciseResult.vue'

const route = useRoute()
const router = useRouter()

const submissionId = computed(() => route.params.submissionId)
const type = computed(() => (route.query.type || 'listening').toString())

const loading = ref(true)
const error = ref('')
const resultData = ref(null)
const status = ref('completed')
const pollTimer = ref(null)

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

async function fetchResult() {
  loading.value = true
  try {
    await fetchResultOnce()
    if (!isListeningOrReading.value && status.value !== 'completed') {
      startPolling()
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

function retry() {
  if (!exerciseId.value) {
    router.push('/dashboard')
    return
  }
  router.push(`/learn/${type.value}/${exerciseId.value}`)
}

function goNextLesson() {
  // TODO: when backend exposes next_lesson_id, navigate to that lesson
  router.push('/dashboard')
}

function goDashboard() {
  router.push('/dashboard')
}

onMounted(fetchResult)
onBeforeUnmount(stopPolling)
</script>

<style scoped>
</style>
