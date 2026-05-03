<template>
  <div class="max-w-2xl mx-auto px-4 py-8">

    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <RouterLink
        :to="passage ? `/skill-practice/passages/${passage.topic_slug}?level=${passage.cefr_level}` : '/skill-practice'"
        class="text-sm hover:opacity-70 transition"
        style="color:var(--color-text-muted)"
      >
        ← Quay lại
      </RouterLink>
      <span class="text-xs px-3 py-1 rounded-full font-semibold" style="background:rgba(99,102,241,0.12);color:#818cf8">
        🎤 Shadowing
      </span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="space-y-4">
      <div class="h-8 w-2/3 rounded-xl animate-pulse" style="background:var(--color-surface-03)" />
      <div class="h-40 rounded-2xl animate-pulse" style="background:var(--color-surface-03)" />
    </div>

    <template v-else-if="passage">

      <!-- Title + meta -->
      <h1 class="text-lg font-bold mb-1" style="color:var(--color-text-base)">{{ passage.title }}</h1>
      <div class="flex items-center gap-2 mb-6 flex-wrap">
        <span class="text-xs px-2 py-0.5 rounded-full" style="background:var(--color-surface-04);color:var(--color-text-muted)">
          {{ passage.cefr_level }}
        </span>
        <span class="text-xs" style="color:var(--color-text-muted)">{{ passage.topic }}</span>
      </div>

      <!-- Sentence progress bar -->
      <div class="flex items-center gap-3 mb-6">
        <div class="flex gap-1.5 flex-wrap flex-1">
          <button
            v-for="(s, i) in sentences"
            :key="i"
            @click="goToSentence(i)"
            class="w-6 h-6 rounded-full text-xs font-bold transition"
            :style="sentenceDotStyle(i)"
          >
            {{ i + 1 }}
          </button>
        </div>
        <span class="text-xs font-medium shrink-0" style="color:var(--color-text-muted)">
          {{ completedCount }}/{{ sentences.length }}
        </span>
      </div>

      <!-- Display options -->
      <div class="flex items-center gap-4 mb-5">
        <label class="flex items-center gap-2 cursor-pointer select-none">
          <div
            @click="showText = !showText"
            class="w-10 h-5 rounded-full relative transition"
            :style="showText ? 'background:#818cf8' : 'background:var(--color-surface-04)'"
          >
            <div
              class="absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-all"
              :style="showText ? 'left:calc(100% - 18px)' : 'left:2px'"
            />
          </div>
          <span class="text-xs" style="color:var(--color-text-muted)">Hiện văn bản</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer select-none">
          <div
            @click="showTranslation = !showTranslation"
            class="w-10 h-5 rounded-full relative transition"
            :style="showTranslation ? 'background:#818cf8' : 'background:var(--color-surface-04)'"
          >
            <div
              class="absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-all"
              :style="showTranslation ? 'left:calc(100% - 18px)' : 'left:2px'"
            />
          </div>
          <span class="text-xs" style="color:var(--color-text-muted)">Dịch nghĩa</span>
        </label>
      </div>

      <!-- Sentence card -->
      <div class="rounded-2xl p-5" style="background:var(--color-surface-02);border:1px solid var(--color-surface-04)">

        <p class="text-xs font-semibold mb-4 uppercase tracking-wide" style="color:var(--color-text-muted)">
          Câu {{ currentIndex + 1 }} / {{ sentences.length }}
        </p>

        <!-- ── STEP 1: Listen ── -->
        <div
          v-if="step !== 'done'"
          class="mb-5 p-3 rounded-xl"
          :style="step === 'listen' ? 'background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.12)' : 'background:var(--color-surface-03)'"
        >
          <p class="text-xs font-semibold mb-3 uppercase tracking-wide" style="color:#818cf8">① Nghe mẫu</p>
          <div class="flex items-center gap-3">
            <button
              @click="playCurrent"
              :disabled="ttsLoading"
              class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
              style="background:rgba(99,102,241,0.12);color:#818cf8;border:1px solid rgba(99,102,241,0.25)"
            >
              <span v-if="ttsLoading" class="animate-spin">⏳</span>
              <span v-else-if="ttsPlaying">⏹ Đang phát</span>
              <span v-else>▶ Nghe ({{ playbackRate }}x)</span>
            </button>
            <div class="flex gap-1">
              <button
                v-for="sp in [0.75, 1.0, 1.25]"
                :key="sp"
                @click="playbackRate = sp"
                class="px-2.5 py-1 rounded-lg text-xs font-medium transition"
                :style="playbackRate === sp
                  ? 'background:rgba(99,102,241,0.2);color:#818cf8;border:1px solid rgba(99,102,241,0.4)'
                  : 'background:var(--color-surface-04);color:var(--color-text-muted)'"
              >
                {{ sp }}x
              </button>
            </div>
          </div>
        </div>

        <!-- Text display (togglable) -->
        <Transition name="fade">
          <div v-if="showText && currentSentence" class="mb-4 px-4 py-3 rounded-xl" style="background:var(--color-surface-03)">
            <p class="text-sm leading-relaxed" style="color:var(--color-text-base)">{{ currentSentence.text }}</p>
            <Transition name="fade">
              <p v-if="showTranslation && currentSentence.translation_vi" class="text-xs mt-2" style="color:var(--color-text-muted)">
                {{ currentSentence.translation_vi }}
              </p>
            </Transition>
          </div>
        </Transition>

        <!-- ── STEP 2: Record ── -->
        <div
          v-if="step === 'listen' && playCount > 0"
          class="mb-5 p-3 rounded-xl"
          :style="isRecording ? 'background:rgba(239,68,68,0.05);border:1px solid rgba(239,68,68,0.2)' : 'background:rgba(239,68,68,0.04);border:1px solid rgba(239,68,68,0.12)'"
        >
          <p class="text-xs font-semibold mb-3 uppercase tracking-wide" style="color:#fca5a5">② Nói theo</p>

          <div class="flex items-center gap-3">
            <button
              v-if="!isRecording"
              @click="startRec"
              class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
              style="background:rgba(239,68,68,0.12);color:#fca5a5;border:1px solid rgba(239,68,68,0.25)"
            >
              🎙 Bắt đầu nói
            </button>
            <button
              v-else
              @click="stopRec"
              class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold animate-pulse transition hover:opacity-80"
              style="background:rgba(239,68,68,0.25);color:#fca5a5;border:1px solid rgba(239,68,68,0.5)"
            >
              ⏹ Dừng ghi âm
            </button>

            <span v-if="isRecording" class="text-xs font-mono" style="color:#fca5a5">
              {{ recordDuration }}s
            </span>
          </div>

          <p v-if="recError" class="text-xs mt-2" style="color:#fca5a5">⚠ {{ recError }}</p>
        </div>

        <!-- ── STEP 3: Assess ── -->
        <div v-if="step === 'assess'" class="mb-5 p-3 rounded-xl" style="background:rgba(251,191,36,0.04);border:1px solid rgba(251,191,36,0.15)">
          <p class="text-xs font-semibold mb-3 uppercase tracking-wide" style="color:#fbbf24">③ Tự đánh giá</p>

          <!-- Playback controls -->
          <div class="flex gap-2 mb-4">
            <button
              @click="playOriginal"
              :disabled="ttsLoading"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition hover:opacity-80"
              style="background:rgba(99,102,241,0.1);color:#818cf8;border:1px solid rgba(99,102,241,0.2)"
            >
              ▶ Nghe mẫu
            </button>
            <button
              v-if="recordedUrl"
              @click="playRecorded"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition hover:opacity-80"
              style="background:rgba(239,68,68,0.1);color:#fca5a5;border:1px solid rgba(239,68,68,0.2)"
            >
              ▶ Nghe giọng bạn
            </button>
          </div>

          <!-- Rating buttons -->
          <div class="flex flex-wrap gap-2">
            <button
              v-for="level in ratingLevels"
              :key="level.value"
              @click="submitRating(level.value)"
              :disabled="submitLoading"
              class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
              :style="level.style"
            >
              {{ level.emoji }} {{ level.label }}
            </button>
          </div>
        </div>

        <!-- ── STEP 4: Done ── -->
        <div v-if="step === 'done'" class="mb-5 p-3 rounded-xl" style="background:rgba(34,197,94,0.04);border:1px solid rgba(34,197,94,0.12)">
          <div class="flex items-center justify-between mb-2">
            <p class="text-xs font-semibold uppercase tracking-wide" style="color:#86efac">✓ Hoàn thành câu này</p>
            <span class="text-xs" style="color:var(--color-text-muted)">
              {{ ratingLevels.find(l => l.value === selfRatings[currentIndex])?.emoji }}
              {{ ratingLevels.find(l => l.value === selfRatings[currentIndex])?.label }}
            </span>
          </div>
          <!-- Show text always when done -->
          <p class="text-sm leading-relaxed" style="color:var(--color-text-base)">{{ currentSentence.text }}</p>
          <p v-if="currentSentence.translation_vi" class="text-xs mt-1" style="color:var(--color-text-muted)">
            {{ currentSentence.translation_vi }}
          </p>
        </div>

        <!-- Navigation -->
        <div class="flex gap-2 flex-wrap">
          <button
            v-if="step === 'done'"
            @click="nextSentence"
            class="px-5 py-2 rounded-xl text-sm font-semibold transition hover:opacity-80"
            style="background:var(--color-primary-600);color:#fff"
          >
            {{ currentIndex < sentences.length - 1 ? 'Câu tiếp →' : 'Xem kết quả →' }}
          </button>
          <button
            v-if="step === 'assess'"
            @click="resetCurrentSentence"
            class="px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
            style="background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)"
          >
            Nghe lại và ghi âm lại
          </button>
        </div>

      </div>
    </template>

    <!-- ── SUMMARY MODAL ── -->
    <Transition name="fade">
      <div
        v-if="showSummary"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        style="background:rgba(0,0,0,0.5)"
        @click.self="showSummary = false"
      >
        <div class="w-full max-w-md rounded-2xl p-6 shadow-xl" style="background:var(--color-surface-01)">
          <div class="text-center mb-5">
            <p class="text-4xl mb-2">🎤</p>
            <h2 class="text-lg font-bold" style="color:var(--color-text-base)">Hoàn thành Shadowing!</h2>
            <p class="text-sm mt-1" style="color:var(--color-text-muted)">{{ passage?.title }}</p>
          </div>

          <!-- Average rating -->
          <div class="flex justify-center mb-5">
            <div class="text-center px-8 py-4 rounded-2xl" style="background:var(--color-surface-03)">
              <p class="text-4xl font-black" style="color:#818cf8">{{ avgRatingLabel }}</p>
              <p class="text-xs mt-1" style="color:var(--color-text-muted)">Đánh giá trung bình</p>
            </div>
          </div>

          <!-- Per-sentence ratings -->
          <div class="flex flex-wrap gap-1.5 mb-5 justify-center">
            <div
              v-for="(s, i) in sentences"
              :key="i"
              class="w-8 h-8 rounded-lg flex items-center justify-center text-sm"
              :title="`Câu ${i+1}: ${ratingLevels.find(l => l.value === (selfRatings[i] || 0))?.label || '—'}`"
              style="background:var(--color-surface-04)"
            >
              {{ ratingLevels.find(l => l.value === (selfRatings[i] || 0))?.emoji || '—' }}
            </div>
          </div>

          <div class="flex flex-col gap-2">
            <RouterLink
              :to="`/skill-practice/dictation/${route.params.id}`"
              class="w-full text-center py-3 rounded-xl text-sm font-semibold transition hover:opacity-80"
              style="background:rgba(6,182,212,0.12);color:#22d3ee;border:1px solid rgba(6,182,212,0.25)"
            >
              🎧 Luyện Chính tả cùng bài
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { skillPracticeApi } from '@/api/skillPractice.js'
import { usePassageTTS } from '@/composables/usePassageTTS.js'
import { useAudioRecorder } from '@/composables/useAudioRecorder.js'

const route = useRoute()
const passageId = computed(() => Number(route.params.id))

const passage = ref(null)
const loading = ref(true)

// TTS
const { play: ttsPlay, stop: ttsStop, isPlaying: ttsPlaying, isLoading: ttsLoading, setRate } = usePassageTTS()
const playbackRate = ref(1.0)
watch(playbackRate, (r) => setRate(r))

// Recorder
const { startRecording, stopRecording, isRecording, recordedUrl, recordDuration, errorMessage: recError, reset: resetRecorder } = useAudioRecorder()

// UI toggles
const showText = ref(true)
const showTranslation = ref(false)
const showSummary = ref(false)

// Shadowing per-sentence state
const currentIndex = ref(0)
const step = ref('listen')  // listen | assess | done
const playCount = ref(0)
const selfRatings = ref({})  // { 0: 3, 1: 4, ... }
const submitLoading = ref(false)
const startTime = ref(Date.now())

const sentences = computed(() => passage.value?.sentences_json || [])
const currentSentence = computed(() => sentences.value[currentIndex.value])

const completedCount = computed(() =>
  sentences.value.filter((_, i) => selfRatings.value[i] !== undefined).length
)

const avgRatingLabel = computed(() => {
  const ratings = Object.values(selfRatings.value)
  if (!ratings.length) return '—'
  const avg = ratings.reduce((a, b) => a + b, 0) / ratings.length
  const level = ratingLevels.find(l => l.value === Math.round(avg))
  return level ? `${level.emoji} ${level.label}` : '—'
})

const ratingLevels = [
  { value: 1, emoji: '😕', label: 'Cần cải thiện', style: 'background:rgba(239,68,68,0.1);color:#fca5a5;border:1px solid rgba(239,68,68,0.2)' },
  { value: 2, emoji: '😐', label: 'Tạm được', style: 'background:rgba(251,191,36,0.1);color:#fbbf24;border:1px solid rgba(251,191,36,0.2)' },
  { value: 3, emoji: '🙂', label: 'Khá tốt', style: 'background:rgba(34,197,94,0.1);color:#86efac;border:1px solid rgba(34,197,94,0.2)' },
  { value: 4, emoji: '😊', label: 'Tốt', style: 'background:rgba(99,102,241,0.1);color:#818cf8;border:1px solid rgba(99,102,241,0.2)' },
  { value: 5, emoji: '🤩', label: 'Xuất sắc', style: 'background:rgba(168,85,247,0.1);color:#c084fc;border:1px solid rgba(168,85,247,0.2)' },
]

function sentenceDotStyle(i) {
  const rating = selfRatings.value[i]
  if (rating !== undefined) {
    if (rating >= 4) return 'background:rgba(99,102,241,0.25);color:#818cf8;border:1px solid rgba(99,102,241,0.4)'
    if (rating >= 3) return 'background:rgba(34,197,94,0.2);color:#86efac;border:1px solid rgba(34,197,94,0.3)'
    if (rating >= 2) return 'background:rgba(251,191,36,0.2);color:#fbbf24;border:1px solid rgba(251,191,36,0.3)'
    return 'background:rgba(239,68,68,0.2);color:#fca5a5;border:1px solid rgba(239,68,68,0.3)'
  }
  if (i === currentIndex.value) return 'background:rgba(99,102,241,0.3);color:#818cf8;border:1px solid rgba(99,102,241,0.5)'
  return 'background:var(--color-surface-04);color:var(--color-text-muted)'
}

async function playCurrent() {
  const s = currentSentence.value
  if (!s) return
  let audioUrl = s.audio_url
  if (!audioUrl) {
    try {
      const res = await skillPracticeApi.getSentenceTTS(passageId.value, s.index)
      audioUrl = res.data.audio_url
      const updated = [...sentences.value]
      updated[currentIndex.value] = { ...s, audio_url: audioUrl }
      passage.value.sentences_json = updated
    } catch { return }
  }
  playCount.value += 1
  await ttsPlay(s.text, passage.value.tts_voice || 'en-US-AriaNeural', playbackRate.value)
}

async function playOriginal() {
  await playCurrent()
}

function playRecorded() {
  if (!recordedUrl.value) return
  const audio = new Audio(recordedUrl.value)
  audio.play()
}

async function startRec() {
  await startRecording()
}

function stopRec() {
  stopRecording()
  // Wait a tick for onstop to fire and recordedUrl to be set
  setTimeout(() => {
    step.value = 'assess'
  }, 200)
}

async function submitRating(rating) {
  submitLoading.value = true
  const timeSpent = Math.round((Date.now() - startTime.value) / 1000)
  try {
    await skillPracticeApi.completeShadowing(passageId.value, {
      sentence_index: currentSentence.value.index,
      self_rating: rating,
      time_spent_seconds: timeSpent,
    })
    selfRatings.value = { ...selfRatings.value, [currentIndex.value]: rating }
    step.value = 'done'
    resetRecorder()
  } catch {
    // silent
  } finally {
    submitLoading.value = false
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
  step.value = 'listen'
  playCount.value = 0
  startTime.value = Date.now()
  resetRecorder()
}

function resetCurrentSentence() {
  step.value = 'listen'
  playCount.value = 0
  resetRecorder()
}

function restartAll() {
  showSummary.value = false
  currentIndex.value = 0
  step.value = 'listen'
  playCount.value = 0
  selfRatings.value = {}
  startTime.value = Date.now()
  resetRecorder()
}

async function loadPassage() {
  loading.value = true
  try {
    const res = await skillPracticeApi.getPassage(passageId.value)
    passage.value = res.data

    // Restore progress
    const sp = res.data.shadowing_progress
    if (sp?.sentences_completed_json) {
      Object.entries(sp.sentences_completed_json).forEach(([idx, done]) => {
        if (done) selfRatings.value[Number(idx)] = selfRatings.value[Number(idx)] || 3
      })
    }
    const firstIncomplete = sentences.value.findIndex((_, i) => selfRatings.value[i] === undefined)
    if (firstIncomplete >= 0) currentIndex.value = firstIncomplete
  } catch {
    passage.value = null
  } finally {
    loading.value = false
  }
}

onMounted(loadPassage)
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
