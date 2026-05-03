<template>
  <div class="max-w-2xl mx-auto px-4 py-8">

    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-2">
        <RouterLink
          :to="passage ? `/skill-practice/passages/${passage.topic_slug}?level=${passage.cefr_level}` : '/skill-practice'"
          class="text-sm hover:opacity-70 transition"
          style="color:var(--color-text-muted)"
        >
          ← Quay lại
        </RouterLink>
      </div>
      <span class="text-xs px-3 py-1 rounded-full font-semibold" style="background:rgba(6,182,212,0.12);color:#22d3ee">
        🎧 Chính tả
      </span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="space-y-4">
      <div class="h-8 w-2/3 rounded-xl animate-pulse" style="background:var(--color-surface-03)" />
      <div class="h-32 rounded-2xl animate-pulse" style="background:var(--color-surface-03)" />
    </div>

    <!-- Passage loaded -->
    <template v-else-if="passage">

      <!-- Title + meta -->
      <h1 class="text-lg font-bold mb-1" style="color:var(--color-text-base)">{{ passage.title }}</h1>
      <div class="flex items-center gap-2 mb-6 flex-wrap">
        <span class="text-xs px-2 py-0.5 rounded-full" style="background:var(--color-surface-04);color:var(--color-text-muted)">
          {{ passage.cefr_level }}
        </span>
        <span class="text-xs" style="color:var(--color-text-muted)">{{ passage.topic }}</span>
        <span class="text-xs" style="color:var(--color-text-muted)">·</span>
        <span class="text-xs" style="color:var(--color-text-muted)">{{ passage.word_count }} từ</span>
      </div>

      <!-- Mode toggle -->
      <div class="flex gap-2 mb-6 p-1 rounded-2xl" style="background:var(--color-surface-03)">
        <button
          @click="switchMode('sentence')"
          class="flex-1 py-2 rounded-xl text-sm font-semibold transition"
          :style="mode === 'sentence'
            ? 'background:var(--color-primary-600);color:#fff'
            : 'color:var(--color-text-muted)'"
        >
          📝 Theo câu
        </button>
        <button
          @click="switchMode('full')"
          class="flex-1 py-2 rounded-xl text-sm font-semibold transition"
          :style="mode === 'full'
            ? 'background:var(--color-primary-600);color:#fff'
            : 'color:var(--color-text-muted)'"
        >
          📄 Cả bài
        </button>
      </div>

      <!-- ───────── SENTENCE MODE ───────── -->
      <template v-if="mode === 'sentence'">

        <!-- Progress bar -->
        <div class="flex items-center gap-3 mb-5">
          <div class="flex gap-1.5 flex-wrap flex-1">
            <button
              v-for="(s, i) in sentences"
              :key="i"
              @click="goToSentence(i)"
              class="w-6 h-6 rounded-full text-xs font-bold transition"
              :style="sentenceStyle(i)"
            >
              {{ i + 1 }}
            </button>
          </div>
          <span class="text-xs font-medium shrink-0" style="color:var(--color-text-muted)">
            {{ completedCount }}/{{ sentences.length }}
          </span>
        </div>

        <!-- Current sentence exercise -->
        <div class="rounded-2xl p-5" style="background:var(--color-surface-02);border:1px solid var(--color-surface-04)">

          <p class="text-xs font-semibold mb-4 uppercase tracking-wide" style="color:var(--color-text-muted)">
            Câu {{ currentIndex + 1 }} / {{ sentences.length }}
          </p>

          <!-- Audio controls -->
          <div class="flex items-center gap-3 mb-5">
            <button
              @click="playCurrent"
              :disabled="ttsLoading"
              class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
              style="background:rgba(6,182,212,0.12);color:#22d3ee;border:1px solid rgba(6,182,212,0.25)"
            >
              <span v-if="ttsLoading" class="animate-spin">⏳</span>
              <span v-else-if="ttsPlaying">⏹ Đang phát</span>
              <span v-else>▶ Nghe câu</span>
            </button>

            <!-- Speed control -->
            <div class="flex gap-1">
              <button
                v-for="sp in [0.75, 1.0, 1.25]"
                :key="sp"
                @click="playbackRate = sp"
                class="px-2.5 py-1 rounded-lg text-xs font-medium transition"
                :style="playbackRate === sp
                  ? 'background:rgba(6,182,212,0.2);color:#22d3ee;border:1px solid rgba(6,182,212,0.4)'
                  : 'background:var(--color-surface-04);color:var(--color-text-muted)'"
              >
                {{ sp }}x
              </button>
            </div>

            <span v-if="playCount > 0" class="text-xs ml-auto" style="color:var(--color-text-muted)">
              Đã nghe {{ playCount }}x
            </span>
          </div>

          <!-- Input -->
          <div class="mb-4">
            <input
              ref="inputRef"
              v-model="userInput"
              @keydown.enter="checkAnswer"
              :disabled="sentenceState === 'correct'"
              type="text"
              placeholder="Gõ câu bạn nghe được..."
              class="w-full px-4 py-3 rounded-xl text-sm outline-none transition"
              style="background:var(--color-surface-03);border:1px solid var(--color-surface-04);color:var(--color-text-base)"
            />
          </div>

          <!-- Diff result -->
          <Transition name="fade">
            <div
              v-if="sentenceState !== 'idle'"
              class="mb-4 px-4 py-3 rounded-xl text-sm leading-loose"
              :style="sentenceState === 'correct'
                ? 'background:rgba(34,197,94,0.07);border:1px solid rgba(34,197,94,0.2)'
                : 'background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.2)'"
            >
              <span
                v-for="(token, ti) in diffResult"
                :key="ti"
                :style="token.match
                  ? 'color:#86efac'
                  : token.word === `[${token.correct_word}]`
                    ? 'color:#9ca3af;text-decoration:line-through'
                    : 'color:#fca5a5;text-decoration:underline wavy'"
              >
                {{ token.word }}{{ ti < diffResult.length - 1 ? ' ' : '' }}
              </span>
              <span v-if="sentenceState === 'correct'" class="ml-2 font-bold" style="color:#86efac">✓ Đúng!</span>
              <span v-else class="ml-2 text-xs" style="color:var(--color-text-muted)">
                Độ chính xác: {{ lastAccuracy }}%
              </span>
            </div>
          </Transition>

          <!-- Hint -->
          <Transition name="fade">
            <div
              v-if="showHint && hint"
              class="mb-4 px-4 py-2.5 rounded-xl text-sm"
              style="background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.2);color:#fbbf24"
            >
              💡 Gợi ý: <span class="font-mono tracking-wider">{{ hint }}</span>
            </div>
          </Transition>

          <!-- Show answer after 3 fails -->
          <Transition name="fade">
            <div
              v-if="showAnswer"
              class="mb-4 px-4 py-3 rounded-xl text-sm"
              style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2)"
            >
              <p class="text-xs font-semibold mb-1" style="color:#818cf8">Đáp án:</p>
              <p style="color:var(--color-text-base)">{{ currentSentence?.text }}</p>
              <p v-if="currentSentence?.translation_vi" class="text-xs mt-1" style="color:var(--color-text-muted)">
                {{ currentSentence.translation_vi }}
              </p>
            </div>
          </Transition>

          <!-- Actions -->
          <div class="flex gap-2 flex-wrap">
            <button
              v-if="sentenceState !== 'correct'"
              @click="checkAnswer"
              :disabled="!userInput.trim() || !playCount || checkLoading"
              class="px-5 py-2 rounded-xl text-sm font-semibold transition hover:opacity-80"
              :style="(!userInput.trim() || !playCount || checkLoading)
                ? 'background:var(--color-surface-04);color:var(--color-text-muted);cursor:not-allowed'
                : 'background:rgba(99,102,241,0.15);color:#818cf8;border:1px solid rgba(99,102,241,0.3)'"
            >
              {{ checkLoading ? '...' : 'Kiểm tra' }}
            </button>

            <button
              v-if="sentenceState === 'wrong' && failCount >= 2 && !showHint"
              @click="showHint = true"
              class="px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
              style="background:rgba(251,191,36,0.1);color:#fbbf24;border:1px solid rgba(251,191,36,0.25)"
            >
              💡 Gợi ý
            </button>

            <button
              v-if="sentenceState === 'wrong' && failCount >= 3 && !showAnswer"
              @click="showAnswer = true"
              class="px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
              style="background:rgba(99,102,241,0.1);color:#818cf8;border:1px solid rgba(99,102,241,0.2)"
            >
              👁 Xem đáp án
            </button>

            <button
              v-if="sentenceState === 'wrong'"
              @click="resetSentence"
              class="px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
              style="background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)"
            >
              Thử lại
            </button>

            <button
              v-if="sentenceState === 'correct' || showAnswer"
              @click="nextSentence"
              class="px-5 py-2 rounded-xl text-sm font-semibold transition hover:opacity-80"
              style="background:var(--color-primary-600);color:#fff"
            >
              {{ currentIndex < sentences.length - 1 ? 'Câu tiếp →' : 'Xem kết quả →' }}
            </button>
          </div>
        </div>
      </template>

      <!-- ───────── FULL PASSAGE MODE ───────── -->
      <template v-else>
        <div class="rounded-2xl p-5 mb-4" style="background:var(--color-surface-02);border:1px solid var(--color-surface-04)">

          <!-- Full audio controls -->
          <div class="flex items-center gap-3 mb-5">
            <button
              @click="playFull"
              :disabled="ttsLoading"
              class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
              style="background:rgba(6,182,212,0.12);color:#22d3ee;border:1px solid rgba(6,182,212,0.25)"
            >
              <span v-if="ttsLoading" class="animate-spin">⏳</span>
              <span v-else-if="ttsPlaying">⏹ Đang phát</span>
              <span v-else>▶ Nghe cả bài</span>
            </button>
            <div class="flex gap-1">
              <button
                v-for="sp in [0.75, 1.0, 1.25]"
                :key="sp"
                @click="playbackRate = sp"
                class="px-2.5 py-1 rounded-lg text-xs font-medium transition"
                :style="playbackRate === sp
                  ? 'background:rgba(6,182,212,0.2);color:#22d3ee;border:1px solid rgba(6,182,212,0.4)'
                  : 'background:var(--color-surface-04);color:var(--color-text-muted)'"
              >
                {{ sp }}x
              </button>
            </div>
          </div>

          <textarea
            v-model="fullInput"
            :disabled="fullState === 'correct'"
            placeholder="Gõ toàn bộ nội dung bạn nghe được..."
            rows="6"
            class="w-full px-4 py-3 rounded-xl text-sm outline-none transition resize-none"
            style="background:var(--color-surface-03);border:1px solid var(--color-surface-04);color:var(--color-text-base)"
          />

          <!-- Full diff result -->
          <Transition name="fade">
            <div
              v-if="fullState !== 'idle'"
              class="mt-4 px-4 py-3 rounded-xl text-sm leading-loose"
              :style="fullState === 'correct'
                ? 'background:rgba(34,197,94,0.07);border:1px solid rgba(34,197,94,0.2)'
                : 'background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.2)'"
            >
              <span
                v-for="(token, ti) in diffResult"
                :key="ti"
                :style="token.match ? 'color:#86efac' : 'color:#fca5a5;text-decoration:underline wavy'"
              >
                {{ token.word }}{{ ti < diffResult.length - 1 ? ' ' : '' }}
              </span>
              <p class="mt-2 text-xs" style="color:var(--color-text-muted)">
                Độ chính xác: <strong>{{ lastAccuracy }}%</strong>
              </p>
            </div>
          </Transition>

          <div class="flex gap-2 mt-4 flex-wrap">
            <button
              v-if="fullState !== 'correct'"
              @click="checkFullPassage"
              :disabled="!fullInput.trim() || checkLoading"
              class="px-5 py-2 rounded-xl text-sm font-semibold transition hover:opacity-80"
              :style="(!fullInput.trim() || checkLoading)
                ? 'background:var(--color-surface-04);color:var(--color-text-muted);cursor:not-allowed'
                : 'background:rgba(99,102,241,0.15);color:#818cf8;border:1px solid rgba(99,102,241,0.3)'"
            >
              {{ checkLoading ? '...' : 'Kiểm tra' }}
            </button>
            <button
              v-if="fullState === 'wrong'"
              @click="fullState = 'idle'; diffResult = []"
              class="px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
              style="background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)"
            >
              Thử lại
            </button>
            <button
              v-if="fullState === 'correct'"
              @click="showSummary = true"
              class="px-5 py-2 rounded-xl text-sm font-semibold transition hover:opacity-80"
              style="background:var(--color-primary-600);color:#fff"
            >
              Xem kết quả →
            </button>
          </div>
        </div>
      </template>

    </template>

    <!-- ───────── SUMMARY MODAL ───────── -->
    <Transition name="fade">
      <div
        v-if="showSummary"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        style="background:rgba(0,0,0,0.5)"
        @click.self="showSummary = false"
      >
        <div class="w-full max-w-md rounded-2xl p-6 shadow-xl" style="background:var(--color-surface-01)">
          <div class="text-center mb-5">
            <p class="text-4xl mb-2">🎉</p>
            <h2 class="text-lg font-bold" style="color:var(--color-text-base)">Hoàn thành Chính tả!</h2>
            <p class="text-sm mt-1" style="color:var(--color-text-muted)">{{ passage?.title }}</p>
          </div>

          <!-- Score -->
          <div class="flex justify-center mb-5">
            <div class="text-center px-8 py-4 rounded-2xl" style="background:var(--color-surface-03)">
              <p class="text-4xl font-black" style="color:#22d3ee">{{ finalScore }}%</p>
              <p class="text-xs mt-1" style="color:var(--color-text-muted)">Độ chính xác</p>
            </div>
          </div>

          <!-- Sentence heatmap -->
          <div v-if="mode === 'sentence'" class="mb-5">
            <p class="text-xs font-semibold mb-2 uppercase tracking-wide" style="color:var(--color-text-muted)">Chi tiết theo câu</p>
            <div class="flex flex-wrap gap-1.5">
              <div
                v-for="(s, i) in sentences"
                :key="i"
                class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold"
                :style="sentenceScores[i] >= 80
                  ? 'background:rgba(34,197,94,0.15);color:#86efac'
                  : sentenceScores[i] > 0
                    ? 'background:rgba(251,191,36,0.15);color:#fbbf24'
                    : 'background:var(--color-surface-04);color:var(--color-text-muted)'"
                :title="`Câu ${i+1}: ${sentenceScores[i] || 0}%`"
              >
                {{ i + 1 }}
              </div>
            </div>
          </div>

          <!-- CTAs -->
          <div class="flex flex-col gap-2">
            <RouterLink
              :to="`/skill-practice/shadowing/${route.params.id}`"
              class="w-full text-center py-3 rounded-xl text-sm font-semibold transition hover:opacity-80"
              style="background:rgba(99,102,241,0.15);color:#818cf8;border:1px solid rgba(99,102,241,0.3)"
            >
              🎤 Chuyển sang Shadowing
            </RouterLink>
            <button
              @click="restartAll"
              class="w-full py-3 rounded-xl text-sm font-medium transition hover:opacity-80"
              style="background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)"
            >
              🔄 Luyện lại
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { skillPracticeApi } from '@/api/skillPractice.js'
import { usePassageTTS } from '@/composables/usePassageTTS.js'

const route = useRoute()
const passageId = computed(() => Number(route.params.id))

const passage = ref(null)
const loading = ref(true)

// TTS
const { play: ttsPlay, stop: ttsStop, isPlaying: ttsPlaying, isLoading: ttsLoading, setRate } = usePassageTTS()
const playbackRate = ref(1.0)
watch(playbackRate, (r) => setRate(r))

// Mode: 'sentence' | 'full'
const mode = ref('sentence')

// Sentence mode state
const currentIndex = ref(0)
const userInput = ref('')
const inputRef = ref(null)
const sentenceState = ref('idle')  // idle | checking | correct | wrong
const diffResult = ref([])
const playCount = ref(0)
const failCount = ref(0)
const showHint = ref(false)
const showAnswer = ref(false)
const hint = ref('')
const lastAccuracy = ref(0)
const checkLoading = ref(false)
const sentenceScores = ref({})  // { 0: 95, 1: 70, ... }
const showSummary = ref(false)
const startTime = ref(Date.now())

// Full mode state
const fullInput = ref('')
const fullState = ref('idle')

const sentences = computed(() => passage.value?.sentences_json || [])
const currentSentence = computed(() => sentences.value[currentIndex.value])

const completedCount = computed(() =>
  sentences.value.filter((_, i) => sentenceScores.value[i] >= 80).length
)

const finalScore = computed(() => {
  const scores = Object.values(sentenceScores.value)
  if (!scores.length) return lastAccuracy.value
  return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length)
})

function sentenceStyle(i) {
  const score = sentenceScores.value[i]
  if (score >= 80) return 'background:rgba(34,197,94,0.2);color:#86efac;border:1px solid rgba(34,197,94,0.3)'
  if (score > 0) return 'background:rgba(251,191,36,0.2);color:#fbbf24;border:1px solid rgba(251,191,36,0.3)'
  if (i === currentIndex.value) return 'background:rgba(99,102,241,0.3);color:#818cf8;border:1px solid rgba(99,102,241,0.5)'
  return 'background:var(--color-surface-04);color:var(--color-text-muted)'
}

async function playCurrent() {
  const s = currentSentence.value
  if (!s) return
  // Use pre-generated audio or on-demand
  let audioUrl = s.audio_url
  if (!audioUrl) {
    try {
      const res = await skillPracticeApi.getSentenceTTS(passageId.value, s.index)
      audioUrl = res.data.audio_url
      // Cache it in the local sentences_json
      const updated = [...sentences.value]
      updated[currentIndex.value] = { ...s, audio_url: audioUrl }
      passage.value.sentences_json = updated
    } catch {
      return
    }
  }
  playCount.value += 1
  await ttsPlay(s.text, passage.value.tts_voice || 'en-US-AriaNeural', playbackRate.value)
}

async function playFull() {
  if (!passage.value) return
  let audioUrl = passage.value.full_audio_url
  if (!audioUrl) {
    // Fallback: use full text via TTS composable
    audioUrl = null
  }
  await ttsPlay(passage.value.full_text, passage.value.tts_voice || 'en-US-AriaNeural', playbackRate.value)
  playCount.value += 1
}

async function checkAnswer() {
  if (!userInput.value.trim() || !playCount.value || checkLoading.value) return
  checkLoading.value = true
  const timeSpent = Math.round((Date.now() - startTime.value) / 1000)
  try {
    const res = await skillPracticeApi.checkDictation(passageId.value, {
      sentence_index: currentSentence.value.index,
      user_input: userInput.value,
      time_spent_seconds: timeSpent,
    })
    const data = res.data
    diffResult.value = data.diff
    lastAccuracy.value = data.accuracy_percent
    sentenceScores.value = { ...sentenceScores.value, [currentIndex.value]: data.accuracy_percent }

    if (data.is_correct) {
      sentenceState.value = 'correct'
      hint.value = ''
      showHint.value = false
      showAnswer.value = false
    } else {
      sentenceState.value = 'wrong'
      failCount.value += 1
      hint.value = data.hint || ''
      if (failCount.value >= 2) showHint.value = true
    }
  } catch {
    // silent
  } finally {
    checkLoading.value = false
  }
}

async function checkFullPassage() {
  if (!fullInput.value.trim() || checkLoading.value) return
  checkLoading.value = true
  const timeSpent = Math.round((Date.now() - startTime.value) / 1000)
  try {
    const res = await skillPracticeApi.checkDictation(passageId.value, {
      sentence_index: null,
      user_input: fullInput.value,
      time_spent_seconds: timeSpent,
    })
    const data = res.data
    diffResult.value = data.diff
    lastAccuracy.value = data.accuracy_percent

    if (data.is_correct || data.accuracy_percent >= 80) {
      fullState.value = 'correct'
      showSummary.value = true
    } else {
      fullState.value = 'wrong'
    }
  } catch {
    // silent
  } finally {
    checkLoading.value = false
  }
}

function nextSentence() {
  if (currentIndex.value < sentences.value.length - 1) {
    goToSentence(currentIndex.value + 1)
  } else {
    showSummary.value = true
  }
}

function goToSentence(i) {
  ttsStop()
  currentIndex.value = i
  userInput.value = ''
  sentenceState.value = 'idle'
  diffResult.value = []
  playCount.value = 0
  failCount.value = 0
  showHint.value = false
  showAnswer.value = false
  hint.value = ''
  startTime.value = Date.now()
  nextTick(() => inputRef.value?.focus())
}

function resetSentence() {
  userInput.value = ''
  sentenceState.value = 'idle'
  diffResult.value = []
}

function switchMode(m) {
  ttsStop()
  mode.value = m
  currentIndex.value = 0
  userInput.value = ''
  fullInput.value = ''
  sentenceState.value = 'idle'
  fullState.value = 'idle'
  diffResult.value = []
  playCount.value = 0
  failCount.value = 0
  showHint.value = false
  showAnswer.value = false
  hint.value = ''
  startTime.value = Date.now()
}

function restartAll() {
  showSummary.value = false
  switchMode(mode.value)
  sentenceScores.value = {}
}

async function loadPassage() {
  loading.value = true
  try {
    const res = await skillPracticeApi.getPassage(passageId.value)
    passage.value = res.data

    // Restore progress
    const dp = res.data.dictation_progress
    if (dp?.sentences_completed_json) {
      Object.entries(dp.sentences_completed_json).forEach(([idx, done]) => {
        if (done) sentenceScores.value[Number(idx)] = 100
      })
    }

    // Jump to first incomplete sentence
    const firstIncomplete = sentences.value.findIndex((_, i) => !sentenceScores.value[i])
    if (firstIncomplete >= 0) currentIndex.value = firstIncomplete
  } catch {
    passage.value = null
  } finally {
    loading.value = false
    startTime.value = Date.now()
  }
}

onMounted(loadPassage)
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
