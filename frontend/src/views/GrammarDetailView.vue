<template>
  <div class="p-6 max-w-3xl mx-auto">

    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 text-sm mb-6" style="color: var(--color-text-muted)">
      <RouterLink to="/grammar" class="transition hover:opacity-80"
                  style="color: var(--color-text-muted)">← Ngữ pháp</RouterLink>
      <span>/</span>
      <span style="color: var(--color-text-base)">{{ topic?.title || 'Đang tải...' }}</span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="space-y-4">
      <div class="h-24 rounded-2xl animate-pulse" style="background-color: var(--color-surface-02)"></div>
      <div v-for="i in 3" :key="i" class="h-40 rounded-2xl animate-pulse"
           style="background-color: var(--color-surface-02)"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-16" style="color: var(--color-text-muted)">
      <p class="text-4xl mb-3">⚠️</p>
      <p>{{ error }}</p>
      <button @click="fetchTopic"
              class="mt-4 px-4 py-2 rounded-lg text-sm transition hover:opacity-80"
              style="background:linear-gradient(135deg,#4f46e5,#7c3aed);color:white">Thử lại</button>
    </div>

    <template v-else-if="topic">

      <!-- ── Topic header ───────────────────────────────────────────── -->
      <div class="rounded-2xl p-6 mb-6"
           style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
        <div class="flex items-center gap-3 mb-3">
          <span class="text-3xl">{{ topic.icon || '📖' }}</span>
          <div>
            <span class="px-2 py-0.5 rounded text-xs font-bold"
                  :style="levelColor(topic.level)">{{ topic.level }}</span>
            <h1 class="text-2xl font-bold mt-1" style="color: var(--color-text-base)">
              {{ topic.title }}
            </h1>
          </div>
        </div>
        <p v-if="topic.description" class="text-sm mb-3" style="color: var(--color-text-muted)">
          {{ topic.description }}
        </p>
        <div v-if="topic.analogy"
             class="text-sm rounded-xl px-4 py-3"
             style="background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.25); color:var(--color-text-base)">
          💡 <strong>Gợi nhớ:</strong> {{ topic.analogy }}
        </div>
      </div>

      <!-- ── Rules list ─────────────────────────────────────────────── -->
      <section v-if="topic.rules?.length" class="mb-8">
        <h2 class="font-bold text-lg mb-4" style="color: var(--color-text-base)">
          📋 Quy tắc ngữ pháp
        </h2>
        <div class="space-y-4">
          <div v-for="rule in topic.rules" :key="rule.id"
               class="rounded-2xl overflow-hidden"
               :style="rule.is_exception
                 ? 'background-color: var(--color-surface-02); border: 1px solid rgba(239,68,68,0.35)'
                 : 'background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)'">

            <!-- Rule header -->
            <div class="p-5">
              <div class="flex items-start justify-between gap-3 mb-2">
                <h3 class="font-bold text-base" style="color: var(--color-text-base)">
                  {{ rule.title }}
                  <span v-if="rule.is_exception"
                        class="ml-2 text-xs font-semibold px-2 py-0.5 rounded"
                        style="background:rgba(239,68,68,0.2); color:#f87171">Ngoại lệ</span>
                </h3>
              </div>

              <!-- Formula pill -->
              <div v-if="rule.formula"
                   class="inline-block px-3 py-1 rounded-lg text-sm font-mono mb-3"
                   style="background: rgba(99,102,241,0.12); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.25)">
                {{ rule.formula }}
              </div>

              <!-- Explanation -->
              <p v-if="rule.explanation" class="text-sm leading-relaxed mb-3"
                 style="color: var(--color-text-muted)">
                {{ rule.explanation }}
              </p>

              <!-- Memory hook -->
              <div v-if="rule.memory_hook"
                   class="text-xs px-3 py-2 rounded-xl"
                   style="background: rgba(251,191,36,0.12); border: 1px solid rgba(251,191,36,0.25); color: #fbbf24">
                🧠 {{ rule.memory_hook }}
              </div>
            </div>

            <!-- Examples table -->
            <div v-if="rule.examples?.length"
                 class="border-t" style="border-color: var(--color-surface-04)">
              <div class="divide-y" style="border-color: var(--color-surface-04)">
                <div v-for="ex in rule.examples" :key="ex.id"
                     class="flex items-start gap-3 px-5 py-3">
                  <span class="flex-shrink-0 text-sm font-bold mt-0.5"
                        style="color: #34d399">✓</span>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm" style="color: var(--color-text-base)"
                       v-html="highlightSentence(ex.sentence, ex.highlight)"></p>
                    <p v-if="ex.translation" class="text-xs mt-0.5"
                       style="color: var(--color-text-muted)">{{ ex.translation }}</p>
                    <p v-if="ex.context" class="text-xs mt-0.5 italic"
                       style="color: #818cf8">{{ ex.context }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Exceptions (collapsible) -->
            <div v-if="rule.exceptions?.length"
                 class="border-t" style="border-color: rgba(239,68,68,0.25)">
              <button @click="rule._showExceptions = !rule._showExceptions"
                      class="w-full px-5 py-3 text-left text-xs font-semibold flex items-center gap-2 transition hover:bg-white/5"
                      style="color: #f87171">
                <span>⚠ {{ rule.exceptions.length }} ngoại lệ</span>
                <span>{{ rule._showExceptions ? '▲' : '▼' }}</span>
              </button>
              <div v-if="rule._showExceptions" class="px-5 pb-4 space-y-1">
                <p v-for="(exc, i) in rule.exceptions" :key="i"
                   class="text-sm" style="color: var(--color-text-muted)">
                  • {{ exc }}
                </p>
              </div>
            </div>

          </div>
        </div>
      </section>

      <!-- ── Memory hook for topic ──────────────────────────────────── -->
      <div v-if="topic.real_world_use" class="rounded-2xl p-5 mb-6"
           style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
        <h3 class="font-semibold text-sm mb-2" style="color: var(--color-text-base)">🌍 Ứng dụng thực tế</h3>
        <p class="text-sm" style="color: var(--color-text-muted)">{{ topic.real_world_use }}</p>
      </div>

      <!-- ── Practice mini-quiz ─────────────────────────────────────── -->
      <section v-if="quizQuestions.length" class="mb-8">
        <h2 class="font-bold text-lg mb-4" style="color: var(--color-text-base)">
          🧩 Thực hành nhanh
        </h2>

        <div class="space-y-4">
          <div v-for="(q, qi) in quizQuestions" :key="qi"
               class="rounded-2xl p-5"
               style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">

            <p class="text-sm font-medium mb-4" style="color: var(--color-text-base)">
              <span class="font-bold mr-2" style="color:#818cf8">{{ qi + 1 }}.</span>
              {{ q.prompt }}
            </p>

            <div class="space-y-2">
              <button
                v-for="(opt, oi) in q.options" :key="oi"
                @click="selectAnswer(qi, oi)"
                :disabled="q.selected !== null"
                class="w-full text-left px-4 py-3 rounded-xl text-sm transition"
                :class="optionClass(q, oi)"
              >
                <span class="font-medium mr-2">{{ 'ABCD'[oi] }}.</span>{{ opt }}
              </button>
            </div>

            <!-- Feedback -->
            <Transition name="fade">
              <div v-if="q.selected !== null" class="mt-3 px-4 py-2 rounded-xl text-xs"
                   :style="q.selected === q.correct
                     ? 'background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);color:#86efac'
                     : 'background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);color:#fca5a5'">
                <span v-if="q.selected === q.correct">✓ Chính xác!</span>
                <span v-else>✗ Chưa đúng. Đáp án: <strong>{{ 'ABCD'[q.correct] }}</strong></span>
                <span v-if="q.explanation"> — {{ q.explanation }}</span>
              </div>
            </Transition>

          </div>
        </div>

        <!-- Quiz score summary -->
        <div v-if="quizDone" class="mt-4 rounded-2xl p-5 text-center"
             style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
          <p class="text-3xl mb-2">
            {{ quizScore === quizQuestions.length ? '🎉' : quizScore >= quizQuestions.length / 2 ? '👍' : '💪' }}
          </p>
          <p class="font-bold text-lg" style="color: var(--color-text-base)">
            {{ quizScore }} / {{ quizQuestions.length }} câu đúng
          </p>
          <button @click="resetQuiz"
                  class="mt-3 px-5 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
                  style="background:linear-gradient(135deg,#4f46e5,#7c3aed); color:white">
            Làm lại
          </button>
        </div>
      </section>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { grammarApi } from '@/api/curriculum.js'

const route = useRoute()
const topic = ref(null)
const loading = ref(false)
const error = ref('')

// ── Mini quiz state ──────────────────────────────────────────────────────────
const quizQuestions = ref([])

const quizDone = computed(() =>
  quizQuestions.value.length > 0 &&
  quizQuestions.value.every(q => q.selected !== null)
)
const quizScore = computed(() =>
  quizQuestions.value.filter(q => q.selected === q.correct).length
)

function selectAnswer(qi, oi) {
  if (quizQuestions.value[qi].selected !== null) return
  quizQuestions.value[qi].selected = oi
}

function optionClass(q, oi) {
  if (q.selected === null) {
    return 'hover:bg-white/5 border border-transparent'
  }
  if (oi === q.correct) return 'correct-opt'
  if (oi === q.selected) return 'wrong-opt'
  return 'opacity-50'
}

function resetQuiz() {
  quizQuestions.value.forEach(q => { q.selected = null })
}

// Build client-side quiz from rule examples
function buildQuiz(rules) {
  const questions = []
  for (const rule of rules) {
    if (!rule.examples || rule.examples.length < 2) continue
    // For each example with a highlight, create a "choose correct sentence" question
    const examples = rule.examples.filter(e => e.sentence)
    if (examples.length < 2) continue

    const correctIdx = Math.floor(Math.random() * Math.min(examples.length, 4))
    const pool = examples.slice(0, 4)

    questions.push(reactive({
      prompt: `Câu nào đúng về quy tắc "${rule.title}"?`,
      options: pool.map(e => e.sentence),
      correct: correctIdx < pool.length ? correctIdx : 0,
      explanation: pool[correctIdx < pool.length ? correctIdx : 0]?.translation || '',
      selected: null,
    }))

    if (questions.length >= 5) break
  }

  // If we couldn't build from examples, generate formula-based questions
  if (questions.length === 0) {
    for (const rule of rules) {
      if (!rule.formula) continue
      questions.push(reactive({
        prompt: `Công thức nào đúng cho "${rule.title}"?`,
        options: [rule.formula, shuffleFormula(rule.formula, 1), shuffleFormula(rule.formula, 2), shuffleFormula(rule.formula, 3)],
        correct: 0,
        explanation: rule.explanation || '',
        selected: null,
      }))
      if (questions.length >= 3) break
    }
  }

  return questions
}

function shuffleFormula(formula, seed) {
  const words = formula.split(/\s+/)
  if (words.length < 2) return formula + (seed === 1 ? ' (incorrect)' : seed === 2 ? ' [wrong]' : ' ≠')
  // swap two words
  const a = seed % words.length
  const b = (seed + 1) % words.length
  const arr = [...words]
  ;[arr[a], arr[b]] = [arr[b], arr[a]]
  return arr.join(' ')
}

// ── API helpers ──────────────────────────────────────────────────────────────
function highlightSentence(sentence, highlight) {
  if (!highlight || !sentence) return sentence || ''
  const escaped = highlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return sentence.replace(
    new RegExp(`(${escaped})`, 'gi'),
    '<mark style="background:rgba(99,102,241,0.25);border-radius:3px;padding:0 2px">$1</mark>'
  )
}

function levelColor(level) {
  const map = {
    A1: 'background:#d1fae5; color:#065f46',
    A2: 'background:#dbeafe; color:#1e40af',
    B1: 'background:#ede9fe; color:#4c1d95',
    B2: 'background:#fef3c7; color:#92400e',
    C1: 'background:#fee2e2; color:#991b1b',
    C2: 'background:#fce7f3; color:#831843',
  }
  return map[level] || 'background:var(--color-surface-04); color:var(--color-text-muted)'
}

async function fetchTopic() {
  loading.value = true
  error.value = ''
  try {
    const res = await grammarApi.getTopic(route.params.slug)
    const d = res.data?.data ?? res.data
    // Attach reactive _showExceptions to each rule
    if (d?.rules) {
      d.rules = d.rules.map(r => reactive({ ...r, _showExceptions: false }))
    }
    topic.value = d
    quizQuestions.value = buildQuiz(d?.rules || [])
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Không thể tải chủ điểm này.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchTopic)
</script>

<style scoped>
.correct-opt {
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.4);
  color: #86efac;
}
.wrong-opt {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}
.fade-enter-active, .fade-leave-active { transition: opacity .25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
