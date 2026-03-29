<template>
  <div class="flex flex-col" style="min-height: calc(100vh - 64px)">

    <!-- Error toast -->
    <Transition name="toast">
      <div v-if="errorToast"
           class="fixed bottom-6 left-1/2 z-50 px-5 py-3 rounded-xl shadow-xl text-sm font-semibold"
           style="-webkit-transform:translateX(-50%);transform:translateX(-50%);
                  background:#450a0a; border:1px solid rgba(239,68,68,0.5); color:#fca5a5;">
        ⚠️ {{ errorToast }}
      </div>
    </Transition>
    <div v-if="loading" class="p-6 space-y-4">
      <div class="h-6 w-56 rounded-lg animate-pulse" style="background: var(--color-surface-03)"></div>
      <div class="h-2 rounded-full animate-pulse" style="background: var(--color-surface-03)"></div>
      <div class="grid grid-cols-1 md:grid-cols-[6fr_4fr] gap-4">
        <div class="h-64 rounded-2xl animate-pulse" style="background: var(--color-surface-02)"></div>
        <div class="h-48 rounded-2xl animate-pulse" style="background: var(--color-surface-02)"></div>
      </div>
    </div>

    <!-- Not found -->
    <div v-else-if="!exercise" class="flex-1 flex flex-col items-center justify-center gap-3"
         style="color: var(--color-text-muted)">
      <span class="text-5xl">📄</span>
      <p>Không tìm thấy bài tập.</p>
      <RouterLink to="/courses" class="text-sm underline">← Quay lại khoá học</RouterLink>
    </div>

    <template v-else>
      <!-- ── Top bar ────────────────────────────────────────────────────── -->
      <div class="px-4 md:px-6 py-3 flex items-center gap-4 border-b shrink-0"
           style="background: var(--color-surface-01); border-color: var(--color-surface-04)">
        <RouterLink to="/courses" class="text-sm shrink-0 hover:opacity-70 transition"
                    style="color: var(--color-text-muted)">← Quay lại</RouterLink>

        <!-- Progress bar -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs font-medium truncate" style="color: var(--color-text-muted)">
              {{ exercise.title }}
            </span>
            <span class="text-xs shrink-0 ml-2" style="color: var(--color-text-muted)">
              Câu {{ currentQuestionIndex + 1 }}/{{ totalQuestions }} · Đã trả lời {{ answeredCount }}/{{ totalQuestions }}
            </span>
          </div>
          <div class="h-1.5 rounded-full overflow-hidden" style="background: var(--color-surface-03)">
            <div class="h-full rounded-full transition-all duration-500"
                 style="background: linear-gradient(90deg, #4f46e5, #7c3aed)"
                 :style="`width: ${answeredCount / Math.max(totalQuestions, 1) * 100}%`">
            </div>
          </div>
        </div>

        <!-- Timer -->
        <div v-if="timerSeconds > 0" class="shrink-0 flex items-center gap-1.5 px-3 py-1 rounded-lg text-sm font-mono font-semibold"
             :style="timerSeconds <= 60
               ? 'background: rgba(239,68,68,0.1); color: #ef4444'
               : 'background: var(--color-surface-03); color: var(--color-text-base)'">
          ⏱ {{ timerDisplay }}
        </div>
      </div>

      <!-- ── Split pane ─────────────────────────────────────────────────── -->
      <div class="reading-grid flex-1 overflow-hidden"
           :class="{ 'md:grid': true }">

        <!-- LEFT: Passage (60%) -->
        <section class="passage-pane overflow-y-auto border-b md:border-b-0 md:border-r"
                 style="border-color: var(--color-surface-04); background: var(--color-surface-01)"
                 ref="passagePaneRef">

          <!-- Passage toolbar -->
          <div class="sticky top-0 z-10 flex items-center gap-2 px-4 py-2 border-b"
               style="background: var(--color-surface-01); border-color: var(--color-surface-04)">
            <span class="text-xs font-semibold uppercase tracking-wider" style="color: var(--color-text-muted)">
              📖 Bài đọc
            </span>
            <div class="ml-auto flex items-center gap-1">
              <!-- Font size -->
              <button @click="decreaseFontSize" class="w-7 h-7 rounded flex items-center justify-center text-sm transition hover:opacity-80"
                      style="background: var(--color-surface-03); color: var(--color-text-muted)">A-</button>
              <button @click="increaseFontSize" class="w-7 h-7 rounded flex items-center justify-center text-sm font-semibold transition hover:opacity-80"
                      style="background: var(--color-surface-03); color: var(--color-text-muted)">A+</button>
              <!-- Highlight toggle -->
              <button @click="highlightMode = !highlightMode"
                      class="px-2 py-1 rounded text-xs font-medium transition ml-1"
                      :style="highlightMode
                        ? 'background: rgba(99,102,241,0.2); color: #818cf8'
                        : 'background: var(--color-surface-03); color: var(--color-text-muted)'">
                🖊 Highlight
              </button>
            </div>
          </div>

          <!-- Passage text -->
          <div class="px-6 py-5"
               :style="`font-size: ${fontSize}px; line-height: 1.8; color: var(--color-text-base)`">
            <!-- When highlight mode off OR no active question ref: plain text -->
            <p v-if="!highlightMode || !activeHighlight" class="whitespace-pre-wrap">{{ exercise.article_text }}</p>
            <!-- Highlighted passage: before / highlight / after -->
            <template v-else>
              <span class="whitespace-pre-wrap">{{ passageBefore }}</span>
              <mark class="rounded px-0.5"
                    style="background: rgba(99,102,241,0.18); color: inherit">{{ passageHighlighted }}</mark>
              <span class="whitespace-pre-wrap">{{ passageAfter }}</span>
            </template>
          </div>

          <!-- Vocab tooltips banner (if any) -->
          <div v-if="exercise.vocab_tooltip_json?.length" class="mx-6 mb-5 p-3 rounded-xl flex flex-wrap gap-2"
               style="background: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <span class="text-xs font-semibold w-full" style="color: var(--color-text-muted)">💡 Từ vựng hỗ trợ</span>
            <span v-for="v in exercise.vocab_tooltip_json" :key="v.word"
                  class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs"
                  style="background: var(--color-surface-03); color: var(--color-text-base)">
              <strong>{{ v.word }}</strong>
              <span style="color: var(--color-text-muted)">{{ v.ipa }}</span>
              <span>— {{ v.meaning_vi }}</span>
            </span>
          </div>
        </section>

        <!-- RIGHT: Questions (40%) -->
        <section class="questions-pane overflow-y-auto"
                 style="background: var(--color-surface-01)">

          <!-- Navigation dots + questions -->
          <div class="p-4 md:p-5 space-y-4">

            <!-- Nav dots -->
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="text-xs mr-1" style="color: var(--color-text-muted)">Câu:</span>
              <button v-for="(q, i) in exercise.questions" :key="q.id"
                      @click="scrollToQuestion(q.id)"
                      class="w-7 h-7 rounded-full text-xs font-semibold transition"
                      :style="answers[q.id] !== undefined && answers[q.id] !== ''
                        ? 'background: #4f46e5; color: white'
                        : 'background: var(--color-surface-03); color: var(--color-text-muted)'">
                {{ i + 1 }}
              </button>
            </div>

            <!-- Question cards -->
            <div v-for="(q, qi) in exercise.questions" :key="q.id"
                 :id="`question-${q.id}`"
                 class="rounded-2xl p-4 transition cursor-pointer"
                 :style="`background: var(--color-surface-02); border: 1px solid ${activeQuestionId === q.id ? 'rgba(99,102,241,0.5)' : answers[q.id] !== undefined ? 'rgba(79,70,229,0.3)' : 'var(--color-surface-04)'}`"
                 @click="activateQuestion(q)">

              <!-- Question header -->
              <div class="flex items-start gap-2 mb-3">
                <span class="shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                      :style="answers[q.id] !== undefined && answers[q.id] !== ''
                        ? 'background: #4f46e5; color: white'
                        : 'background: var(--color-surface-03); color: var(--color-text-muted)'">
                  {{ qi + 1 }}
                </span>
                <p class="text-sm leading-relaxed font-medium" style="color: var(--color-text-base)">
                  {{ q.question_text }}
                </p>
              </div>

              <!-- Multiple choice options -->
              <template v-if="q.question_type === 'mc' || !q.question_type">
                <div class="space-y-2">
                  <label v-for="opt in q.options" :key="opt.id"
                         class="flex items-center gap-2.5 p-2.5 rounded-xl cursor-pointer transition"
                         :style="`background: var(--color-surface-03); border: 1px solid ${answers[q.id] === opt.id ? '#4f46e5' : 'transparent'}`"
                         @click.stop>
                    <input type="radio" :name="`q${q.id}`" :value="opt.id"
                           v-model="answers[q.id]" class="sr-only" />
                    <span class="w-5 h-5 rounded-full shrink-0 flex items-center justify-center text-xs font-bold"
                          :style="answers[q.id] === opt.id
                            ? 'background: #4f46e5; color: white'
                            : 'background: var(--color-surface-04); color: var(--color-text-muted)'">
                      {{ String.fromCharCode(65 + opt.order - 1) }}
                    </span>
                    <span class="text-sm" style="color: var(--color-text-base)">{{ opt.option_text }}</span>
                  </label>
                </div>
              </template>

              <!-- Gap fill -->
              <template v-else-if="q.question_type === 'gap_fill'">
                <div v-if="q.options?.length" class="flex flex-wrap gap-2">
                  <button v-for="opt in q.options" :key="opt.id"
                          @click.stop="answers[q.id] = opt.id"
                          class="px-3 py-1 rounded-lg text-sm font-medium transition border"
                          :style="answers[q.id] === opt.id
                            ? 'background: #4f46e5; color: white; border-color: #4f46e5'
                            : 'background: var(--color-surface-03); color: var(--color-text-base); border-color: var(--color-surface-04)'">
                    {{ opt.option_text }}
                  </button>
                </div>
                <input v-else type="text"
                       :value="answers[q.id] || ''"
                       @input.stop="answers[q.id] = $event.target.value"
                       placeholder="Nhập câu trả lời..."
                       class="w-full px-3 py-2 rounded-xl text-sm outline-none"
                       style="background: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)"/>
              </template>
            </div>

            <!-- Submit button -->
            <button @click="submit" :disabled="submitting"
                    class="w-full py-4 rounded-2xl font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
                    style="background: linear-gradient(135deg, #4f46e5, #7c3aed)">
              <span v-if="submitting" class="flex items-center justify-center gap-2">
                <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="10" stroke="white" stroke-width="3" stroke-dasharray="30 70"/>
                </svg>
                Đang chấm bài...
              </span>
              <span v-else>
                Nộp bài {{ answeredCount < totalQuestions ? `(${answeredCount}/${totalQuestions} câu)` : '' }}
              </span>
            </button>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getExercise } from '@/api/curriculum.js'
import { progressApi } from '@/api/progress.js'

const route = useRoute()
const router = useRouter()

// ── State ────────────────────────────────────────────────────────────────────
const exercise = ref(null)
const loading = ref(false)
const submitting = ref(false)
const answers = reactive({})

// Error toast
const errorToast = ref('')
let _errorToastTimer = null

function showErrorToast(message) {
  clearTimeout(_errorToastTimer)
  errorToast.value = message
  _errorToastTimer = setTimeout(() => { errorToast.value = '' }, 4000)
}

const passagePaneRef = ref(null)
const fontSize = ref(15)
const highlightMode = ref(true)
const activeQuestionId = ref(null)

// Timer
const timerSeconds = ref(0)
let timerInterval = null

// ── Computed ─────────────────────────────────────────────────────────────────
const totalQuestions = computed(() => exercise.value?.questions?.length ?? 0)

const answeredCount = computed(() => {
  if (!exercise.value) return 0
  return exercise.value.questions.filter(q =>
    answers[q.id] !== undefined && answers[q.id] !== ''
  ).length
})

const currentQuestionIndex = computed(() => {
  if (!exercise.value) return 0
  const idx = exercise.value.questions.findIndex(q =>
    answers[q.id] === undefined || answers[q.id] === ''
  )
  return idx === -1 ? totalQuestions.value - 1 : idx
})

const timerDisplay = computed(() => {
  const m = Math.floor(timerSeconds.value / 60)
  const s = timerSeconds.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

// Active question highlight slicing
const activeHighlight = computed(() => {
  if (!activeQuestionId.value || !exercise.value) return null
  const q = exercise.value.questions.find(q => q.id === activeQuestionId.value)
  if (!q || q.passage_ref_start == null || q.passage_ref_end == null) return null
  return { start: q.passage_ref_start, end: q.passage_ref_end }
})

const passage = computed(() => exercise.value?.article_text ?? '')

const passageBefore = computed(() =>
  activeHighlight.value ? passage.value.slice(0, activeHighlight.value.start) : ''
)
const passageHighlighted = computed(() =>
  activeHighlight.value ? passage.value.slice(activeHighlight.value.start, activeHighlight.value.end) : ''
)
const passageAfter = computed(() =>
  activeHighlight.value ? passage.value.slice(activeHighlight.value.end) : ''
)

// ── Lifecycle ────────────────────────────────────────────────────────────────
onMounted(async () => {
  loading.value = true
  try {
    const res = await getExercise('reading', route.params.id)
    exercise.value = res.data?.data ?? res.data
    // Start timer if any
    const limit = exercise.value?.time_limit ?? 0
    if (limit > 0) {
      timerSeconds.value = limit
      timerInterval = setInterval(() => {
        timerSeconds.value--
        if (timerSeconds.value <= 0) {
          clearInterval(timerInterval)
          submit()
        }
      }, 1000)
    }
  } catch {
    exercise.value = null
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  if (timerInterval) clearInterval(timerInterval)
})

// ── Passage toolbar ──────────────────────────────────────────────────────────
function increaseFontSize() { if (fontSize.value < 22) fontSize.value++ }
function decreaseFontSize() { if (fontSize.value > 12) fontSize.value-- }

// ── Question activation + scroll ─────────────────────────────────────────────
function activateQuestion(q) {
  activeQuestionId.value = q.id
  // Scroll passage to highlighted section
  if (highlightMode.value && q.passage_ref_start != null && passagePaneRef.value) {
    // Estimate scroll position by char ratio
    const ratio = q.passage_ref_start / Math.max(passage.value.length, 1)
    const el = passagePaneRef.value
    nextTick(() => {
      el.scrollTop = ratio * el.scrollHeight
    })
  }
}

function scrollToQuestion(qId) {
  activeQuestionId.value = qId
  nextTick(() => {
    const el = document.getElementById(`question-${qId}`)
    el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

// ── Submit ───────────────────────────────────────────────────────────────────
async function submit() {
  if (submitting.value) return
  submitting.value = true
  if (timerInterval) clearInterval(timerInterval)
  try {
    const res = await progressApi.submitReading({
      exercise_id: exercise.value.id,
      lesson_id: route.query.lesson_id ?? null,
      answers: { ...answers },
    })
    const d = res.data?.data ?? res.data
    const submissionId = d?.id ?? d?.submission_id
    router.push(`/learn/result/${submissionId}?type=reading`)
  } catch (err) {
    showErrorToast(err?.response?.data?.detail || 'Đã có lỗi xảy ra, vui lòng thử lại.')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.reading-grid {
  display: grid;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .reading-grid {
    grid-template-columns: 6fr 4fr;
    height: calc(100vh - 112px); /* subtract top bar height */
  }
  .passage-pane,
  .questions-pane {
    max-height: calc(100vh - 112px);
  }
}

.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translate(-50%, 12px); }
</style>

