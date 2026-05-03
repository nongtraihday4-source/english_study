<template>
  <!-- Section block: Reading 60/40 -->
  <div>
    <!-- Section header -->
    <div class="flex items-center gap-2 mb-4">
      <span class="text-xl">📖</span>
      <span class="text-base font-bold" style="color:var(--color-text-base)">Đọc hiểu</span>
      <span v-if="isDone && questions.length > 0"
            class="ml-auto text-xs font-medium px-2.5 py-0.5 rounded-full"
            style="background:rgba(34,197,94,0.15);color:#86efac">
        ✓ Hoàn thành
      </span>
    </div>

    <!-- 60/40 split -->
    <div class="flex flex-col lg:flex-row lg:gap-6 lg:items-start">

      <!-- Left 60%: Passage + Vocab footnote -->
      <div class="lg:w-[60%] min-w-0 space-y-4 mb-4 lg:mb-0">
        <div class="rounded-2xl overflow-hidden"
             style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
          <!-- TTS toolbar -->
          <div class="flex items-center gap-2 px-4 py-2.5"
               style="border-bottom:1px solid var(--color-surface-04);background-color:var(--color-surface-03)">
            <!-- Play / Pause button -->
            <button
              @click="togglePlay"
              :disabled="isLoading"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition hover:opacity-80"
              style="background:rgba(99,102,241,0.12);color:#818cf8;border:1px solid rgba(99,102,241,0.25)">
              <span v-if="isLoading" class="inline-block animate-spin">⏳</span>
              <span v-else-if="isPlaying">⏸</span>
              <span v-else-if="isPaused">▶</span>
              <span v-else>▶</span>
              <span v-if="isLoading">Đang tải...</span>
              <span v-else-if="isPlaying">Dừng</span>
              <span v-else-if="isPaused">Tiếp tục</span>
              <span v-else>Nghe bài đọc</span>
            </button>
            <!-- Stop button (only visible while active) -->
            <button
              v-if="isPlaying || isPaused"
              @click="stopTTS"
              class="flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-xs font-medium transition hover:opacity-80"
              style="background:var(--color-surface-04);color:var(--color-text-muted);border:1px solid var(--color-surface-04)">
              ⏹
            </button>
            <!-- Speed buttons -->
            <div class="flex gap-1 ml-auto">
              <button v-for="sp in [0.75, 1.0, 1.25, 1.5]" :key="sp"
                      @click="changeSpeed(sp)"
                      class="px-2 py-1 rounded-lg text-xs font-medium transition"
                      :style="ttsRate === sp
                        ? 'background:rgba(99,102,241,0.25);color:#818cf8;border:1px solid rgba(99,102,241,0.4)'
                        : 'background:var(--color-surface-02);color:var(--color-text-muted);border:1px solid var(--color-surface-04)'">
                {{ sp }}x
              </button>
            </div>
          </div>
          <div class="px-5 py-4 prose-lesson"
               style="color:var(--color-text-base);line-height:1.75;font-size:0.95rem"
               v-html="passage"></div>
        </div>
        <!-- Vocab footnotes below passage -->
        <VocabFootnote v-if="vocabItems?.length" :items="vocabItems" />
      </div>

      <!-- Right 40%: Reading MCQs -->
      <div class="lg:w-[40%] min-w-0 lg:sticky lg:top-20 lg:self-start">
        <div v-if="questions?.length"
             class="rounded-2xl overflow-hidden"
             style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
          <div class="flex items-center justify-between px-5 py-3"
               style="background-color:var(--color-surface-03);border-bottom:1px solid var(--color-surface-04)">
            <span class="font-semibold text-sm" style="color:var(--color-text-base)">❓ Câu hỏi đọc hiểu</span>
            <span v-if="answered > 0"
                  class="text-xs font-medium px-2 py-0.5 rounded-full"
                  style="background:rgba(99,102,241,0.15);color:#818cf8">
              {{ correct }}/{{ answered }} đúng
            </span>
          </div>
          <div class="px-5 py-4 space-y-6">
            <div v-for="(q, qi) in questions" :key="qi">
              <p class="font-medium text-sm mb-3" style="color:var(--color-text-base)">
                {{ qi + 1 }}. {{ q.question }}
              </p>
              <div class="grid grid-cols-1 gap-2">
                <button
                  v-for="(opt, oi) in q.options" :key="oi"
                  @click="selectAnswer(qi, oi)"
                  :disabled="answers[qi] !== undefined"
                  class="text-left px-4 py-2.5 rounded-xl text-sm transition"
                  :style="answerStyle(qi, oi, q.correct)"
                >
                  <span class="font-mono mr-2 text-xs opacity-60">{{ String.fromCharCode(65 + oi) }}</span>{{ opt }}
                </button>
              </div>
              <Transition name="fade">
                <div v-if="answers[qi] !== undefined"
                     class="mt-2 px-3 py-2 rounded-xl text-xs"
                     :style="answers[qi] === q.correct
                       ? 'background:rgba(34,197,94,0.1);color:#86efac'
                       : 'background:rgba(239,68,68,0.1);color:#fca5a5'">
                  {{ answers[qi] === q.correct ? '✓ Đúng! ' : '✗ Sai. ' }}{{ q.explanation }}
                </div>
              </Transition>
            </div>
          </div>
        </div>
        <!-- No questions placeholder -->
        <div v-else
             class="rounded-2xl p-6 text-center"
             style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
          <p class="text-sm" style="color:var(--color-text-muted)">📖 Đọc và ghi nhớ nội dung bài</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, watch, ref, onUnmounted } from 'vue'
import VocabFootnote from './VocabFootnote.vue'
import { usePassageTTS } from '@/composables/usePassageTTS.js'

const props = defineProps({
  passage:    { type: String, default: '' },
  questions:  { type: Array,  default: () => [] },
  vocabItems: { type: Array,  default: () => [] },
})

const emit = defineEmits(['progress'])

// ── TTS ──────────────────────────────────────────────────────────────────────
const { play, pause, resume, stop, setRate, isPlaying, isPaused, isLoading } = usePassageTTS()
const ttsRate = ref(1.0)

function stripHtml(html) {
  const el = document.createElement('div')
  el.innerHTML = html
  return el.innerText || el.textContent || ''
}

function togglePlay() {
  if (isPlaying.value) {
    pause()
  } else if (isPaused.value) {
    resume()
  } else {
    const text = stripHtml(props.passage)
    play(text, undefined, ttsRate.value)
  }
}

function changeSpeed(sp) {
  ttsRate.value = sp
  setRate(sp)
}

function stopTTS() {
  stop()
}

onUnmounted(() => { stop() })

// ── Answers ───────────────────────────────────────────────────────────────────
const answers = reactive({})

const answered = computed(() => Object.keys(answers).length)

const correct = computed(() =>
  props.questions.reduce((acc, q, qi) => acc + (answers[qi] === q.correct ? 1 : 0), 0)
)

const isDone = computed(() =>
  props.questions.length === 0 || answered.value >= props.questions.length
)

// Emit initial total so parent can initialize its tracking
watch(() => props.questions, (qs) => {
  emit('progress', { done: answered.value, correct: correct.value, total: qs.length })
}, { immediate: true })

function selectAnswer(qi, oi) {
  if (answers[qi] !== undefined) return
  answers[qi] = oi
  emit('progress', { done: answered.value, correct: correct.value, total: props.questions.length })
}

function answerStyle(qi, oi, correctOpt) {
  const ans = answers[qi]
  const base = 'border:1px solid;'
  if (ans === undefined)
    return base + 'background:var(--color-surface-03);border-color:var(--color-surface-04);color:var(--color-text-base);cursor:pointer'
  if (oi === correctOpt)
    return base + 'background:rgba(34,197,94,0.12);border-color:rgba(34,197,94,0.4);color:#86efac'
  if (oi === ans)
    return base + 'background:rgba(239,68,68,0.12);border-color:rgba(239,68,68,0.4);color:#fca5a5'
  return base + 'background:var(--color-surface-03);border-color:var(--color-surface-04);color:var(--color-text-muted);opacity:0.5'
}
</script>

<style scoped>
.prose-lesson :deep(p)  { margin-bottom: 0.75rem; }
.prose-lesson :deep(strong) { color: var(--color-primary-500); }
.prose-lesson :deep(blockquote) {
  border-left: 3px solid var(--color-primary-500);
  padding: 0.5rem 0.75rem;
  margin: 0.75rem 0;
  background: var(--color-surface-03);
  border-radius: 0.5rem;
}
.fade-enter-active, .fade-leave-active { transition: opacity .25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
