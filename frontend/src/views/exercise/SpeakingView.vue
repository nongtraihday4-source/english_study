<template>
  <div class="flex flex-col" style="min-height: calc(100vh - 64px)">

    <!-- Loading -->
    <div v-if="loading" class="p-6 space-y-4">
      <div class="h-6 w-48 rounded-lg animate-pulse" style="background: var(--color-surface-03)"></div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="h-64 rounded-2xl animate-pulse" style="background: var(--color-surface-02)"></div>
        <div class="h-64 rounded-2xl animate-pulse" style="background: var(--color-surface-02)"></div>
      </div>
    </div>

    <!-- Not found -->
    <div v-else-if="!exercise" class="flex-1 flex flex-col items-center justify-center gap-3"
         style="color: var(--color-text-muted)">
      <span class="text-5xl">🎤</span>
      <p>Không tìm thấy bài tập.</p>
      <RouterLink to="/courses" class="text-sm underline">← Quay lại khoá học</RouterLink>
    </div>

    <template v-else>
      <!-- ── Top bar ─────────────────────────────────────────────── -->
      <div class="px-4 md:px-6 py-3 flex items-center gap-4 border-b shrink-0"
           style="background: var(--color-surface-01); border-color: var(--color-surface-04)">
        <RouterLink to="/courses" class="text-sm shrink-0 hover:opacity-70 transition"
                    style="color: var(--color-text-muted)">← Quay lại</RouterLink>
        <span class="truncate font-medium text-sm" style="color: var(--color-text-base)">{{ exercise.title }}</span>
        <span class="shrink-0 px-2 py-0.5 rounded text-xs font-semibold ml-auto"
              style="background: rgba(79,70,229,0.15); color: #818cf8">{{ exercise.cefr_level }}</span>
      </div>

      <!-- ── Split body ─────────────────────────────────────────── -->
      <div class="flex flex-col md:flex-row flex-1 overflow-hidden">

        <!-- LEFT: Scenario + Karaoke (50%) -->
        <aside class="md:w-1/2 overflow-y-auto p-4 md:p-6 space-y-4 border-b md:border-b-0 md:border-r"
               style="background: var(--color-surface-01); border-color: var(--color-surface-04)">

          <!-- Scenario -->
          <div v-if="exercise.scenario" class="rounded-2xl p-4"
               style="background: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <p class="text-xs font-semibold uppercase tracking-wider mb-2" style="color: var(--color-text-muted)">
              🎭 Tình huống
            </p>
            <p class="text-sm leading-relaxed" style="color: var(--color-text-base)">{{ exercise.scenario }}</p>
          </div>

          <!-- Dialogue -->
          <div v-if="exercise.dialogue_json?.length" class="space-y-2">
            <p class="text-xs font-semibold uppercase tracking-wider" style="color: var(--color-text-muted)">💬 Hội thoại</p>
            <div v-for="(line, i) in exercise.dialogue_json" :key="i"
                 class="flex gap-3"
                 :class="line.role?.toUpperCase() === 'AI' ? 'flex-row' : 'flex-row-reverse'">
              <div class="w-8 h-8 rounded-full shrink-0 flex items-center justify-center text-xs font-bold"
                   :style="line.role?.toUpperCase() === 'AI'
                     ? 'background: rgba(79,70,229,0.2); color: #818cf8'
                     : 'background: rgba(34,197,94,0.2); color: #4ade80'">
                {{ line.role?.toUpperCase() === 'AI' ? 'AI' : 'You' }}
              </div>
              <div class="max-w-[80%] px-3 py-2 rounded-2xl text-sm"
                   :style="line.role?.toUpperCase() === 'AI'
                     ? 'background: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-text-base)'
                     : 'background: rgba(79,70,229,0.15); color: var(--color-text-base)'">
                {{ line.text }}
              </div>
            </div>
          </div>

          <!-- Target sentence / Karaoke display -->
          <div class="rounded-2xl p-5"
               style="background: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <div class="flex items-center justify-between mb-3">
              <p class="text-xs font-semibold uppercase tracking-wider" style="color: var(--color-text-muted)">
                🗣 Câu cần nói
              </p>
              <!-- Sample audio button -->
              <button v-if="exercise.sample_audio_url" @click="toggleSample"
                      class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition"
                      :style="samplePlaying
                        ? 'background: rgba(99,102,241,0.2); color: #818cf8'
                        : 'background: var(--color-surface-03); color: var(--color-text-base)'">
                <span>{{ samplePlaying ? '⏹' : '🔊' }}</span>
                {{ samplePlaying ? 'Dừng' : 'Nghe mẫu' }}
              </button>
            </div>

            <!-- Karaoke words -->
            <div class="flex flex-wrap gap-2">
              <span v-for="(word, idx) in karaokeWords" :key="idx"
                    class="px-2 py-1 rounded-lg text-base font-semibold transition-all duration-100"
                    :style="getWordStyle(idx)">
                {{ word.word }}
              </span>
              <!-- Fallback plain text if no karaoke data -->
              <span v-if="!karaokeWords.length" class="text-lg font-semibold leading-relaxed"
                    style="color: var(--color-text-base)">{{ exercise.target_sentence }}</span>
            </div>

            <!-- Hidden sample audio element -->
            <audio ref="sampleAudioRef" :src="exercise.sample_audio_url"
                   @ended="onSampleEnded" class="hidden"></audio>
          </div>

          <!-- Instructions -->
          <div class="rounded-xl px-4 py-3 text-xs leading-relaxed"
               style="background: rgba(99,102,241,0.08); color: var(--color-text-muted)">
            <strong style="color: #818cf8">Hướng dẫn:</strong>
            Nghe mẫu trước, sau đó bấm 🔴 để ghi âm. Nói rõ ràng và tự nhiên. Thời gian tối đa {{ maxSeconds }}s.
          </div>
        </aside>

        <!-- RIGHT: Recorder (50%) -->
        <main class="md:w-1/2 overflow-y-auto p-4 md:p-6 flex flex-col gap-5"
              style="background: var(--color-surface-01)">

          <!-- Stage indicator -->
          <div class="flex items-center justify-center gap-0">
            <div v-for="(stage, i) in stages" :key="i" class="flex items-center">
              <div class="flex flex-col items-center gap-1">
                <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition"
                     :style="currentStageIndex >= i
                       ? 'background: #4f46e5; color: white'
                       : 'background: var(--color-surface-03); color: var(--color-text-muted)'">
                  {{ i + 1 }}
                </div>
                <span class="text-xs" style="color: var(--color-text-muted)">{{ stage }}</span>
              </div>
              <div v-if="i < stages.length - 1" class="w-10 h-0.5 mb-4"
                   :style="currentStageIndex > i ? 'background: #4f46e5' : 'background: var(--color-surface-04)'"></div>
            </div>
          </div>

          <!-- Waveform canvas -->
          <div class="rounded-2xl overflow-hidden flex items-end justify-center"
               style="height: 80px; background: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <canvas v-if="recordingState === 'recording'" ref="canvasRef"
                    class="w-full h-full" width="400" height="80"></canvas>
            <div v-else class="flex items-center justify-center w-full h-full gap-1">
              <div v-for="n in 20" :key="n"
                   class="w-1.5 rounded-full"
                   :style="`height: ${recordingState === 'idle' ? 8 : Math.random() * 30 + 8}px; background: var(--color-surface-04)`"></div>
            </div>
          </div>

          <!-- Record button + timer -->
          <div class="flex flex-col items-center gap-3">
            <button @click="toggleRecord"
                    :disabled="recordingState === 'done'"
                    class="relative flex items-center justify-center rounded-full transition focus:outline-none disabled:opacity-40"
                    style="width: 80px; height: 80px"
                    :title="recordingState === 'recording' ? 'Dừng ghi' : 'Bắt đầu ghi'">
              <!-- Pulse ring when recording -->
              <span v-if="recordingState === 'recording'"
                    class="absolute inset-0 rounded-full animate-ping opacity-40"
                    style="background: rgba(239,68,68,0.4)"></span>
              <!-- Button body -->
              <span class="relative z-10 w-full h-full rounded-full flex items-center justify-center text-2xl shadow-lg"
                    :style="recordingState === 'recording'
                      ? 'background: rgba(239,68,68,0.15); border: 2px solid #ef4444'
                      : 'background: linear-gradient(135deg, #4f46e5, #7c3aed)'">
                <span v-if="recordingState === 'recording'" style="color: #ef4444">⏹</span>
                <span v-else style="color: white">🎙</span>
              </span>
            </button>

            <!-- Timer -->
            <p class="text-sm font-mono font-semibold"
               :style="recordingState === 'recording' && recordingSeconds >= maxSeconds - 10 ? 'color: #ef4444' : 'color: var(--color-text-muted)'">
              <template v-if="recordingState === 'recording'">
                {{ formatTime(recordingSeconds) }} / {{ formatTime(maxSeconds) }}
              </template>
              <template v-else-if="recordingState === 'review'">
                Đã ghi {{ formatTime(recordedDuration) }}
              </template>
              <template v-else>
                Tối đa {{ formatTime(maxSeconds) }}
              </template>
            </p>

            <p class="text-xs text-center" style="color: var(--color-text-muted)">
              <template v-if="recordingState === 'idle'">Nhấn để bắt đầu ghi âm</template>
              <template v-else-if="recordingState === 'recording'">Đang ghi... nhấn để dừng</template>
              <template v-else-if="recordingState === 'review'">Ghi âm hoàn tất. Nghe lại hoặc ghi lại.</template>
            </p>
          </div>

          <!-- Playback review -->
          <Transition name="slide-up">
            <div v-if="recordingState === 'review' && audioBlob"
                 class="rounded-2xl p-4 space-y-3"
                 style="background: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
              <p class="text-xs font-semibold uppercase tracking-wider" style="color: var(--color-text-muted)">
                🎧 Xem lại bản ghi
              </p>
              <audio :src="recordingUrl" controls class="w-full rounded-lg" style="height: 36px"></audio>
              <div class="flex gap-2">
                <button @click="resetRecording"
                        class="flex-1 py-2 rounded-xl text-sm font-semibold transition"
                        style="background: var(--color-surface-03); color: var(--color-text-base)">
                  🔄 Ghi lại
                </button>
                <button @click="submit" :disabled="submitting"
                        class="flex-1 py-2 rounded-xl text-sm font-semibold text-white transition disabled:opacity-50"
                        style="background: linear-gradient(135deg, #4f46e5, #7c3aed)">
                  <span v-if="submitting" class="flex items-center justify-center gap-1.5">
                    <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="10" stroke="white" stroke-width="3" stroke-dasharray="30 70"/>
                    </svg>
                    Đang nộp...
                  </span>
                  <span v-else>✓ Nộp bài</span>
                </button>
              </div>
            </div>
          </Transition>

          <!-- Submit from idle (if already has audio) shouldn't appear; just the review block covers it -->
        </main>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getExercise } from '@/api/curriculum.js'
import { progressApi } from '@/api/progress.js'

const route = useRoute()
const router = useRouter()

// ── State ────────────────────────────────────────────────────────────────────
const exercise = ref(null)
const loading = ref(false)
const submitting = ref(false)

// Recording
const recordingState = ref('idle')   // idle | recording | review
const audioBlob = ref(null)
const recordingUrl = ref(null)
const recordingSeconds = ref(0)
const recordedDuration = ref(0)
let mediaRecorder = null
let recordingStream = null
let chunks = []
let recordingInterval = null

// Waveform
const canvasRef = ref(null)
let audioContext = null
let analyser = null
let animFrameId = null

// Sample audio
const sampleAudioRef = ref(null)
const samplePlaying = ref(false)
const highlightedWordIndex = ref(-1)
let karaokeInterval = null

// ── Computed ─────────────────────────────────────────────────────────────────
const maxSeconds = computed(() => exercise.value?.time_limit_seconds || 60)

const karaokeWords = computed(() => {
  const arr = exercise.value?.karaoke_words_json
  if (!Array.isArray(arr) || !arr.length) return []
  return arr
})

const stages = ['Nghe mẫu', 'Ghi âm', 'Xem lại']
const currentStageIndex = computed(() => {
  if (recordingState.value === 'review') return 2
  if (recordingState.value === 'recording') return 1
  return 0
})

// ── Lifecycle ────────────────────────────────────────────────────────────────
onMounted(async () => {
  loading.value = true
  try {
    const res = await getExercise('speaking', route.params.id)
    exercise.value = res.data?.data ?? res.data
  } catch {
    exercise.value = null
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  // SECURITY: always release microphone on unmount
  if (mediaRecorder?.state === 'recording') {
    mediaRecorder.stop()
  }
  if (recordingStream) {
    recordingStream.getTracks().forEach(t => t.stop())
    recordingStream = null
  }
  if (audioContext) {
    audioContext.close()
    audioContext = null
  }
  if (animFrameId) cancelAnimationFrame(animFrameId)
  if (recordingInterval) clearInterval(recordingInterval)
  if (karaokeInterval) clearInterval(karaokeInterval)
  if (sampleAudioRef.value && !sampleAudioRef.value.paused) {
    sampleAudioRef.value.pause()
  }
  if (recordingUrl.value) URL.revokeObjectURL(recordingUrl.value)
})

// ── Sample audio ─────────────────────────────────────────────────────────────
function toggleSample() {
  if (!sampleAudioRef.value) return
  if (samplePlaying.value) {
    sampleAudioRef.value.pause()
    sampleAudioRef.value.currentTime = 0
    samplePlaying.value = false
    stopKaraokeHighlight()
  } else {
    sampleAudioRef.value.play()
    samplePlaying.value = true
    startKaraokeHighlight()
  }
}

function onSampleEnded() {
  samplePlaying.value = false
  stopKaraokeHighlight()
  // Keep last word highlighted briefly then clear
  setTimeout(() => { highlightedWordIndex.value = -1 }, 600)
}

function startKaraokeHighlight() {
  if (!karaokeWords.value.length || !sampleAudioRef.value) return
  karaokeInterval = setInterval(() => {
    const nowMs = (sampleAudioRef.value?.currentTime ?? 0) * 1000
    const idx = karaokeWords.value.findIndex((w, i) => {
      const next = karaokeWords.value[i + 1]
      return nowMs >= w.start_ms && (!next || nowMs < next.start_ms)
    })
    highlightedWordIndex.value = idx
  }, 80)
}

function stopKaraokeHighlight() {
  if (karaokeInterval) { clearInterval(karaokeInterval); karaokeInterval = null }
}

function getWordStyle(idx) {
  const isActive = idx === highlightedWordIndex.value
  const isPast = idx < highlightedWordIndex.value
  if (isActive) return 'background: rgba(99,102,241,0.25); color: #818cf8; transform: scale(1.05)'
  if (isPast) return 'background: var(--color-surface-02); color: var(--color-text-muted); opacity: 0.6'
  return 'background: var(--color-surface-02); color: var(--color-text-base)'
}

// ── Recording ────────────────────────────────────────────────────────────────
async function toggleRecord() {
  if (recordingState.value === 'recording') {
    stopRecording()
  } else {
    await startRecording()
  }
}

async function startRecording() {
  chunks = []
  audioBlob.value = null
  if (recordingUrl.value) { URL.revokeObjectURL(recordingUrl.value); recordingUrl.value = null }

  try {
    recordingStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false })
  } catch {
    alert('Không thể truy cập microphone. Vui lòng cấp quyền.')
    return
  }

  // Web Audio waveform
  audioContext = new (window.AudioContext || window.webkitAudioContext)()
  analyser = audioContext.createAnalyser()
  analyser.fftSize = 128
  const source = audioContext.createMediaStreamSource(recordingStream)
  source.connect(analyser)

  mediaRecorder = new MediaRecorder(recordingStream)
  mediaRecorder.ondataavailable = e => { if (e.data.size > 0) chunks.push(e.data) }
  mediaRecorder.onstop = () => {
    audioBlob.value = new Blob(chunks, { type: 'audio/webm' })
    recordingUrl.value = URL.createObjectURL(audioBlob.value)
    recordedDuration.value = recordingSeconds.value
    recordingState.value = 'review'
    stopWaveform()
    recordingStream?.getTracks().forEach(t => t.stop())
    recordingStream = null
  }

  mediaRecorder.start(100)
  recordingState.value = 'recording'
  recordingSeconds.value = 0

  // Timer
  recordingInterval = setInterval(() => {
    recordingSeconds.value++
    if (recordingSeconds.value >= maxSeconds.value) stopRecording()
  }, 1000)

  // Draw waveform after next tick so canvas is in DOM
  nextTick(() => drawWaveform())
}

function stopRecording() {
  if (recordingInterval) { clearInterval(recordingInterval); recordingInterval = null }
  if (mediaRecorder?.state === 'recording') mediaRecorder.stop()
}

function stopWaveform() {
  if (animFrameId) { cancelAnimationFrame(animFrameId); animFrameId = null }
  if (audioContext) { audioContext.close(); audioContext = null }
  analyser = null
}

function drawWaveform() {
  if (!analyser) return
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const bufLen = analyser.frequencyBinCount
  const data = new Uint8Array(bufLen)

  function loop() {
    animFrameId = requestAnimationFrame(loop)
    analyser.getByteFrequencyData(data)
    const w = canvas.width
    const h = canvas.height
    ctx.clearRect(0, 0, w, h)
    const barW = (w / bufLen) * 2
    let x = 0
    for (let i = 0; i < bufLen; i++) {
      const barH = (data[i] / 255) * h
      const alpha = 0.4 + (data[i] / 255) * 0.6
      ctx.fillStyle = `rgba(129,140,248,${alpha})`
      ctx.fillRect(x, h - barH, barW, barH)
      x += barW + 1
    }
  }
  loop()
}

function resetRecording() {
  if (recordingUrl.value) { URL.revokeObjectURL(recordingUrl.value); recordingUrl.value = null }
  audioBlob.value = null
  recordingState.value = 'idle'
  recordingSeconds.value = 0
  recordedDuration.value = 0
}

// ── Submit ───────────────────────────────────────────────────────────────────
async function submit() {
  if (!audioBlob.value || submitting.value) return
  submitting.value = true
  try {
    const fd = new FormData()
    fd.append('exercise_id', exercise.value.id)
    if (route.query.lesson_id) fd.append('lesson_id', route.query.lesson_id)
    fd.append('audio_file', audioBlob.value, 'recording.webm')
    const res = await progressApi.submitSpeaking(fd)
    const d = res.data?.data ?? res.data
    const submissionId = d?.submission_id ?? d?.id
    router.push(`/learn/result/${submissionId}?type=speaking`)
  } catch {
    // TODO: error toast
  } finally {
    submitting.value = false
  }
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function formatTime(sec) {
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}
</script>

<style scoped>
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s ease; }
.slide-up-enter-from { opacity: 0; transform: translateY(12px); }
.slide-up-leave-to   { opacity: 0; transform: translateY(12px); }
</style>

