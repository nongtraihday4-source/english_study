<template>
  <div>
    <!-- Section header -->
    <div class="flex items-center gap-2 mb-4">
      <span class="text-xl">🗣️</span>
      <span class="text-base font-bold" style="color:var(--color-text-base)">Luyện nói</span>
      <span v-if="allDone"
            class="ml-auto text-xs font-medium px-2.5 py-0.5 rounded-full"
            style="background:rgba(34,197,94,0.15);color:#86efac">
        ✓ Hoàn thành
      </span>
      <span v-else-if="doneSentences > 0"
            class="ml-auto text-xs font-medium px-2.5 py-0.5 rounded-full"
            style="background:rgba(6,182,212,0.12);color:#22d3ee">
        {{ doneSentences }}/{{ totalSentences }}
      </span>
    </div>

    <!-- Mode badge -->
    <p class="text-xs mb-4" style="color:var(--color-text-muted)">
      <span v-if="content.mode === 'repeat'">🔁 Nghe và nhắc lại từng câu</span>
      <span v-else-if="content.mode === 'shadow'">👥 Shadow: nói cùng lúc với người bản ngữ</span>
      <span v-else-if="content.mode === 'dialogue'">💬 Luyện đối thoại</span>
    </p>

    <!-- Sentence cards -->
    <div class="space-y-4">
      <div v-for="(s, si) in content.sentences" :key="si"
           class="rounded-2xl overflow-hidden"
           style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
        <!-- Card header: index + status -->
        <div class="flex items-center justify-between px-4 py-2.5"
             style="background-color:var(--color-surface-03);border-bottom:1px solid var(--color-surface-04)">
          <span class="text-xs font-semibold" style="color:var(--color-text-muted)">
            Câu {{ si + 1 }}/{{ totalSentences }}
          </span>
          <span v-if="ratings[si]" class="text-xs font-medium px-2 py-0.5 rounded-full"
                :style="ratingBadgeStyle(ratings[si])">
            {{ ratingLabel(ratings[si]) }}
          </span>
          <span v-else-if="playCount[si]" class="text-xs" style="color:#22d3ee">
            {{ step[si] === 'rate' ? 'Đánh giá ↓' : `Nghe ${playCount[si]}x` }}
          </span>
        </div>

        <!-- Body -->
        <div class="px-5 py-4">
          <!-- Text / translation toggles -->
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <div v-if="showText[si]">
                <p class="text-base font-medium" style="color:var(--color-text-base)">{{ s.text }}</p>
                <p v-if="showTranslation[si]" class="text-sm mt-1" style="color:var(--color-text-muted)">
                  {{ s.translation_vi }}
                </p>
              </div>
              <p v-else class="text-sm italic" style="color:var(--color-text-muted)">
                (lời bài ẩn — hãy nghe trước)
              </p>
              <!-- Focus words -->
              <div v-if="s.focus_words?.length" class="flex flex-wrap gap-1.5 mt-2">
                <span v-for="w in s.focus_words" :key="w"
                      class="px-2 py-0.5 rounded-lg text-xs font-medium"
                      style="background:rgba(6,182,212,0.1);color:#22d3ee;border:1px solid rgba(6,182,212,0.2)">
                  {{ w }}
                </span>
              </div>
            </div>
            <div class="flex gap-2 ml-4 shrink-0">
              <button @click="showText[si] = !showText[si]"
                      class="text-xs px-2 py-1 rounded-lg transition"
                      style="background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)">
                {{ showText[si] ? 'Ẩn lời' : 'Hiện lời' }}
              </button>
              <button v-if="showText[si]"
                      @click="showTranslation[si] = !showTranslation[si]"
                      class="text-xs px-2 py-1 rounded-lg transition"
                      style="background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)">
                {{ showTranslation[si] ? 'Ẩn dịch' : 'Hiện dịch' }}
              </button>
            </div>
          </div>

          <!-- Action row -->
          <div v-if="!ratings[si]" class="flex items-center gap-3">
            <!-- Speed selector -->
            <div class="flex gap-1">
              <button v-for="sp in speeds" :key="sp"
                      @click="setSpeed(si, sp)"
                      class="px-2 py-1 rounded-lg text-xs font-medium transition"
                      :style="sentenceSpeed[si] === sp
                        ? 'background:rgba(6,182,212,0.25);color:#22d3ee;border:1px solid rgba(6,182,212,0.4)'
                        : 'background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)'">
                {{ sp }}x
              </button>
            </div>

            <button @click="playSentence(si, s)"
                    :disabled="loadingSentence[si]"
                    class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition hover:opacity-80 ml-auto"
                    style="background:rgba(6,182,212,0.12);color:#22d3ee;border:1px solid rgba(6,182,212,0.25)">
              <span v-if="loadingSentence[si]" class="animate-spin">⏳</span>
              <span v-else>🔊 Nghe</span>
            </button>
          </div>

          <!-- Rate prompt (shown after at least 1 play) -->
          <div v-if="step[si] === 'rate' && !ratings[si]"
               class="mt-4 pt-4"
               style="border-top:1px solid var(--color-surface-04)">
              <p class="text-xs mb-3 font-medium" style="color:var(--color-text-muted)">
                Tự đánh giá phát âm của bạn:
              </p>
              <div class="flex gap-2">
                <button @click="rate(si, 'poor')"
                        class="flex-1 flex flex-col items-center gap-1 px-3 py-2.5 rounded-xl text-xs font-medium transition hover:opacity-80"
                        style="background:rgba(239,68,68,0.1);color:#fca5a5;border:1px solid rgba(239,68,68,0.25)">
                  <span class="text-lg">😕</span> Cần luyện thêm
                </button>
                <button @click="rate(si, 'ok')"
                        class="flex-1 flex flex-col items-center gap-1 px-3 py-2.5 rounded-xl text-xs font-medium transition hover:opacity-80"
                        style="background:rgba(251,191,36,0.1);color:#fbbf24;border:1px solid rgba(251,191,36,0.25)">
                  <span class="text-lg">😊</span> Được rồi
                </button>
                <button @click="rate(si, 'great')"
                        class="flex-1 flex flex-col items-center gap-1 px-3 py-2.5 rounded-xl text-xs font-medium transition hover:opacity-80"
                        style="background:rgba(34,197,94,0.1);color:#86efac;border:1px solid rgba(34,197,94,0.25)">
                  <span class="text-lg">🎯</span> Tốt lắm
                </button>
              </div>
          </div>

          <!-- Rated state -->
          <div v-if="ratings[si]"
                 class="mt-3 px-3 py-2.5 rounded-xl flex items-center gap-3"
                 :style="ratingCardStyle(ratings[si])">
              <span class="text-xl">{{ ratingEmoji(ratings[si]) }}</span>
              <div>
                <p class="text-sm font-medium" :style="ratingTextStyle(ratings[si])">
                  {{ ratingLabel(ratings[si]) }}
                </p>
                <p class="text-xs mt-0.5" style="color:var(--color-text-muted)">{{ s.text }}</p>
              </div>
              <button @click="retry(si)"
                      class="ml-auto text-xs px-2.5 py-1 rounded-lg transition"
                      style="background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)">
                Luyện lại
              </button>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import apiClient from '@/api/client.js'

const props = defineProps({
  content: { type: Object, required: true },
})
const emit = defineEmits(['progress'])

const speeds = [0.75, 1.0, 1.25]

const sentences = computed(() => props.content.sentences ?? [])
const totalSentences = computed(() => sentences.value.length)

// Per-sentence state
const showText        = reactive({})
const showTranslation = reactive({})
const sentenceSpeed   = reactive({})
const playCount       = reactive({})
const loadingSentence = reactive({})
const step            = reactive({})   // 'idle' | 'rate'
const ratings         = reactive({})   // 'poor' | 'ok' | 'great'
const audioBlobCache  = reactive({})   // si → object URL

// ── Progress ─────────────────────────────────────────────────────────────────
const doneSentences = computed(() =>
  Object.keys(ratings).filter(k => ratings[k]).length
)
const allDone = computed(() =>
  totalSentences.value > 0 && doneSentences.value >= totalSentences.value
)

function emitProgress() {
  emit('progress', { done: doneSentences.value, total: totalSentences.value })
}

// Initialize defaults
watch(() => sentences.value, (sents) => {
  sents.forEach((s, si) => {
    if (sentenceSpeed[si] === undefined) sentenceSpeed[si] = s.speed ?? 1.0
    if (showText[si] === undefined)      showText[si]      = false
    if (step[si] === undefined)          step[si]          = 'idle'
  })
  emitProgress()
}, { immediate: true })

async function playSentence(si, s) {
  if (loadingSentence[si]) return
  const speed = sentenceSpeed[si] ?? 1.0

  loadingSentence[si] = true
  try {
    const cacheKey = `${si}:${speed}`
    if (!audioBlobCache[cacheKey]) {
      const resp = await apiClient.get('/pronunciation/tts/', {
        params: { text: s.text, speed },
        responseType: 'blob',
      })
      audioBlobCache[cacheKey] = URL.createObjectURL(resp.data)
    }
    const audio = new Audio(audioBlobCache[cacheKey])
    audio.play()
    playCount[si] = (playCount[si] ?? 0) + 1
    if (step[si] === 'idle') step[si] = 'rate'
  } catch (e) {
    console.error('TTS error', e)
  } finally {
    loadingSentence[si] = false
  }
}

function setSpeed(si, sp) {
  sentenceSpeed[si] = sp
}

function rate(si, rating) {
  ratings[si] = rating
  emitProgress()
}

function retry(si) {
  ratings[si]  = undefined
  playCount[si] = 0
  step[si]     = 'idle'
  emitProgress()
}

// ── Rating helpers ────────────────────────────────────────────────────────────
function ratingLabel(r) {
  return r === 'great' ? '🎯 Tốt lắm!' : r === 'ok' ? '😊 Được rồi' : '😕 Cần luyện thêm'
}
function ratingEmoji(r) {
  return r === 'great' ? '🎯' : r === 'ok' ? '😊' : '😕'
}
function ratingBadgeStyle(r) {
  if (r === 'great') return 'background:rgba(34,197,94,0.15);color:#86efac'
  if (r === 'ok')    return 'background:rgba(251,191,36,0.15);color:#fbbf24'
  return 'background:rgba(239,68,68,0.15);color:#fca5a5'
}
function ratingCardStyle(r) {
  if (r === 'great') return 'background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.25)'
  if (r === 'ok')    return 'background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.25)'
  return 'background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.25)'
}
function ratingTextStyle(r) {
  if (r === 'great') return 'color:#86efac'
  if (r === 'ok')    return 'color:#fbbf24'
  return 'color:#fca5a5'
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity .25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
