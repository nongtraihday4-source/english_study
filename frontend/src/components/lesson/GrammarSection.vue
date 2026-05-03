<template>
  <!-- TIP mode: collapsible grammar hint card for non-grammar lessons -->
  <div v-if="mode === 'tip'">
    <div class="rounded-2xl overflow-hidden"
         style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
      <button
        class="w-full flex items-center gap-2 px-5 py-3 transition hover:opacity-80"
        style="background-color:rgba(99,102,241,0.08);border-bottom:1px solid var(--color-surface-04)"
        @click="tipOpen = !tipOpen"
      >
        <span class="text-base">💡</span>
        <span class="font-medium text-sm" style="color:#818cf8">Ngữ pháp gợi nhớ: {{ section.title }}</span>
        <span class="ml-auto text-xs" style="color:var(--color-text-muted)">{{ tipOpen ? '▲' : '▼' }}</span>
      </button>
      <Transition name="collapse">
        <div v-show="tipOpen" class="px-5 py-4">
          <div v-if="section.note"
               class="grammar-note text-sm leading-relaxed mb-3"
               style="color:var(--color-text-base)"
               v-html="renderMarkdown(section.note)"></div>
          <div v-if="section.examples?.length" class="space-y-2">
            <div v-for="(ex, ei) in section.examples" :key="ei"
                 class="rounded-xl px-3 py-2"
                 style="background:var(--color-surface-03);border:1px solid var(--color-surface-04)">
              <p class="text-sm font-medium" style="color:var(--color-text-base)"
                 v-html="highlightText(ex.en, ex.highlight)"></p>
              <p v-if="ex.vi" class="text-xs mt-0.5" style="color:var(--color-text-muted)">{{ ex.vi }}</p>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>

  <!-- FULL mode: 60/40 split — grammar explanation + exercises -->
  <div v-else>
    <div class="flex items-center gap-2 mb-4">
      <span class="text-xl">📐</span>
      <span class="text-base font-bold" style="color:#818cf8">{{ section.title }}</span>
      <span v-if="isDone"
            class="ml-auto text-xs font-medium px-2.5 py-0.5 rounded-full"
            style="background:rgba(34,197,94,0.15);color:#86efac">
        ✓ Hoàn thành
      </span>
    </div>

    <div class="flex flex-col lg:flex-row lg:gap-6 lg:items-start">

      <!-- Left 60%: Grammar explanation + examples -->
      <div class="lg:w-[60%] min-w-0 mb-4 lg:mb-0">
        <div class="rounded-2xl overflow-hidden"
             style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
          <div class="flex items-center gap-2 px-5 py-3"
               style="background-color:rgba(99,102,241,0.08);border-bottom:1px solid var(--color-surface-04)">
            <span class="font-semibold text-sm" style="color:#818cf8">📐 Ngữ pháp</span>
          </div>
          <div v-if="section.note" class="px-5 py-4">
            <div class="grammar-note text-sm leading-relaxed"
                 style="color:var(--color-text-base)"
                 v-html="renderMarkdown(section.note)"></div>
          </div>
          <div v-if="section.examples?.length" class="px-5 pb-4 space-y-2">
            <p class="text-xs font-semibold uppercase tracking-wide mb-2" style="color:var(--color-text-muted)">Ví dụ</p>
            <div v-for="(ex, ei) in section.examples" :key="ei"
                 class="rounded-xl px-4 py-3"
                 style="background:var(--color-surface-03);border:1px solid var(--color-surface-04)">
              <p class="text-sm font-medium mb-0.5" style="color:var(--color-text-base)"
                 v-html="highlightText(ex.en, ex.highlight)"></p>
              <p v-if="ex.vi" class="text-xs" style="color:var(--color-text-muted)">{{ ex.vi }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right 40%: Exercises -->
      <div class="lg:w-[40%] min-w-0 lg:sticky lg:top-20 lg:self-start">
        <div v-if="section.exercises?.length"
             class="rounded-2xl overflow-hidden"
             style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
          <div class="flex items-center justify-between px-5 py-3"
               style="background-color:var(--color-surface-03);border-bottom:1px solid var(--color-surface-04)">
            <span class="font-semibold text-sm" style="color:var(--color-text-base)">
              🧩 Bài tập ({{ section.exercises.length }} câu)
            </span>
            <span v-if="done > 0"
                  class="text-xs font-medium px-2 py-0.5 rounded-full"
                  style="background:rgba(99,102,241,0.15);color:#818cf8">
              {{ correct }}/{{ done }} đúng
            </span>
          </div>
          <div class="px-5 py-4 space-y-6">
            <div v-for="(ex, ei) in section.exercises" :key="ei">
              <div class="flex items-center gap-2 mb-2">
                <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                      :style="exerciseTypeBadge(ex.type)">
                  {{ exerciseTypeLabel(ex.type) }}
                </span>
                <span class="text-xs" style="color:var(--color-text-muted)">Câu {{ ei + 1 }}</span>
              </div>
              <p class="text-sm font-medium mb-3" style="color:var(--color-text-base)">{{ ex.prompt }}</p>

              <!-- Cloze: nested option arrays -->
              <template v-if="isCloze(ex)">
                <div class="space-y-3">
                  <div v-for="(blankOpts, bi) in ex.options" :key="bi">
                    <p class="text-xs mb-1 font-medium" style="color:var(--color-text-muted)">Chỗ trống [{{ bi + 1 }}]:</p>
                    <div class="flex flex-wrap gap-2">
                      <button
                        v-for="(opt, oi) in blankOpts" :key="oi"
                        @click="selectCloze(ei, bi, oi)"
                        :disabled="exerciseAnswers[ei] !== undefined"
                        class="text-sm px-3 py-1.5 rounded-xl transition border"
                        :style="clozeStyle(ei, bi, oi, ex.correct[bi])"
                      >{{ opt }}</button>
                    </div>
                  </div>
                </div>
              </template>

              <!-- Standard MC / gap-fill / error / rewrite -->
              <template v-else>
                <div class="grid grid-cols-1 gap-2">
                  <button
                    v-for="(opt, oi) in ex.options" :key="oi"
                    @click="selectAnswer(ei, oi)"
                    :disabled="exerciseAnswers[ei] !== undefined"
                    class="text-left px-4 py-2.5 rounded-xl text-sm transition"
                    :style="answerStyle(ei, oi, ex.correct)"
                  >
                    <span class="font-mono mr-2 text-xs opacity-60">{{ String.fromCharCode(65 + oi) }}</span>{{ opt }}
                  </button>
                </div>
              </template>

              <Transition name="fade">
                <div v-if="exerciseAnswers[ei] !== undefined"
                     class="mt-2 px-3 py-2 rounded-xl text-xs"
                     :style="isExerciseCorrect(ei, ex)
                       ? 'background:rgba(34,197,94,0.1);color:#86efac'
                       : 'background:rgba(239,68,68,0.1);color:#fca5a5'">
                  {{ isExerciseCorrect(ei, ex) ? '✓ Đúng! ' : '✗ Sai. ' }}{{ ex.explanation }}
                </div>
              </Transition>
            </div>
          </div>
        </div>

        <!-- No exercises placeholder (shouldn't appear in full mode normally) -->
        <div v-else
             class="rounded-2xl p-6 text-center"
             style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
          <p class="text-sm" style="color:var(--color-text-muted)">📐 Đọc và ghi nhớ ngữ pháp</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'

const props = defineProps({
  section:      { type: Object, required: true },
  mode:         { type: String, default: 'full' }, // 'full' | 'tip'
  sectionIndex: { type: Number, default: 0 },
})

const emit = defineEmits(['progress'])

const tipOpen       = ref(false)
const exerciseAnswers = reactive({})  // { exIdx: optionIdx | 'correct'|'wrong' }
const clozeAnswers    = reactive({})  // { exIdx: { blankIdx: optionIdx } }

// Emit initial total so parent can track from the start
watch(() => [props.section, props.mode], () => {
  const total = props.mode === 'full' ? (props.section.exercises?.length ?? 0) : 0
  emit('progress', { sectionIndex: props.sectionIndex, done: 0, correct: 0, total })
}, { immediate: true })

const done = computed(() => {
  if (props.mode !== 'full' || !props.section.exercises?.length) return 0
  return props.section.exercises.reduce((acc, ex, ei) => {
    if (isCloze(ex))
      return acc + (Object.keys(clozeAnswers[ei] ?? {}).length >= ex.options.length ? 1 : 0)
    return acc + (exerciseAnswers[ei] !== undefined ? 1 : 0)
  }, 0)
})

const correct = computed(() => {
  if (props.mode !== 'full' || !props.section.exercises?.length) return 0
  return props.section.exercises.reduce((acc, ex, ei) => {
    if (isCloze(ex))
      return acc + (Array.isArray(ex.correct) && ex.correct.every((c, bi) => clozeAnswers[ei]?.[bi] === c) ? 1 : 0)
    return acc + (exerciseAnswers[ei] === ex.correct ? 1 : 0)
  }, 0)
})

const isDone = computed(() => {
  const total = props.section.exercises?.length ?? 0
  return total === 0 || done.value >= total
})

function emitProgress() {
  const total = props.mode === 'full' ? (props.section.exercises?.length ?? 0) : 0
  emit('progress', { sectionIndex: props.sectionIndex, done: done.value, correct: correct.value, total })
}

function selectAnswer(ei, oi) {
  if (exerciseAnswers[ei] !== undefined) return
  exerciseAnswers[ei] = oi
  emitProgress()
}

function selectCloze(ei, bi, oi) {
  if (exerciseAnswers[ei] !== undefined) return
  if (!clozeAnswers[ei]) clozeAnswers[ei] = {}
  clozeAnswers[ei][bi] = oi
  const ex = props.section.exercises[ei]
  if (Object.keys(clozeAnswers[ei]).length >= ex.options.length) {
    exerciseAnswers[ei] = ex.correct.every((c, bi) => clozeAnswers[ei][bi] === c) ? 'correct' : 'wrong'
    emitProgress()
  }
}

function isCloze(ex) {
  return ex.type === 'cloze' || Array.isArray(ex.options?.[0])
}

function isExerciseCorrect(ei, ex) {
  if (isCloze(ex)) return Array.isArray(ex.correct) && ex.correct.every((c, bi) => clozeAnswers[ei]?.[bi] === c)
  return exerciseAnswers[ei] === ex.correct
}

function answerStyle(ei, oi, correctOpt) {
  const ans = exerciseAnswers[ei]
  const base = 'border:1px solid;'
  if (ans === undefined)
    return base + 'background:var(--color-surface-03);border-color:var(--color-surface-04);color:var(--color-text-base);cursor:pointer'
  if (oi === correctOpt)
    return base + 'background:rgba(34,197,94,0.12);border-color:rgba(34,197,94,0.4);color:#86efac'
  if (oi === ans)
    return base + 'background:rgba(239,68,68,0.12);border-color:rgba(239,68,68,0.4);color:#fca5a5'
  return base + 'background:var(--color-surface-03);border-color:var(--color-surface-04);color:var(--color-text-muted);opacity:0.5'
}

function clozeStyle(ei, bi, oi, correctOpt) {
  const answered = exerciseAnswers[ei] !== undefined
  const selected = clozeAnswers[ei]?.[bi] === oi
  const base = 'border:1px solid;transition:all .15s;'
  if (!answered && !selected)
    return base + 'background:var(--color-surface-03);border-color:var(--color-surface-04);color:var(--color-text-base);cursor:pointer'
  if (!answered && selected)
    return base + 'background:rgba(99,102,241,0.2);border-color:#818cf8;color:#818cf8'
  if (oi === correctOpt)
    return base + 'background:rgba(34,197,94,0.12);border-color:rgba(34,197,94,0.4);color:#86efac'
  if (selected)
    return base + 'background:rgba(239,68,68,0.12);border-color:rgba(239,68,68,0.4);color:#fca5a5'
  return base + 'background:var(--color-surface-03);border-color:var(--color-surface-04);color:var(--color-text-muted);opacity:0.4'
}

function exerciseTypeBadge(type) {
  return {
    'gap-fill': 'background:rgba(6,182,212,0.12);color:#22d3ee',
    'mc':       'background:rgba(99,102,241,0.12);color:#818cf8',
    'error':    'background:rgba(239,68,68,0.12);color:#fca5a5',
    'rewrite':  'background:rgba(251,146,60,0.12);color:#fb923c',
    'cloze':    'background:rgba(34,197,94,0.12);color:#86efac',
  }[type] || 'background:var(--color-surface-04);color:var(--color-text-muted)'
}

function exerciseTypeLabel(type) {
  return {
    'gap-fill': 'Điền vào chỗ trống',
    'mc':       'Chọn đáp án',
    'error':    'Tìm lỗi sai',
    'rewrite':  'Viết lại',
    'cloze':    'Cloze test',
  }[type] || type
}

function escapeHtml(str) {
  return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function highlightText(text, highlight) {
  if (!highlight || !text) return escapeHtml(text)
  const safe = escapeHtml(text), safeHL = escapeHtml(highlight)
  return safe.replace(new RegExp(`(${safeHL})`, 'i'), '<strong style="color:var(--color-primary-500)">$1</strong>')
}

function renderMarkdown(text) {
  if (!text) return ''
  let html = escapeHtml(text)
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/^\|(.+)\|$/gm, (line) => {
    if (/^\|[-| :]+\|$/.test(line)) return ''
    const cells = line.split('|').slice(1, -1).map(c => c.trim())
    return '<tr>' + cells.map(c => `<td>${c}</td>`).join('') + '</tr>'
  })
  if (html.includes('<tr>')) html = '<table class="grammar-table">' + html + '</table>'
  html = html.replace(/^(•.+)/gm, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>(\n)?)+/g, '<ul>$&</ul>')
  html = html.replace(/\n/g, '<br>')
  return html
}
</script>

<style scoped>
.grammar-note :deep(strong) { color: var(--color-primary-500); }
.grammar-note :deep(ul) { margin: 0.5rem 0 0.5rem 1rem; list-style: none; padding: 0; }
.grammar-note :deep(li) { margin-bottom: 0.25rem; }
.grammar-note :deep(table.grammar-table) {
  border-collapse: collapse; width: 100%; margin: 0.75rem 0; font-size: 0.8rem;
}
.grammar-note :deep(table.grammar-table td) {
  border: 1px solid var(--color-surface-04); padding: 0.35rem 0.6rem;
}
.fade-enter-active, .fade-leave-active { transition: opacity .25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.collapse-enter-active, .collapse-leave-active { transition: all .2s ease; overflow: hidden; }
.collapse-enter-from, .collapse-leave-to { max-height: 0; opacity: 0; }
.collapse-enter-to, .collapse-leave-from { max-height: 9999px; opacity: 1; }
</style>
