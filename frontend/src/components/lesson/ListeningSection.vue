<template>
  <div>
    <!-- Section header -->
    <div class="flex items-center gap-2 mb-4">
      <span class="text-xl">🎧</span>
      <span class="text-base font-bold" style="color:var(--color-text-base)">Luyện nghe</span>
      <span v-if="allDone"
            class="ml-auto text-xs font-medium px-2.5 py-0.5 rounded-full"
            style="background:rgba(34,197,94,0.15);color:#86efac">
        ✓ Hoàn thành
      </span>
      <span v-else-if="exerciseDone > 0"
            class="ml-auto text-xs font-medium px-2.5 py-0.5 rounded-full"
            style="background:rgba(6,182,212,0.12);color:#22d3ee">
        {{ exerciseDone }}/{{ exerciseTotal }}
      </span>
    </div>

    <!-- Audio player card -->
    <div class="rounded-2xl overflow-hidden mb-5"
         style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">

      <!-- Toolbar -->
      <div class="flex items-center gap-2 px-4 py-2.5"
           style="border-bottom:1px solid var(--color-surface-04);background-color:var(--color-surface-03)">
        <button @click="togglePlay" :disabled="ttsLoading"
                class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition hover:opacity-80"
                style="background:rgba(6,182,212,0.12);color:#22d3ee;border:1px solid rgba(6,182,212,0.25)">
          <span v-if="ttsLoading" class="inline-block animate-spin">⏳</span>
          <span v-else-if="ttsPlaying">⏸ Dừng</span>
          <span v-else>▶ Nghe bài</span>
        </button>
        <div class="flex gap-1 ml-auto">
          <button v-for="sp in speeds" :key="sp"
                  @click="setPlaySpeed(sp)"
                  class="px-2 py-1 rounded-lg text-xs font-medium transition"
                  :style="currentSpeed === sp
                    ? 'background:rgba(6,182,212,0.25);color:#22d3ee;border:1px solid rgba(6,182,212,0.4)'
                    : 'background:var(--color-surface-02);color:var(--color-text-muted);border:1px solid var(--color-surface-04)'">
            {{ sp }}x
          </button>
        </div>
      </div>

      <!-- Transcript (hidden until revealed) -->
      <div class="px-5 py-4">
        <div v-if="!transcriptRevealed" class="flex items-center justify-between">
          <p class="text-sm" style="color:var(--color-text-muted)">
            🎧 Nghe bài trước, sau đó trả lời câu hỏi bên dưới.
          </p>
          <button @click="revealTranscript"
                  class="text-xs px-3 py-1.5 rounded-lg transition hover:opacity-80"
                  style="background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)">
            Hiện lời
          </button>
        </div>
        <div v-else class="space-y-2">
          <div class="flex items-center justify-between mb-2">
            <p class="text-xs font-semibold uppercase tracking-wide" style="color:var(--color-text-muted)">Lời bài nghe</p>
            <button @click="transcriptRevealed = false"
                    class="text-xs" style="color:var(--color-text-muted)">Ẩn</button>
          </div>
          <div v-for="(s, si) in content.sentences" :key="si"
               class="px-3 py-2 rounded-lg"
               style="background:var(--color-surface-03)">
            <div class="flex items-center gap-2">
              <button @click="playSentence(s.text, si)"
                      class="text-xs px-2 py-0.5 rounded transition hover:opacity-70"
                      style="background:rgba(6,182,212,0.1);color:#22d3ee;border:1px solid rgba(6,182,212,0.2)">
                ▶
              </button>
              <p class="text-sm flex-1" style="color:var(--color-text-base)">{{ s.text }}</p>
            </div>
            <p class="text-xs mt-1 ml-8" style="color:var(--color-text-muted)">{{ s.translation_vi }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Comprehension Questions -->
    <div v-if="content.comprehension_questions?.length"
         class="rounded-2xl overflow-hidden mb-5"
         style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
      <div class="flex items-center justify-between px-5 py-3"
           style="background-color:var(--color-surface-03);border-bottom:1px solid var(--color-surface-04)">
        <span class="font-semibold text-sm" style="color:var(--color-text-base)">❓ Câu hỏi đọc hiểu</span>
        <span v-if="mcqAnswered > 0"
              class="text-xs font-medium px-2 py-0.5 rounded-full"
              style="background:rgba(6,182,212,0.15);color:#22d3ee">
          {{ mcqCorrect }}/{{ mcqAnswered }} đúng
        </span>
      </div>
      <div class="px-5 py-4 space-y-6">
        <div v-for="(q, qi) in content.comprehension_questions" :key="qi">
          <p class="font-medium text-sm mb-3" style="color:var(--color-text-base)">
            {{ qi + 1 }}. {{ q.question }}
          </p>
          <div class="grid grid-cols-1 gap-2">
            <button v-for="(opt, oi) in q.options" :key="oi"
                    @click="selectMCQ(qi, oi)"
                    :disabled="mcqAnswers[qi] !== undefined"
                    class="text-left px-4 py-2.5 rounded-xl text-sm transition"
                    :style="mcqStyle(qi, oi, q.correct)">
              <span class="font-mono mr-2 text-xs opacity-60">{{ String.fromCharCode(65 + oi) }}</span>{{ opt }}
            </button>
          </div>
          <div v-if="mcqAnswers[qi] !== undefined"
               class="mt-2 px-3 py-2 rounded-xl text-xs"
               :style="mcqAnswers[qi] === q.correct
                 ? 'background:rgba(34,197,94,0.1);color:#86efac'
                 : 'background:rgba(239,68,68,0.1);color:#fca5a5'">
            {{ mcqAnswers[qi] === q.correct ? '✓ Đúng! ' : '✗ Sai. ' }}{{ q.explanation }}
          </div>
        </div>
      </div>
    </div>

    <!-- Dictation exercises -->
    <div v-if="content.dictation_sentences?.length"
         class="rounded-2xl overflow-hidden"
         style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
      <div class="flex items-center justify-between px-5 py-3"
           style="background-color:var(--color-surface-03);border-bottom:1px solid var(--color-surface-04)">
        <div class="flex items-center gap-2">
          <span class="text-sm">✍️</span>
          <span class="font-semibold text-sm" style="color:var(--color-text-base)">Chính tả</span>
          <span class="text-xs" style="color:var(--color-text-muted)">Nghe và gõ lại câu</span>
        </div>
        <span class="text-xs font-medium px-2 py-0.5 rounded-full"
              :style="dictationAllDone
                ? 'background:rgba(34,197,94,0.15);color:#86efac'
                : 'background:rgba(6,182,212,0.12);color:#22d3ee'">
          {{ dictationDone }}/{{ content.dictation_sentences.length }}
        </span>
      </div>
      <div class="px-5 py-4 space-y-6">
        <div v-for="(sentence, si) in content.dictation_sentences" :key="si">
          <p v-if="content.dictation_sentences.length > 1"
             class="text-xs font-medium mb-3" style="color:var(--color-text-muted)">
            Bài {{ si + 1 }}/{{ content.dictation_sentences.length }}
          </p>
          <InlineDictation
            :sentence="sentence"
            :done="dictationDoneMap[si]"
            @complete="markDictationDone(si)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onUnmounted } from 'vue'
import { usePassageTTS } from '@/composables/usePassageTTS.js'

// ── InlineDictation sub-component (defined below via defineComponent pattern)
import InlineDictation from './InlineDictation.vue'

const props = defineProps({
  content: { type: Object, required: true },
})
const emit = defineEmits(['progress'])

// ── TTS ──────────────────────────────────────────────────────────────────────
const { play, pause, resume, stop, setRate, isPlaying, isPaused, isLoading } = usePassageTTS()
const currentSpeed = ref(props.content.speed ?? 1.0)
const speeds = [0.75, 1.0, 1.25]

const ttsLoading = computed(() => isLoading.value)
const ttsPlaying = computed(() => isPlaying.value)

function stripHtml(html) {
  const el = document.createElement('div'); el.innerHTML = html
  return el.innerText || el.textContent || ''
}

function togglePlay() {
  if (isPlaying.value) { pause(); return }
  if (isPaused.value) { resume(); return }
  play(props.content.audio_text, undefined, currentSpeed.value)
}

function playSentence(text, _idx) {
  stop()
  setTimeout(() => play(text, undefined, currentSpeed.value), 80)
}

function setPlaySpeed(sp) {
  currentSpeed.value = sp
  if (isPlaying.value) { stop(); play(props.content.audio_text, undefined, sp) }
  else if (isPaused.value) { stop() }
  setRate(sp)
}

onUnmounted(() => stop())

// ── Transcript reveal ─────────────────────────────────────────────────────────
const transcriptRevealed = ref(false)
function revealTranscript() { transcriptRevealed.value = true }

// ── MCQ tracking ──────────────────────────────────────────────────────────────
const mcqAnswers = reactive({})

const mcqAnswered = computed(() => Object.keys(mcqAnswers).length)
const mcqCorrect  = computed(() =>
  Object.entries(mcqAnswers).filter(([qi, oi]) =>
    oi === (props.content.comprehension_questions?.[Number(qi)]?.correct ?? -1)
  ).length
)

function selectMCQ(qi, oi) {
  if (mcqAnswers[qi] !== undefined) return
  mcqAnswers[qi] = oi
  emitProgress()
}

function mcqStyle(qi, oi, correctOpt) {
  const ans = mcqAnswers[qi]
  const base = 'border:1px solid;'
  if (ans === undefined)
    return base + 'background:var(--color-surface-03);border-color:var(--color-surface-04);color:var(--color-text-base);cursor:pointer'
  if (oi === correctOpt)
    return base + 'background:rgba(34,197,94,0.12);border-color:rgba(34,197,94,0.4);color:#86efac'
  if (oi === ans)
    return base + 'background:rgba(239,68,68,0.12);border-color:rgba(239,68,68,0.4);color:#fca5a5'
  return base + 'background:var(--color-surface-03);border-color:var(--color-surface-04);color:var(--color-text-muted);opacity:0.5'
}

// ── Dictation tracking ────────────────────────────────────────────────────────
const dictationDoneMap = reactive({})

const dictationDone    = computed(() => Object.values(dictationDoneMap).filter(Boolean).length)
const dictationAllDone = computed(() =>
  (props.content.dictation_sentences?.length ?? 0) > 0 &&
  dictationDone.value >= props.content.dictation_sentences.length
)

function markDictationDone(si) {
  dictationDoneMap[si] = true
  emitProgress()
}

// ── Totals for parent progress ────────────────────────────────────────────────
const mcqTotal        = computed(() => props.content.comprehension_questions?.length ?? 0)
const dictationTotal  = computed(() => props.content.dictation_sentences?.length ?? 0)
const exerciseTotal   = computed(() => mcqTotal.value + dictationTotal.value)
const exerciseDone    = computed(() => mcqAnswered.value + dictationDone.value)
const exerciseCorrect = computed(() => mcqCorrect.value + dictationDone.value)

const allDone = computed(() =>
  exerciseDone.value >= exerciseTotal.value && exerciseTotal.value > 0
)

function emitProgress() {
  emit('progress', {
    done:    exerciseDone.value,
    correct: exerciseCorrect.value,
    total:   exerciseTotal.value,
  })
}

// Emit initial totals immediately
watch(() => props.content, () => emitProgress(), { immediate: true })
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity .25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
