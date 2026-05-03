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

    <!-- Loading skeleton -->
    <div v-if="loading" class="p-6 space-y-4">
      <div class="h-6 w-48 rounded-lg animate-pulse" style="background: var(--color-surface-03)"></div>
      <div class="h-2 rounded-full animate-pulse" style="background: var(--color-surface-03)"></div>
      <div class="h-48 rounded-2xl animate-pulse" style="background: var(--color-surface-02)"></div>
    </div>

    <!-- Not found -->
    <div v-else-if="!exercise" class="flex-1 flex flex-col items-center justify-center gap-3"
         style="color: var(--color-text-muted)">
      <span class="text-5xl">🎧</span>
      <p>Không tìm thấy bài tập.</p>
      <RouterLink to="/courses" class="text-sm underline">← Quay lại khoá học</RouterLink>
    </div>

    <template v-else>
      <!-- ── Top bar ───────────────────────────────────────────────── -->
      <div class="px-4 md:px-6 py-3 flex items-center gap-4 border-b"
           style="background: var(--color-surface-01); border-color: var(--color-surface-04)">
        <RouterLink to="/courses" class="text-sm shrink-0 hover:opacity-70 transition"
                    style="color: var(--color-text-muted)">← Quay lại</RouterLink>

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

        <!-- Split view toggle -->
        <button @click="splitMode = !splitMode"
                class="shrink-0 px-3 py-1 rounded-lg text-xs font-semibold transition hover:opacity-80"
                :style="splitMode
                  ? 'background: rgba(99,102,241,0.15); color: #818cf8'
                  : 'background: var(--color-surface-03); color: var(--color-text-muted)'">
          ⊞ Split
        </button>
      </div>

      <!-- ── Split pane body ─────────────────────────────────────── -->
      <div class="flex-1 overflow-hidden" :class="splitMode ? 'flex flex-col md:flex-row' : 'flex flex-col'">

        <!-- LEFT PANE — Audio player (40%) -->
        <aside class="overflow-y-auto p-4 md:p-6 border-b"
               :class="splitMode ? 'md:w-2/5 md:border-b-0 md:border-r' : ''"
               style="background: var(--color-surface-01); border-color: var(--color-surface-04)">

          <!-- CEFR badge -->
          <span class="inline-block px-2 py-0.5 rounded text-xs font-semibold mb-4"
                style="background: rgba(79,70,229,0.15); color: #818cf8">
            {{ exercise.cefr_level }}
          </span>

          <!-- Context hint -->
          <p v-if="exercise.context_hint" class="text-sm mb-4 p-3 rounded-xl"
             style="background: var(--color-surface-02); color: var(--color-text-muted)">
            {{ exercise.context_hint }}
          </p>

          <!-- Audio player card -->
          <div class="rounded-2xl p-5" style="background: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <p class="text-xs font-semibold uppercase tracking-wider mb-4" style="color: var(--color-text-muted)">
              🎧 Đoạn âm thanh
            </p>

            <!-- Native audio (hidden — we drive it manually) -->
            <audio
              ref="audioRef"
              :src="exercise.audio_url"
              @timeupdate="onTimeUpdate"
              @loadedmetadata="onMetadata"
              @ended="onEnded"
              class="hidden"
            ></audio>

            <!-- No audio fallback -->
            <p v-if="!exercise.audio_url" class="text-sm text-center py-6"
               style="color: var(--color-text-muted)">Không có file âm thanh.</p>

            <template v-else>
              <!-- Play/Pause button -->
              <div class="flex justify-center mb-4">
                <button
                  @click="togglePlay"
                  :disabled="!canPlay"
                  class="w-20 h-20 rounded-full flex items-center justify-center transition shadow-lg disabled:opacity-40 disabled:cursor-not-allowed"
                  style="background: linear-gradient(135deg, #4f46e5, #7c3aed)"
                  :title="!canPlay ? 'Đã hết lượt nghe' : (isPlaying ? 'Tạm dừng' : 'Phát')"
                >
                  <!-- Play icon -->
                  <svg v-if="!isPlaying" class="w-8 h-8 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z"/>
                  </svg>
                  <!-- Pause icon -->
                  <svg v-else class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                  </svg>
                </button>
              </div>

              <!-- Time display -->
              <div class="flex justify-between text-xs font-mono mb-2"
                   style="color: var(--color-text-muted)">
                <span>{{ formatTime(currentTime) }}</span>
                <span>{{ formatTime(duration) }}</span>
              </div>

              <!-- Seek progress bar -->
              <div
                class="h-2 rounded-full cursor-pointer relative"
                style="background: var(--color-surface-04)"
                @click="seek"
                ref="seekBarRef"
              >
                <div class="h-full rounded-full transition-all"
                     style="background: linear-gradient(90deg, #4f46e5, #7c3aed)"
                     :style="`width: ${progressPercent}%`">
                </div>
                <!-- Thumb -->
                <div class="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full shadow"
                     style="background: #7c3aed"
                     :style="`left: calc(${progressPercent}% - 6px)`">
                </div>
              </div>

              <!-- Plays remaining -->
              <div v-if="exercise.max_plays > 0" class="mt-4 flex items-center justify-between">
                <span class="text-xs" style="color: var(--color-text-muted)">Lượt nghe</span>
                <span class="text-xs font-semibold px-2 py-0.5 rounded-full"
                      :style="playsRemaining === 0
                        ? 'background: rgba(239,68,68,0.1); color: #f87171'
                        : 'background: rgba(34,197,94,0.1); color: #4ade80'">
                  {{ playsRemaining > 0 ? `Còn ${playsRemaining} lần` : 'Hết lượt nghe' }}
                </span>
              </div>

              <!-- Speed control -->
              <div class="mt-4 flex items-center gap-2">
                <span class="text-xs" style="color: var(--color-text-muted)">Tốc độ:</span>
                <button v-for="r in [0.75, 1, 1.25]" :key="r"
                        @click="setRate(r)"
                        class="px-2 py-0.5 rounded text-xs font-semibold transition"
                        :style="playbackRate === r
                          ? 'background: #4f46e5; color: white'
                          : 'background: var(--color-surface-03); color: var(--color-text-muted)'">
                  {{ r }}x
                </button>
              </div>
            </template>
          </div>

          <!-- Transcript (show after exercise is submitted) -->
          <Transition name="fade">
            <div v-if="submitted && exercise.transcript_preview"
                 class="mt-4 rounded-2xl p-4"
                 style="background: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
              <p class="text-xs font-semibold uppercase tracking-wider mb-2"
                 style="color: var(--color-text-muted)">📄 Transcript</p>
              <p class="text-sm leading-relaxed whitespace-pre-wrap"
                 style="color: var(--color-text-base)">{{ exercise.transcript_preview }}</p>
            </div>
          </Transition>
        </aside>

        <!-- RIGHT PANE — Questions (60%) -->
        <main class="overflow-y-auto p-4 md:p-6 space-y-5" :class="splitMode ? 'md:w-3/5' : ''"
              style="background: var(--color-surface-01)">

          <div v-for="(q, qi) in exercise.questions" :key="q.id"
               :id="`question-${q.id}`"
               class="rounded-2xl p-5 transition"
               :style="`background: var(--color-surface-02); border: 1px solid ${answers[q.id] !== undefined ? 'rgba(79,70,229,0.4)' : 'var(--color-surface-04)'}`">

            <!-- Question header -->
            <div class="flex items-start gap-3 mb-4">
              <span class="shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold"
                    :style="answers[q.id] !== undefined
                      ? 'background: #4f46e5; color: white'
                      : 'background: var(--color-surface-03); color: var(--color-text-muted)'">
                {{ qi + 1 }}
              </span>
              <p class="text-sm leading-relaxed font-medium" style="color: var(--color-text-base)">
                {{ q.question_text }}
              </p>
            </div>

            <!-- Multiple choice -->
            <template v-if="q.question_type === 'mc'">
              <div class="space-y-2">
                <label v-for="opt in q.options" :key="opt.id"
                       class="flex items-center gap-3 p-3 rounded-xl cursor-pointer transition"
                       :style="`background: var(--color-surface-03); border: 1px solid ${answers[q.id] === opt.id ? '#4f46e5' : 'transparent'}`">
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
              <div v-if="q.options && q.options.length" class="flex flex-wrap gap-2">
                <button v-for="opt in q.options" :key="opt.id"
                        @click="answers[q.id] = opt.id"
                        class="px-3 py-1.5 rounded-lg text-sm font-medium transition border"
                        :style="answers[q.id] === opt.id
                          ? 'background: #4f46e5; color: white; border-color: #4f46e5'
                          : 'background: var(--color-surface-03); color: var(--color-text-base); border-color: var(--color-surface-04)'">
                  {{ opt.option_text }}
                </button>
              </div>
              <div v-else class="mt-1">
                <input type="text"
                       :value="gapAnswers[q.id] || ''"
                       @input="gapAnswers[q.id] = $event.target.value; answers[q.id] = $event.target.value"
                       placeholder="Nhập câu trả lời..."
                       class="w-full px-3 py-2 rounded-xl text-sm outline-none transition"
                       style="background: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)"/>
              </div>
            </template>

            <!-- Drag & drop -->
            <template v-else-if="q.question_type === 'drag_drop'">
              <!-- Answer slots -->
              <div class="flex flex-wrap gap-2 mb-3 min-h-10 p-2 rounded-xl border-2 border-dashed"
                   style="border-color: var(--color-surface-04)"
                   @dragover.prevent
                   @drop="dropToSlot(q.id, $event)">
                <span v-if="!dragSlots[q.id]?.length" class="text-xs self-center"
                      style="color: var(--color-text-muted)">Kéo từ vào đây...</span>
                <span v-for="(itemId, idx) in (dragSlots[q.id] || [])" :key="idx"
                      class="px-3 py-1 rounded-lg text-sm font-medium cursor-grab"
                      style="background: #4f46e5; color: white"
                      draggable="true"
                      @dragstart="dragStartPlaced(q.id, idx, $event)"
                      @click="removePlaced(q.id, idx)">
                  {{ optionTextById(q, itemId) }} ✕
                </span>
              </div>
              <!-- Word bank -->
              <div class="flex flex-wrap gap-2">
                <span v-for="opt in availableOptions(q)" :key="opt.id"
                      class="px-3 py-1 rounded-lg text-sm font-medium cursor-grab transition border"
                      style="background: var(--color-surface-03); color: var(--color-text-base); border-color: var(--color-surface-04)"
                      draggable="true"
                      @dragstart="dragStartBank(opt.id, $event)"
                      @click="placeOption(q.id, opt.id)">
                  {{ opt.option_text }}
                </span>
              </div>
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

        </main>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getExercise } from '@/api/curriculum.js'
import { progressApi } from '@/api/progress.js'

const route = useRoute()
const router = useRouter()

// ── State ────────────────────────────────────────────────────────────────────
const exercise = ref(null)
const loading = ref(false)
const submitting = ref(false)
const submitted = ref(false)
const splitMode = ref(true)

// Audio
const audioRef = ref(null)
const seekBarRef = ref(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const playbackRate = ref(1)
const playsUsed = ref(0)

// Answers
const answers = reactive({})      // { [q.id]: option_id | text }
const gapAnswers = reactive({})   // text answers for free-form gap fill
const dragSlots = reactive({})    // { [q.id]: [option_id, ...] }
const dragItem = ref(null)        // { source: 'bank'|'placed', optionId, qId, idx }

// Error toast
const errorToast = ref('')
let _errorToastTimer = null

function showErrorToast(message) {
  clearTimeout(_errorToastTimer)
  errorToast.value = message
  _errorToastTimer = setTimeout(() => { errorToast.value = '' }, 4000)
}

// Timer
const timerSeconds = ref(0)
let timerInterval = null

// ── Computed ─────────────────────────────────────────────────────────────────
const totalQuestions = computed(() => exercise.value?.questions?.length ?? 0)

const answeredCount = computed(() => {
  if (!exercise.value) return 0
  return exercise.value.questions.filter(q => {
    if (q.question_type === 'drag_drop') return (dragSlots[q.id]?.length ?? 0) > 0
    return answers[q.id] !== undefined && answers[q.id] !== ''
  }).length
})

const currentQuestionIndex = computed(() => {
  if (!exercise.value) return 0
  const idx = exercise.value.questions.findIndex(q => {
    if (q.question_type === 'drag_drop') return !(dragSlots[q.id]?.length > 0)
    return answers[q.id] === undefined || answers[q.id] === ''
  })
  return idx === -1 ? totalQuestions.value - 1 : idx
})

const progressPercent = computed(() =>
  duration.value > 0 ? (currentTime.value / duration.value) * 100 : 0
)

const playsRemaining = computed(() => {
  if (!exercise.value || exercise.value.max_plays === 0) return null // unlimited
  return Math.max(0, exercise.value.max_plays - playsUsed.value)
})

const canPlay = computed(() => playsRemaining.value === null || playsRemaining.value > 0)

const timerDisplay = computed(() => {
  const m = Math.floor(timerSeconds.value / 60)
  const s = timerSeconds.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

// ── Lifecycle ────────────────────────────────────────────────────────────────
onMounted(async () => {
  loading.value = true
  try {
    const res = await getExercise('listening', route.params.id)
    exercise.value = res.data?.data ?? res.data
    // Init drag slots for drag_drop questions
    exercise.value?.questions?.forEach(q => {
      if (q.question_type === 'drag_drop') dragSlots[q.id] = []
    })
    // Start timer if set
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
  if (audioRef.value && isPlaying.value) {
    audioRef.value.pause()
  }
})

// Keep drag_drop answers synced
watch(dragSlots, (slots) => {
  if (!exercise.value) return
  exercise.value.questions.forEach(q => {
    if (q.question_type === 'drag_drop') {
      answers[q.id] = slots[q.id] ?? []
    }
  })
}, { deep: true })

// ── Audio control ────────────────────────────────────────────────────────────
function togglePlay() {
  if (!audioRef.value || !canPlay.value) return
  if (isPlaying.value) {
    audioRef.value.pause()
    isPlaying.value = false
  } else {
    audioRef.value.play()
    isPlaying.value = true
    if (currentTime.value === 0 || audioRef.value.ended) {
      playsUsed.value++
    }
  }
}

function onTimeUpdate() {
  currentTime.value = audioRef.value?.currentTime ?? 0
}

function onMetadata() {
  duration.value = audioRef.value?.duration ?? 0
}

function onEnded() {
  isPlaying.value = false
  currentTime.value = 0
  if (audioRef.value) audioRef.value.currentTime = 0
}

function seek(e) {
  if (!seekBarRef.value || !audioRef.value || duration.value === 0) return
  const rect = seekBarRef.value.getBoundingClientRect()
  const ratio = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width))
  audioRef.value.currentTime = ratio * duration.value
  currentTime.value = audioRef.value.currentTime
}

function setRate(r) {
  playbackRate.value = r
  if (audioRef.value) audioRef.value.playbackRate = r
}

function formatTime(sec) {
  if (!sec || isNaN(sec)) return '0:00'
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m}:${String(s).padStart(2, '0')}`
}

// ── Drag & Drop helpers ──────────────────────────────────────────────────────
function optionTextById(q, id) {
  return q.options.find(o => o.id === id)?.option_text ?? id
}

function availableOptions(q) {
  const placed = dragSlots[q.id] ?? []
  return q.options.filter(o => !placed.includes(o.id))
}

function dragStartBank(optionId, e) {
  dragItem.value = { source: 'bank', optionId }
  e.dataTransfer.effectAllowed = 'move'
}

function dragStartPlaced(qId, idx, e) {
  dragItem.value = { source: 'placed', qId, idx, optionId: dragSlots[qId][idx] }
  e.dataTransfer.effectAllowed = 'move'
}

function dropToSlot(qId, e) {
  e.preventDefault()
  if (!dragItem.value) return
  if (dragItem.value.source === 'placed' && dragItem.value.qId === qId) {
    dragItem.value = null
    return
  }
  if (dragItem.value.source === 'placed') {
    // remove from old question
    dragSlots[dragItem.value.qId].splice(dragItem.value.idx, 1)
  }
  if (!dragSlots[qId]) dragSlots[qId] = []
  dragSlots[qId].push(dragItem.value.optionId)
  dragItem.value = null
}

function placeOption(qId, optionId) {
  if (!dragSlots[qId]) dragSlots[qId] = []
  dragSlots[qId].push(optionId)
}

function removePlaced(qId, idx) {
  dragSlots[qId].splice(idx, 1)
}

// ── Submit ───────────────────────────────────────────────────────────────────
async function submit() {
  if (submitting.value) return
  submitting.value = true
  if (timerInterval) clearInterval(timerInterval)
  try {
    const payload = {
      exercise_id: exercise.value.id,
      lesson_id: route.query.lesson_id ?? null,
      answers: { ...answers },
    }
    const res = await progressApi.submitListening(payload)
    const d = res.data?.data ?? res.data
    const submissionId = d?.id ?? d?.submission_id
    submitted.value = true
    router.push({
      path: `/learn/result/${submissionId}`,
      query: {
        type: 'listening',
        lesson_id: route.query.lesson_id ?? undefined,
      },
    })
  } catch (err) {
    showErrorToast(err?.response?.data?.detail || 'Đã có lỗi xảy ra, vui lòng thử lại.')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translate(-50%, 12px); }
</style>

