<template>
  <div class="p-6 max-w-7xl">
    <div v-if="loading" class="grid grid-cols-1 lg:grid-cols-[1fr_260px] gap-5">
      <div class="space-y-4">
        <div class="rounded-3xl h-32 animate-pulse" style="background-color: var(--color-surface-02)" />
        <div v-for="i in 3" :key="i" class="rounded-2xl h-48 animate-pulse" style="background-color: var(--color-surface-02)" />
      </div>
      <div class="rounded-2xl h-64 animate-pulse" style="background-color: var(--color-surface-02)" />
    </div>

    <div v-else-if="error" class="text-center py-16 rounded-2xl" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
      <p class="text-4xl mb-3">⚠️</p>
      <p style="color: #fca5a5">{{ error }}</p>
    </div>

    <div v-else class="space-y-5">
      <header
        class="rounded-3xl p-4 md:p-5"
        style="background: linear-gradient(145deg, color-mix(in srgb, var(--color-primary-600) 26%, transparent), color-mix(in srgb, var(--color-surface-02) 82%, transparent)); border: 1px solid var(--color-surface-04)"
      >
        <div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div class="mb-2 flex flex-wrap items-center gap-2">
              <span class="rounded-full px-2.5 py-1 text-xs font-semibold" style="background-color: var(--color-primary-600)22; color: var(--color-primary-400)">
                Giám sát nghiêm ngặt
              </span>
              <span class="rounded-full px-2.5 py-1 text-xs font-semibold" style="background-color: var(--color-surface-03); color: var(--color-text-muted)">
                {{ exam.cefr_level }}
              </span>
            </div>
            <h1 class="text-2xl font-bold" style="color: var(--color-text-base)">{{ exam.title }}</h1>
            <p class="text-sm mt-1" style="color: var(--color-text-soft)">
              {{ exam.total_questions || questions.length }} câu · {{ exam.time_limit_minutes }} phút
            </p>
          </div>

          <div class="rounded-2xl px-4 py-3 text-right" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <p class="text-xs" style="color: var(--color-text-muted)">Thời gian còn lại</p>
            <p class="text-3xl font-bold" :style="{ color: remainingSeconds <= 60 ? '#f87171' : 'var(--color-text-base)' }">
              {{ mmss }}
            </p>
          </div>
        </div>
      </header>

      <div class="rounded-2xl px-4 py-3 text-sm" style="background-color: rgba(248,113,113,0.12); border: 1px solid rgba(248,113,113,0.25); color: #fca5a5">
        Không được rời tab, đổi cửa sổ, tải lại trang hoặc thoát khỏi màn hình làm bài. Hệ thống sẽ tự động nộp bài nếu phát hiện vi phạm.
      </div>

      <div v-if="sectionTabs.length > 1" class="flex flex-wrap gap-2">
        <button
          v-for="sec in sectionTabs"
          :key="sec"
          @click="activeSection = sec"
          class="rounded-full px-4 py-1.5 text-sm font-semibold"
          :style="activeSection === sec
            ? 'background-color: var(--color-primary-600); color: #fff'
            : 'background-color: var(--color-surface-02); color: var(--color-text-muted); border: 1px solid var(--color-surface-04)'"
        >
          {{ sectionLabel(sec) }}
        </button>
      </div>

      <div class="grid gap-5 lg:grid-cols-[1fr_260px]">
        <main class="space-y-4">
          <article
            v-for="q in visibleQuestions"
            :key="q.id"
            :id="`q-${q.id}`"
            class="rounded-2xl border p-4"
            style="background-color: var(--color-surface-02); border-color: var(--color-surface-04)"
          >
            <div class="mb-3 flex items-start justify-between gap-3">
              <h3 class="font-semibold" style="color: var(--color-text-base)">
                Câu {{ questionIndex(q.id) }}. {{ q.question_text }}
              </h3>
              <button
                @click="toggleFlag(q.id)"
                class="rounded-lg px-2 py-1 text-sm transition"
                :style="isFlagged(q.id)
                  ? 'background-color: rgba(248,113,113,0.16); color: #fca5a5'
                  : 'background-color: var(--color-surface-03); color: var(--color-text-muted)'"
              >⚑</button>
            </div>

            <div class="space-y-2">
              <label
                v-for="opt in q.options || []"
                :key="opt.id"
                class="flex cursor-pointer items-center gap-2 rounded-xl border p-2.5 transition"
                :style="selectedAnswer(q.id) === opt.id
                  ? 'border-color: var(--color-primary-500); background-color: color-mix(in srgb, var(--color-primary-600) 16%, transparent)'
                  : 'border-color: var(--color-surface-04); background-color: var(--color-surface-01)'"
              >
                <input
                  type="radio"
                  :name="`q-${q.id}`"
                  :value="opt.id"
                  :checked="selectedAnswer(q.id) === opt.id"
                  @change="setAnswer(q.id, opt.id)"
                >
                <span style="color: var(--color-text-base)">{{ opt.option_text }}</span>
              </label>
            </div>
          </article>
        </main>

        <aside
          class="lg:sticky lg:top-4 h-fit rounded-2xl border p-4"
          style="background-color: var(--color-surface-02); border-color: var(--color-surface-04)"
        >
          <h4 class="mb-2 text-sm font-semibold" style="color: var(--color-text-base)">Điều hướng câu hỏi</h4>
          <div class="grid grid-cols-5 gap-2">
            <button
              v-for="q in questions"
              :key="`nav-${q.id}`"
              @click="scrollToQuestion(q.id)"
              class="h-9 rounded-lg text-sm font-semibold"
              :style="navStyle(q.id)"
            >{{ questionIndex(q.id) }}</button>
          </div>

          <div class="mt-4 space-y-2 text-xs" style="color: var(--color-text-muted)">
            <p>Đã trả lời: {{ answeredCount }}/{{ questions.length }}</p>
            <p>Đánh dấu cờ: {{ flagged.size }}</p>
          </div>

          <button
            @click="openSubmitModal"
            class="mt-4 w-full rounded-xl px-4 py-2.5 font-semibold transition hover:opacity-80"
            style="background-color: var(--color-primary-600); color: #fff"
          >Nộp bài</button>
        </aside>
      </div>
    </div>

    <div v-if="showSubmitModal" class="fixed inset-0 z-50 grid place-items-center bg-black/50 p-4">
      <div class="w-full max-w-md rounded-2xl border p-5"
           style="background-color: var(--color-surface-01); border-color: var(--color-surface-04)">
        <h3 class="mb-2 text-lg font-semibold" style="color: var(--color-text-base)">Xác nhận nộp bài</h3>
        <p style="color: var(--color-text-muted)">
          Bạn đã trả lời {{ answeredCount }}/{{ questions.length }} câu,
          còn {{ questions.length - answeredCount }} câu chưa trả lời. Nộp bài?
        </p>
        <div class="mt-4 flex justify-end gap-2">
          <button
            @click="showSubmitModal = false"
            class="rounded-lg px-4 py-2 text-sm"
            style="border: 1px solid var(--color-surface-04); color: var(--color-text-muted)"
          >Huỷ</button>
          <button
            @click="submitExam()"
            class="rounded-lg px-4 py-2 text-sm font-medium text-white"
            style="background-color: var(--color-primary-600)"
          >Xác nhận nộp</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'
import { exercisesApi } from '@/api/exercises'
import { progressApi } from '@/api/progress'

const route = useRoute()
const router = useRouter()

const examId = computed(() => Number(route.params.id))
const loading = ref(true)
const error = ref('')
const exam = ref({})
const questions = ref([])
const answers = ref({})
const flagged = ref(new Set())
const activeSection = ref('all')
const showSubmitModal = ref(false)
const submitting = ref(false)
const examSubmitted = ref(false)
const allowRouteNavigation = ref(false)
const violationTriggered = ref(false)

const timerId = ref(null)
const autosaveId = ref(null)
const hiddenTimeoutId = ref(null)
const remainingSeconds = ref(0)

const storageKey = computed(() => `exam_draft_${examId.value}`)

const sectionTabs = computed(() => {
  const s = new Set(questions.value.map((q) => q.section || 'general'))
  return ['all', ...Array.from(s)]
})

const visibleQuestions = computed(() => {
  if (activeSection.value === 'all') return questions.value
  return questions.value.filter((q) => (q.section || 'general') === activeSection.value)
})

const answeredCount = computed(() => Object.keys(answers.value).length)

const mmss = computed(() => {
  const sec = Math.max(0, remainingSeconds.value)
  const m = String(Math.floor(sec / 60)).padStart(2, '0')
  const s = String(sec % 60).padStart(2, '0')
  return `${m}:${s}`
})

function sectionLabel(v) {
  if (v === 'all') return 'Tất cả'
  if (v === 'listening') return 'Listening'
  if (v === 'reading') return 'Reading'
  if (v === 'grammar') return 'Grammar'
  if (v === 'general') return 'General'
  return v
}

function questionIndex(id) {
  return questions.value.findIndex((q) => q.id === id) + 1
}

function selectedAnswer(qid) {
  return answers.value[String(qid)]
}

function setAnswer(qid, val) {
  answers.value = { ...answers.value, [String(qid)]: val }
}

function toggleFlag(qid) {
  const next = new Set(flagged.value)
  if (next.has(qid)) next.delete(qid)
  else next.add(qid)
  flagged.value = next
}

function isFlagged(qid) {
  return flagged.value.has(qid)
}

function navStyle(qid) {
  const key = String(qid)
  if (flagged.value.has(qid)) return 'background-color: rgba(248,113,113,0.16); color: #fca5a5'
  if (Object.prototype.hasOwnProperty.call(answers.value, key)) return 'background-color: rgba(74,222,128,0.16); color: #86efac'
  return 'background-color: var(--color-surface-01); color: var(--color-text-soft); border: 1px solid var(--color-surface-04)'
}

function scrollToQuestion(qid) {
  const el = document.getElementById(`q-${qid}`)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function openSubmitModal() {
  showSubmitModal.value = true
}

function isExamActive() {
  return !loading.value && !error.value && !examSubmitted.value && !submitting.value
}

function handleBeforeUnload(event) {
  if (!isExamActive()) return
  event.preventDefault()
  event.returnValue = 'Bạn đang làm bài thi. Nếu thoát khỏi trang, bài sẽ bị coi là vi phạm và có thể bị nộp sớm.'
}

function clearHiddenTimeout() {
  if (hiddenTimeoutId.value) {
    window.clearTimeout(hiddenTimeoutId.value)
    hiddenTimeoutId.value = null
  }
}

async function triggerViolationAutoSubmit(reason) {
  if (!isExamActive() || violationTriggered.value) return
  violationTriggered.value = true
  showSubmitModal.value = false

  if (!document.hidden) {
    window.alert('Phát hiện rời màn hình thi. Hệ thống sẽ nộp bài sớm do vi phạm.')
  }

  await submitExam({ auto: true, violation: true, reason })
}

function handleVisibilityChange() {
  if (!isExamActive()) return
  if (document.hidden) {
    clearHiddenTimeout()
    hiddenTimeoutId.value = window.setTimeout(() => {
      if (document.hidden) {
        triggerViolationAutoSubmit('tab_hidden')
      }
    }, 3000)
    return
  }
  clearHiddenTimeout()
}

function handlePageHide() {
  if (!isExamActive()) return
  triggerViolationAutoSubmit('page_hide')
}

function mountProctoringGuards() {
  window.addEventListener('beforeunload', handleBeforeUnload)
  document.addEventListener('visibilitychange', handleVisibilityChange)
  window.addEventListener('pagehide', handlePageHide)
}

function unmountProctoringGuards() {
  window.removeEventListener('beforeunload', handleBeforeUnload)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  window.removeEventListener('pagehide', handlePageHide)
  clearHiddenTimeout()
}

function saveDraft() {
  const payload = {
    answers: answers.value,
    flagged: Array.from(flagged.value),
    remainingSeconds: remainingSeconds.value,
    savedAt: Date.now(),
  }
  localStorage.setItem(storageKey.value, JSON.stringify(payload))
}

function restoreDraftIfAny() {
  const raw = localStorage.getItem(storageKey.value)
  if (!raw) return
  try {
    const draft = JSON.parse(raw)
    const shouldRestore = window.confirm('Phát hiện bài thi chưa hoàn thành. Bạn muốn tiếp tục bài thi?')
    if (!shouldRestore) return

    answers.value = draft.answers || {}
    flagged.value = new Set(Array.isArray(draft.flagged) ? draft.flagged : [])
    if (typeof draft.remainingSeconds === 'number' && draft.remainingSeconds > 0) {
      remainingSeconds.value = draft.remainingSeconds
    }
  } catch {
    // ignore invalid draft
  }
}

function startTimer() {
  if (!remainingSeconds.value) return
  timerId.value = window.setInterval(() => {
    if (remainingSeconds.value <= 1) {
      remainingSeconds.value = 0
      window.clearInterval(timerId.value)
      submitExam({ auto: true, reason: 'timeout' })
      return
    }
    remainingSeconds.value -= 1
  }, 1000)
}

async function submitExam(options = {}) {
  const opts = {
    auto: false,
    violation: false,
    reason: 'manual',
    ...options,
  }

  if (submitting.value) return
  submitting.value = true
  showSubmitModal.value = false

  try {
    const spent = (exam.value.time_limit_minutes || 0) * 60 - remainingSeconds.value
    const payload = {
      exam_id: examId.value,
      answers: answers.value,
      time_spent_seconds: Math.max(0, spent),
    }
    const res = await progressApi.submitExam(payload)
    const data = res.data?.data ?? res.data

    const scoreMap = JSON.parse(localStorage.getItem('exam_scores_v1') || '{}')
    scoreMap[String(examId.value)] = { done: true, score: data?.score ?? 0 }
    localStorage.setItem('exam_scores_v1', JSON.stringify(scoreMap))

    localStorage.removeItem(storageKey.value)
    examSubmitted.value = true
    allowRouteNavigation.value = true
    unmountProctoringGuards()
    router.push(`/learn/result/${data.id}?type=exam${opts.violation ? '&violation=1' : ''}`)
  } catch (e) {
    if (!opts.auto) {
      error.value = 'Nộp bài thất bại. Vui lòng thử lại.'
    }
    if (opts.violation) {
      violationTriggered.value = false
    }
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    const res = await exercisesApi.getExamDetail(examId.value)
    const data = res.data?.data ?? res.data

    exam.value = data || {}
    questions.value = Array.isArray(data?.questions) ? data.questions : []
    remainingSeconds.value = (data?.time_limit_minutes || 0) * 60

    restoreDraftIfAny()

    if (questions.value.length > 0) {
      const firstSection = questions.value[0].section || 'general'
      activeSection.value = firstSection
    }

    startTimer()
    autosaveId.value = window.setInterval(saveDraft, 30000)
    mountProctoringGuards()
  } catch (e) {
    error.value = 'Không thể tải đề thi.'
  } finally {
    loading.value = false
  }
})

onBeforeRouteLeave(() => {
  if (allowRouteNavigation.value || examSubmitted.value) return true
  if (!isExamActive()) return true

  const confirmed = window.confirm(
    'Bạn đang cố rời khỏi màn hình làm bài. Hệ thống sẽ nộp bài sớm do vi phạm. Bạn có chắc chắn muốn rời?'
  )

  if (!confirmed) return false
  triggerViolationAutoSubmit('route_leave')
  return false
})

onBeforeUnmount(() => {
  if (timerId.value) window.clearInterval(timerId.value)
  if (autosaveId.value) window.clearInterval(autosaveId.value)
  unmountProctoringGuards()
  if (!examSubmitted.value) saveDraft()
})
</script>
