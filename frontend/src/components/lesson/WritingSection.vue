<template>
  <div>
    <!-- Section header -->
    <div class="flex items-center gap-2 mb-4">
      <span class="text-xl">✍️</span>
      <span class="text-base font-bold" style="color:var(--color-text-base)">Luyện viết</span>
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

    <!-- Exercise cards -->
    <div class="space-y-5">
      <div v-for="(ex, ei) in exercises" :key="ei"
           class="rounded-2xl overflow-hidden"
           style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
        <!-- Card header -->
        <div class="flex items-center justify-between px-5 py-3"
             style="background-color:var(--color-surface-03);border-bottom:1px solid var(--color-surface-04)">
          <span class="text-xs font-semibold" style="color:var(--color-text-muted)">
            Bài {{ ei + 1 }}/{{ exercises.length }}
            <span class="ml-2 px-2 py-0.5 rounded-full"
                  style="background:var(--color-surface-04);font-weight:400">
              {{ typeLabel(ex.type) }}
            </span>
          </span>
          <span v-if="results[ei] === true"
                class="text-xs font-medium text-green-400">✓ Đúng</span>
          <span v-else-if="results[ei] === false"
                class="text-xs font-medium text-red-400">✗ Sai</span>
          <span v-else-if="submitted[ei]"
                class="text-xs font-medium" style="color:#fbbf24">✓ Đã nộp</span>
        </div>

        <!-- Body -->
        <div class="px-5 py-4">
          <!-- Grammar hint -->
          <div v-if="ex.grammar_hint"
               class="mb-3 px-3 py-2 rounded-xl text-xs"
               style="background:rgba(6,182,212,0.06);color:#22d3ee;border:1px solid rgba(6,182,212,0.18)">
            💡 {{ ex.grammar_hint }}
          </div>

          <!-- Prompt -->
          <p class="font-medium text-sm mb-1" style="color:var(--color-text-base)">{{ ex.prompt }}</p>
          <p v-if="ex.prompt_vi" class="text-xs mb-4" style="color:var(--color-text-muted)">{{ ex.prompt_vi }}</p>

          <!-- ── word_order ─────────────────────────────────────────────── -->
          <template v-if="ex.type === 'word_order'">
            <WordOrderExercise
              :items="ex.items"
              :correct-answer="ex.correct_answer"
              :done="submitted[ei]"
              @submit="onWordOrder(ei, $event)"
            />
          </template>

          <!-- ── gap_fill ────────────────────────────────────────────────── -->
          <template v-else-if="ex.type === 'gap_fill'">
            <div class="grid grid-cols-1 gap-2">
              <button v-for="(opt, oi) in ex.options" :key="oi"
                      @click="selectGapFill(ei, oi)"
                      :disabled="submitted[ei]"
                      class="text-left px-4 py-2.5 rounded-xl text-sm transition"
                      :style="gapFillStyle(ei, oi, ex.correct_index)">
                <span class="font-mono mr-2 text-xs opacity-60">{{ String.fromCharCode(65 + oi) }}</span>{{ opt }}
              </button>
            </div>
            <p v-if="submitted[ei]"
               class="mt-2 text-xs px-3 py-1.5 rounded-xl"
               :style="results[ei]
                 ? 'background:rgba(34,197,94,0.1);color:#86efac'
                 : 'background:rgba(239,68,68,0.1);color:#fca5a5'">
              {{ results[ei] ? '✓ Đúng!' : `✗ Sai. Đáp án: ${ex.options[ex.correct_index]}` }}
            </p>
          </template>

          <!-- ── sentence_completion / guided / free ────────────────────── -->
          <template v-else>
            <div v-if="!submitted[ei]">
              <textarea
                v-model="textAnswers[ei]"
                :placeholder="ex.type === 'sentence_completion'
                  ? 'Hoàn thành câu...'
                  : 'Viết câu trả lời...'"
                rows="3"
                class="w-full rounded-xl px-4 py-3 text-sm outline-none resize-none transition"
                style="background:var(--color-surface-03);border:1.5px solid var(--color-surface-04);color:var(--color-text-base)"
              />
              <!-- Word count bar -->
              <div v-if="ex.min_words || ex.max_words" class="mt-2">
                <div class="flex justify-between text-xs mb-1" style="color:var(--color-text-muted)">
                  <span>{{ wordCount(textAnswers[ei]) }} từ</span>
                  <span>{{ ex.min_words }}–{{ ex.max_words }} từ</span>
                </div>
                <div class="w-full h-1.5 rounded-full overflow-hidden"
                     style="background:var(--color-surface-04)">
                  <div class="h-full rounded-full transition-all"
                       :style="wordBarStyle(ei, ex)" />
                </div>
              </div>
              <button @click="submitFreeWrite(ei, ex)"
                      :disabled="!canSubmit(ei, ex)"
                      class="mt-3 w-full py-2.5 rounded-xl text-sm font-medium transition"
                      :style="canSubmit(ei, ex)
                        ? 'background:rgba(6,182,212,0.18);color:#22d3ee;border:1px solid rgba(6,182,212,0.35);cursor:pointer'
                        : 'background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04);cursor:not-allowed;opacity:0.5'">
                Nộp bài
              </button>
            </div>
            <!-- Submitted view -->
            <div v-if="submitted[ei]">
                <div class="px-4 py-3 rounded-xl mb-3"
                     style="background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.2)">
                  <p class="text-xs font-semibold mb-1" style="color:#86efac">Bài của bạn:</p>
                  <p class="text-sm" style="color:var(--color-text-base)">{{ textAnswers[ei] }}</p>
                </div>
                <div v-if="ex.sample_answer">
                  <button v-if="!showSample[ei]"
                          @click="showSample[ei] = true"
                          class="text-xs px-3 py-1.5 rounded-lg transition hover:opacity-80"
                          style="background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)">
                    Xem bài mẫu
                  </button>
                  <div v-else
                       class="px-4 py-3 rounded-xl"
                       style="background:rgba(6,182,212,0.06);border:1px solid rgba(6,182,212,0.2)">
                    <p class="text-xs font-semibold mb-1" style="color:#22d3ee">Bài mẫu:</p>
                    <p class="text-sm" style="color:var(--color-text-base)">{{ ex.sample_answer }}</p>
                  </div>
                </div>
              </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, defineComponent, h } from 'vue'

// ── WordOrderExercise inline component ────────────────────────────────────────
const WordOrderExercise = defineComponent({
  props: {
    items: { type: Array, required: true },
    correctAnswer: { type: String, required: true },
    done: { type: Boolean, default: false },
  },
  emits: ['submit'],
  setup(props, { emit }) {
    const available = ref([...props.items].sort(() => Math.random() - 0.5))
    const chosen    = ref([])
    const checked   = ref(false)
    const correct   = ref(false)

    function pick(i) {
      if (checked.value) return
      chosen.value.push(available.value[i])
      available.value.splice(i, 1)
    }
    function remove(i) {
      if (checked.value) return
      available.value.push(chosen.value[i])
      chosen.value.splice(i, 1)
    }
    function check() {
      const normalize = s => s.toLowerCase().trim().replace(/[.!?,;]+$/, '')
      const userSentence = chosen.value.join(' ')
      const isCorrect = normalize(userSentence) === normalize(props.correctAnswer)
      correct.value  = isCorrect
      checked.value  = true
      emit('submit', { correct: isCorrect })
    }
    function reset() {
      available.value = [...props.items].sort(() => Math.random() - 0.5)
      chosen.value = []
      checked.value = false
      correct.value = false
    }

    return () => {
      const chipBase = 'display:inline-block;padding:4px 10px;border-radius:8px;font-size:13px;font-weight:500;cursor:pointer;transition:all .15s;margin:2px;border:1px solid'
      const chipAvail = chipBase + ';background:var(--color-surface-03);border-color:var(--color-surface-04);color:var(--color-text-base)'
      const chipChosen = chipBase + ';background:rgba(6,182,212,0.12);border-color:rgba(6,182,212,0.3);color:#22d3ee'
      const chipCorrect = chipBase + ';background:rgba(34,197,94,0.12);border-color:rgba(34,197,94,0.3);color:#86efac;cursor:default'
      const chipWrong = chipBase + ';background:rgba(239,68,68,0.12);border-color:rgba(239,68,68,0.3);color:#fca5a5;cursor:default'

      return h('div', [
        // Chosen tray
        h('div', {
          style: 'min-height:42px;padding:6px;border-radius:12px;margin-bottom:8px;display:flex;flex-wrap:wrap;gap:2px;background:var(--color-surface-03);border:1.5px dashed var(--color-surface-04)'
        }, [
          chosen.value.length === 0
            ? h('span', { style: 'color:var(--color-text-muted);font-size:12px;padding:4px 6px' }, 'Xếp từ vào đây...')
            : chosen.value.map((w, i) =>
                h('span', {
                  style: checked.value ? (correct.value ? chipCorrect : chipWrong) : chipChosen,
                  onClick: () => remove(i),
                }, w)
              ),
        ]),
        // Available words
        h('div', { style: 'display:flex;flex-wrap:wrap;gap:2px;margin-bottom:12px' },
          available.value.map((w, i) =>
            h('span', { style: chipAvail, onClick: () => pick(i) }, w)
          )
        ),
        // Actions
        !checked.value
          ? h('button', {
              style: chosen.value.length === props.items.length
                ? 'background:rgba(6,182,212,0.18);color:#22d3ee;border:1px solid rgba(6,182,212,0.35);padding:8px 18px;border-radius:10px;font-size:13px;cursor:pointer;font-weight:500'
                : 'background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04);padding:8px 18px;border-radius:10px;font-size:13px;cursor:not-allowed;opacity:0.5',
              disabled: chosen.value.length !== props.items.length,
              onClick: check,
            }, 'Kiểm tra')
          : h('div', { style: 'display:flex;align-items:center;gap:8px' }, [
              h('p', {
                style: correct.value
                  ? 'font-size:13px;color:#86efac'
                  : 'font-size:13px;color:#fca5a5',
              }, correct.value ? '✓ Chính xác!' : `✗ Đáp án: ${props.correctAnswer}`),
              !correct.value && h('button', {
                style: 'font-size:12px;padding:4px 10px;border-radius:8px;background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04);cursor:pointer',
                onClick: reset,
              }, 'Thử lại'),
            ]),
      ])
    }
  },
})

// ── Section component ─────────────────────────────────────────────────────────
const props = defineProps({
  content: { type: Object, required: true },
})
const emit = defineEmits(['progress'])

const exercises   = computed(() => props.content.exercises ?? [])
const textAnswers = reactive({})
const submitted   = reactive({})
const results     = reactive({})   // true (correct) | false (wrong) | undefined (open)
const showSample  = reactive({})
const gapFillSel  = reactive({})   // ei → selected option index

// ── Word order submit ─────────────────────────────────────────────────────────
function onWordOrder(ei, { correct }) {
  submitted[ei] = true
  results[ei]   = correct
  emitProgress()
}

// ── Gap fill ──────────────────────────────────────────────────────────────────
function selectGapFill(ei, oi) {
  if (submitted[ei]) return
  gapFillSel[ei] = oi
  submitted[ei]  = true
  results[ei]    = oi === exercises.value[ei].correct_index
  emitProgress()
}

function gapFillStyle(ei, oi, correctIdx) {
  const a   = gapFillSel[ei]
  const base = 'border:1px solid;'
  if (a === undefined)
    return base + 'background:var(--color-surface-03);border-color:var(--color-surface-04);color:var(--color-text-base);cursor:pointer'
  if (oi === correctIdx)
    return base + 'background:rgba(34,197,94,0.12);border-color:rgba(34,197,94,0.4);color:#86efac'
  if (oi === a)
    return base + 'background:rgba(239,68,68,0.12);border-color:rgba(239,68,68,0.4);color:#fca5a5'
  return base + 'background:var(--color-surface-03);border-color:var(--color-surface-04);color:var(--color-text-muted);opacity:0.5'
}

// ── Free write submit ─────────────────────────────────────────────────────────
function submitFreeWrite(ei, ex) {
  if (!canSubmit(ei, ex)) return
  submitted[ei] = true
  results[ei]   = undefined   // not auto-graded
  emitProgress()
}

function canSubmit(ei, ex) {
  const wc = wordCount(textAnswers[ei])
  if (!textAnswers[ei]?.trim()) return false
  if (ex.min_words && wc < ex.min_words) return false
  return true
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function wordCount(str) {
  return (str ?? '').trim().split(/\s+/).filter(w => w).length
}

function wordBarStyle(ei, ex) {
  const wc  = wordCount(textAnswers[ei])
  const min = ex.min_words ?? 0
  const max = ex.max_words ?? 100
  const pct = Math.min(100, (wc / (max || 1)) * 100)
  let color = 'rgba(6,182,212,0.7)'
  if (wc < min) color = 'rgba(251,191,36,0.7)'
  if (wc > max) color = 'rgba(239,68,68,0.7)'
  return `width:${pct}%;background:${color}`
}

function typeLabel(t) {
  const map = {
    word_order:           'Sắp xếp từ',
    gap_fill:             'Điền vào chỗ trống',
    sentence_completion:  'Hoàn thành câu',
    guided:               'Viết có hướng dẫn',
    free:                 'Viết tự do',
  }
  return map[t] ?? t
}

// ── Progress ──────────────────────────────────────────────────────────────────
const exerciseTotal   = computed(() => exercises.value.length)
const exerciseDone    = computed(() => Object.values(submitted).filter(Boolean).length)
const exerciseCorrect = computed(() =>
  Object.values(results).filter(v => v === true).length
)
const allDone = computed(() =>
  exerciseTotal.value > 0 && exerciseDone.value >= exerciseTotal.value
)

function emitProgress() {
  emit('progress', {
    done:    exerciseDone.value,
    correct: exerciseCorrect.value,
    total:   exerciseTotal.value,
  })
}

watch(() => props.content, () => emitProgress(), { immediate: true })
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity .25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
