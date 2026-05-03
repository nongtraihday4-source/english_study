<template>
  <div class="shadowing-exercise">
    <div class="flex items-center gap-2 mb-3">
      <span class="text-xs px-2 py-0.5 rounded-full font-medium"
            style="background:rgba(99,102,241,0.12);color:#818cf8">🎤 Shadowing</span>
      <span v-if="done" class="text-xs font-medium" style="color:#86efac">✓ Hoàn thành</span>
    </div>

    <p class="text-sm font-medium mb-3" style="color:var(--color-text-base)">
      Nghe câu và luyện nói theo. Tự đánh giá phát âm của bạn.
    </p>

    <!-- Step 1: Listen -->
    <div v-if="step !== 'done'" class="mb-4">
      <div class="flex items-center gap-3 mb-2">
        <button @click="playAudio"
                :disabled="ttsLoading"
                class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
                style="background:rgba(99,102,241,0.12);color:#818cf8;border:1px solid rgba(99,102,241,0.25)">
          <span v-if="ttsLoading" class="animate-spin">⏳</span>
          <span v-else-if="ttsPlaying">⏹ Đang phát</span>
          <span v-else>▶ Nghe ({{ currentSpeed }}x)</span>
        </button>

        <!-- Speed toggle -->
        <div class="flex gap-1">
          <button v-for="sp in [0.75, 1.0]" :key="sp"
                  @click="currentSpeed = sp"
                  class="px-2.5 py-1 rounded-lg text-xs font-medium transition"
                  :style="currentSpeed === sp
                    ? 'background:rgba(99,102,241,0.25);color:#818cf8;border:1px solid rgba(99,102,241,0.4)'
                    : 'background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)'">
            {{ sp }}x
          </button>
        </div>
      </div>

      <!-- Prompt to speak -->
      <p v-if="playCount > 0 && step === 'listen'" class="text-xs mb-3" style="color:var(--color-text-muted)">
        Nhấn "Nói theo" khi sẵn sàng.
      </p>
    </div>

    <!-- Step 2: Record -->
    <div v-if="step === 'listen' && playCount > 0" class="mb-4">
      <button v-if="!recording"
              @click="startRecording"
              class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
              style="background:rgba(239,68,68,0.12);color:#fca5a5;border:1px solid rgba(239,68,68,0.25)">
        🎙 Nói theo
      </button>
      <button v-else
              @click="stopRecording"
              class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80 animate-pulse"
              style="background:rgba(239,68,68,0.25);color:#fca5a5;border:1px solid rgba(239,68,68,0.5)">
        ⏹ Dừng ghi âm ({{ recordSeconds }}s)
      </button>
    </div>

    <!-- Step 3: Self-assessment -->
    <div v-if="step === 'assess'" class="mb-4">
      <p class="text-sm font-medium mb-3" style="color:var(--color-text-base)">
        Bạn cảm thấy phát âm của mình thế nào?
      </p>

      <!-- Playback recorded audio -->
      <button v-if="recordedUrl"
              @click="playRecorded"
              class="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium mb-3 transition hover:opacity-80"
              style="background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)">
        ▶ Nghe lại giọng của bạn
      </button>

      <div class="flex gap-2 flex-wrap">
        <button v-for="level in assessLevels" :key="level.value"
                @click="submitAssessment(level.value)"
                class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
                :style="level.style">
          {{ level.emoji }} {{ level.label }}
        </button>
      </div>
    </div>

    <!-- Step 4: Done — show text for review -->
    <div v-if="step === 'done'" class="mb-4">
      <div class="px-4 py-3 rounded-xl"
           style="background:var(--color-surface-03);border:1px solid var(--color-surface-04)">
        <p class="text-xs font-semibold uppercase tracking-wide mb-1" style="color:var(--color-text-muted)">Câu gốc</p>
        <p class="text-sm font-medium" style="color:var(--color-text-base)">{{ exercise.audio_text }}</p>
        <p v-if="exercise.translation_vi" class="text-xs mt-1" style="color:var(--color-text-muted)">
          {{ exercise.translation_vi }}
        </p>
      </div>
      <p v-if="selfRating" class="text-xs mt-2" style="color:var(--color-text-muted)">
        Tự đánh giá: {{ assessLevels.find(l => l.value === selfRating)?.emoji }}
        {{ assessLevels.find(l => l.value === selfRating)?.label }}
      </p>
    </div>

    <!-- Try again / Continue -->
    <div v-if="step === 'done'" class="flex gap-2">
      <button @click="resetExercise"
              class="px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
              style="background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)">
        Thử lại
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import apiClient from '@/api/client.js'

const props = defineProps({
  exercise: { type: Object, required: true },
  done: { type: Boolean, default: false },
})
const emit = defineEmits(['complete'])

// TTS with playback rate (uses raw Audio element for speed control)
const ttsLoading = ref(false)
const ttsPlaying = ref(false)
const currentSpeed = ref(1.0)
const playCount = ref(0)

// Blob cache per text
const blobUrlCache = new Map()

async function playAudio() {
  if (ttsLoading.value) return
  if (ttsPlaying.value) {
    if (_playingAudio) { _playingAudio.pause(); _playingAudio = null }
    ttsPlaying.value = false
    return
  }

  const text = props.exercise.audio_text?.trim().toLowerCase() || ''
  const cacheKey = `${text}`
  let blobUrl = blobUrlCache.get(cacheKey)

  if (!blobUrl) {
    ttsLoading.value = true
    try {
      const resp = await apiClient.get('/pronunciation/tts/', {
        params: { text },
        responseType: 'blob',
      })
      blobUrl = URL.createObjectURL(resp.data)
      blobUrlCache.set(cacheKey, blobUrl)
    } catch {
      ttsLoading.value = false
      return
    }
    ttsLoading.value = false
  }

  const audio = new Audio(blobUrl)
  audio.playbackRate = currentSpeed.value
  _playingAudio = audio
  ttsPlaying.value = true
  audio.addEventListener('ended', () => { ttsPlaying.value = false; _playingAudio = null })
  audio.addEventListener('error', () => { ttsPlaying.value = false; _playingAudio = null })
  try { await audio.play() } catch { ttsPlaying.value = false; _playingAudio = null }
  playCount.value++
}

let _playingAudio = null

// Recording
const step = ref('listen')   // listen | assess | done
const recording = ref(false)
const recordSeconds = ref(0)
const recordedUrl = ref(null)
const selfRating = ref(null)
let _mediaRecorder = null
let _recordChunks = []
let _recordTimer = null

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    _recordChunks = []
    _mediaRecorder = new MediaRecorder(stream)
    _mediaRecorder.ondataavailable = e => { if (e.data.size > 0) _recordChunks.push(e.data) }
    _mediaRecorder.onstop = () => {
      const blob = new Blob(_recordChunks, { type: 'audio/webm' })
      recordedUrl.value = URL.createObjectURL(blob)
      stream.getTracks().forEach(t => t.stop())
      step.value = 'assess'
    }
    _mediaRecorder.start()
    recording.value = true
    recordSeconds.value = 0
    _recordTimer = setInterval(() => { recordSeconds.value++ }, 1000)
  } catch (e) {
    console.warn('[Shadowing] microphone access denied:', e)
  }
}

function stopRecording() {
  if (_mediaRecorder && recording.value) {
    _mediaRecorder.stop()
    recording.value = false
    clearInterval(_recordTimer)
  }
}

function playRecorded() {
  if (recordedUrl.value) {
    const a = new Audio(recordedUrl.value)
    a.play().catch(() => {})
  }
}

const assessLevels = [
  { value: 'poor',  emoji: '😕', label: 'Chưa tốt', style: 'background:rgba(239,68,68,0.1);color:#fca5a5;border:1px solid rgba(239,68,68,0.25)' },
  { value: 'ok',    emoji: '😊', label: 'Khá',      style: 'background:rgba(251,191,36,0.1);color:#fbbf24;border:1px solid rgba(251,191,36,0.25)' },
  { value: 'great', emoji: '🎯', label: 'Tốt',      style: 'background:rgba(34,197,94,0.1);color:#86efac;border:1px solid rgba(34,197,94,0.25)' },
]

function submitAssessment(rating) {
  selfRating.value = rating
  step.value = 'done'
  emit('complete')
}

function resetExercise() {
  step.value = 'listen'
  recording.value = false
  recordedUrl.value = null
  selfRating.value = null
  playCount.value = 0
  recordSeconds.value = 0
  clearInterval(_recordTimer)
}

onUnmounted(() => {
  clearInterval(_recordTimer)
  if (_playingAudio) { _playingAudio.pause(); _playingAudio = null }
})
</script>
