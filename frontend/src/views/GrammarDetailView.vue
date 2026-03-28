<template>
  <div class="p-6 max-w-3xl mx-auto">

    <!-- Breadcrumb + navigation -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-2 text-sm" style="color: var(--color-text-muted)">
        <RouterLink to="/grammar" class="transition hover:opacity-80"
                    style="color: var(--color-text-muted)">← Ngữ pháp</RouterLink>
        <span>/</span>
        <span style="color: var(--color-text-base)">{{ topic?.title || 'Đang tải...' }}</span>
      </div>
      <!-- Prev / Next -->
      <div v-if="topic" class="flex items-center gap-2">
        <RouterLink v-if="topic.prev_topic"
                    :to="{ name: 'grammar-detail', params: { slug: topic.prev_topic.slug } }"
                    class="px-3 py-1.5 rounded-lg text-xs font-medium transition hover:opacity-80"
                    style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-text-muted); text-decoration: none">
          ← {{ truncate(topic.prev_topic.title, 20) }}
        </RouterLink>
        <RouterLink v-if="topic.next_topic"
                    :to="{ name: 'grammar-detail', params: { slug: topic.next_topic.slug } }"
                    class="px-3 py-1.5 rounded-lg text-xs font-medium transition hover:opacity-80"
                    style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-text-muted); text-decoration: none">
          {{ truncate(topic.next_topic.title, 20) }} →
        </RouterLink>
      </div>
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

      <!-- ╔══════════════════════════════════════════════════════════════════╗ -->
      <!-- ║  SECTION 1: HOOK — Analogy + Description                       ║ -->
      <!-- ╚══════════════════════════════════════════════════════════════════╝ -->
      <section class="rounded-2xl p-6 mb-6"
               style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
        <div class="flex items-center gap-3 mb-4">
          <span class="text-3xl">{{ topic.icon || '📖' }}</span>
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="px-2 py-0.5 rounded text-xs font-bold"
                    :style="levelColor(topic.level)">{{ topic.level }}</span>
              <span v-if="topic.chapter" class="text-xs" style="color: var(--color-text-muted)">
                {{ topic.chapter }}
              </span>
            </div>
            <h1 class="text-2xl font-bold" style="color: var(--color-text-base)">
              {{ topic.title }}
            </h1>
          </div>
        </div>

        <p v-if="topic.description" class="text-sm mb-4 leading-relaxed" style="color: var(--color-text-muted)">
          {{ topic.description }}
        </p>

        <!-- Analogy box -->
        <div v-if="topic.analogy"
             class="rounded-xl px-4 py-3 mb-3"
             style="background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.25)">
          <p class="text-sm" style="color: var(--color-text-base)">
            💡 <strong>Gợi nhớ:</strong> {{ topic.analogy }}
          </p>
        </div>

        <!-- Memory hook -->
        <div v-if="topic.memory_hook"
             class="rounded-xl px-4 py-3"
             style="background:rgba(251,191,36,0.1); border:1px solid rgba(251,191,36,0.25)">
          <p class="text-sm" style="color: #fbbf24">
            🧠 <strong>Mẹo nhớ:</strong> {{ topic.memory_hook }}
          </p>
        </div>
      </section>

      <!-- ╔══════════════════════════════════════════════════════════════════╗ -->
      <!-- ║  SECTION 2: FORMULA — Rules with formulas + examples           ║ -->
      <!-- ╚══════════════════════════════════════════════════════════════════╝ -->
      <section v-if="topic.rules?.length" class="mb-6">
        <h2 class="font-bold text-lg mb-4 flex items-center gap-2" style="color: var(--color-text-base)">
          📋 Công thức & Quy tắc
          <span class="text-xs font-normal px-2 py-0.5 rounded-full"
                style="background: var(--color-surface-04); color: var(--color-text-muted)">
            {{ topic.rules.length }} quy tắc
          </span>
        </h2>

        <!-- Stepper-style rule cards -->
        <div class="space-y-4">
          <div v-for="(rule, ri) in topic.rules" :key="rule.id"
               class="rounded-2xl overflow-hidden"
               :style="rule.is_exception
                 ? 'background-color: var(--color-surface-02); border: 1px solid rgba(239,68,68,0.35)'
                 : 'background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)'">

            <div class="p-5">
              <!-- Step number + title -->
              <div class="flex items-start gap-3 mb-3">
                <div class="flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold flex-shrink-0"
                     :style="rule.is_exception
                       ? 'background:rgba(239,68,68,0.2); color:#f87171'
                       : 'background:rgba(99,102,241,0.15); color:#818cf8'">
                  {{ ri + 1 }}
                </div>
                <div>
                  <h3 class="font-bold text-base" style="color: var(--color-text-base)">
                    {{ rule.title }}
                    <span v-if="rule.is_exception"
                          class="ml-2 text-xs font-semibold px-2 py-0.5 rounded"
                          style="background:rgba(239,68,68,0.2); color:#f87171">⚠ Ngoại lệ</span>
                  </h3>
                </div>
              </div>

              <!-- Formula pill -->
              <div v-if="rule.formula"
                   class="inline-block px-4 py-2 rounded-xl text-sm font-mono mb-3"
                   style="background: rgba(99,102,241,0.12); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.25)">
                {{ rule.formula }}
              </div>

              <!-- Explanation -->
              <p v-if="rule.explanation" class="text-sm leading-relaxed mb-3"
                 style="color: var(--color-text-muted)">
                {{ rule.explanation }}
              </p>

              <!-- Rule memory hook -->
              <div v-if="rule.memory_hook"
                   class="text-xs px-3 py-2 rounded-xl mb-3"
                   style="background: rgba(251,191,36,0.1); border: 1px solid rgba(251,191,36,0.25); color: #fbbf24">
                🧠 {{ rule.memory_hook }}
              </div>
            </div>

            <!-- Examples -->
            <div v-if="rule.examples?.length"
                 class="border-t" style="border-color: var(--color-surface-04)">
              <div class="divide-y" style="border-color: var(--color-surface-04)">
                <div v-for="ex in rule.examples" :key="ex.id"
                     class="flex items-start gap-3 px-5 py-3">
                  <span class="flex-shrink-0 text-sm font-bold mt-0.5" style="color: #34d399">✓</span>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                      <p class="text-sm flex-1" style="color: var(--color-text-base)"
                         v-html="highlightSentence(ex.sentence, ex.highlight)"></p>
                      <!-- Audio button -->
                      <button v-if="ex.audio_url" @click.prevent="playAudio(ex.audio_url)"
                              class="flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-full transition hover:opacity-80"
                              style="background: rgba(99,102,241,0.15); color: #818cf8"
                              title="Nghe phát âm">
                        🔊
                      </button>
                    </div>
                    <p v-if="ex.translation" class="text-xs mt-0.5" style="color: var(--color-text-muted)">
                      {{ ex.translation }}
                    </p>
                    <p v-if="ex.context" class="text-xs mt-0.5 italic" style="color: #818cf8">
                      {{ ex.context }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ╔══════════════════════════════════════════════════════════════════╗ -->
      <!-- ║  SECTION 3: PRACTICE — Quiz (3 types)                         ║ -->
      <!-- ╚══════════════════════════════════════════════════════════════════╝ -->
      <section v-if="quizQuestions.length" class="mb-6">
        <h2 class="font-bold text-lg mb-4 flex items-center gap-2" style="color: var(--color-text-base)">
          🧩 Thực hành
          <span class="text-xs font-normal px-2 py-0.5 rounded-full"
                style="background: var(--color-surface-04); color: var(--color-text-muted)">
            {{ quizQuestions.length }} câu
          </span>
        </h2>

        <div class="space-y-4">
          <div v-for="(q, qi) in quizQuestions" :key="qi"
               class="rounded-2xl p-5"
               style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">

            <!-- Question type badge -->
            <div class="flex items-center gap-2 mb-3">
              <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                    :style="quizTypeBadge(q.type)">
                {{ quizTypeLabel(q.type) }}
              </span>
              <span class="text-xs" style="color: var(--color-text-muted)">
                Câu {{ qi + 1 }} / {{ quizQuestions.length }}
              </span>
            </div>

            <!-- Gap-fill question -->
            <template v-if="q.type === 'gap-fill'">
              <p class="text-sm font-medium mb-4" style="color: var(--color-text-base)"
                 v-html="q.prompt"></p>
              <div class="space-y-2">
                <button v-for="(opt, oi) in q.options" :key="oi"
                        @click="selectAnswer(qi, oi)"
                        :disabled="q.selected !== null"
                        class="w-full text-left px-4 py-3 rounded-xl text-sm transition"
                        :class="optionClass(q, oi)">
                  <span class="font-medium mr-2">{{ 'ABCD'[oi] }}.</span>{{ opt }}
                </button>
              </div>
            </template>

            <!-- Multiple choice question -->
            <template v-else-if="q.type === 'mc'">
              <p class="text-sm font-medium mb-4" style="color: var(--color-text-base)">
                {{ q.prompt }}
              </p>
              <div class="space-y-2">
                <button v-for="(opt, oi) in q.options" :key="oi"
                        @click="selectAnswer(qi, oi)"
                        :disabled="q.selected !== null"
                        class="w-full text-left px-4 py-3 rounded-xl text-sm transition"
                        :class="optionClass(q, oi)">
                  <span class="font-medium mr-2">{{ 'ABCD'[oi] }}.</span>{{ opt }}
                </button>
              </div>
            </template>

            <!-- Error correction question -->
            <template v-else-if="q.type === 'error'">
              <p class="text-sm font-medium mb-2" style="color: var(--color-text-base)">
                Tìm lỗi sai trong câu:
              </p>
              <p class="text-base font-medium mb-4 px-4 py-3 rounded-xl"
                 style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2); color: var(--color-text-base)">
                "{{ q.errorSentence }}"
              </p>
              <div class="space-y-2">
                <button v-for="(opt, oi) in q.options" :key="oi"
                        @click="selectAnswer(qi, oi)"
                        :disabled="q.selected !== null"
                        class="w-full text-left px-4 py-3 rounded-xl text-sm transition"
                        :class="optionClass(q, oi)">
                  <span class="font-medium mr-2">{{ 'ABCD'[oi] }}.</span>{{ opt }}
                </button>
              </div>
            </template>

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
        <Transition name="fade">
          <div v-if="quizDone" class="mt-5 rounded-2xl p-6 text-center"
               style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <p class="text-4xl mb-2">
              {{ quizScore === quizQuestions.length ? '🎉' : quizScore >= quizQuestions.length / 2 ? '👍' : '💪' }}
            </p>
            <p class="font-bold text-xl mb-1" style="color: var(--color-text-base)">
              {{ quizScore }} / {{ quizQuestions.length }} câu đúng
            </p>
            <p class="text-sm mb-4" style="color: var(--color-text-muted)">
              {{ quizPercent }}% — {{ quizPercent >= 80 ? 'Tuyệt vời!' : quizPercent >= 50 ? 'Khá tốt, cần ôn thêm.' : 'Cần ôn lại lý thuyết.' }}
            </p>

            <!-- Save indicator -->
            <p v-if="quizSaved" class="text-xs mb-3" style="color: #34d399">✓ Đã lưu kết quả</p>
            <p v-else-if="quizSaving" class="text-xs mb-3" style="color: var(--color-text-muted)">Đang lưu...</p>

            <div class="flex items-center justify-center gap-3">
              <button @click="resetQuiz"
                      class="px-5 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
                      style="background:linear-gradient(135deg,#4f46e5,#7c3aed); color:white">
                Làm lại
              </button>
              <RouterLink v-if="topic.next_topic"
                          :to="{ name: 'grammar-detail', params: { slug: topic.next_topic.slug } }"
                          class="px-5 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
                          style="background-color: var(--color-surface-04); color: var(--color-text-base); text-decoration: none">
                Bài tiếp →
              </RouterLink>
            </div>
          </div>
        </Transition>
      </section>

      <!-- ╔══════════════════════════════════════════════════════════════════╗ -->
      <!-- ║  SECTION 4: REAL WORLD — Practical application                 ║ -->
      <!-- ╚══════════════════════════════════════════════════════════════════╝ -->
      <section v-if="topic.real_world_use" class="mb-6">
        <div class="rounded-2xl p-5"
             style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
          <h3 class="font-semibold text-sm mb-2 flex items-center gap-2" style="color: var(--color-text-base)">
            🌍 Ứng dụng thực tế
          </h3>
          <p class="text-sm leading-relaxed" style="color: var(--color-text-muted)">{{ topic.real_world_use }}</p>
        </div>
      </section>

      <!-- ── Bottom navigation ──────────────────────────────────────── -->
      <div class="flex items-center justify-between pt-4 border-t" style="border-color: var(--color-surface-04)">
        <RouterLink v-if="topic.prev_topic"
                    :to="{ name: 'grammar-detail', params: { slug: topic.prev_topic.slug } }"
                    class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm transition hover:opacity-80"
                    style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-text-muted); text-decoration: none">
          ← {{ topic.prev_topic.title }}
        </RouterLink>
        <div v-else></div>
        <RouterLink v-if="topic.next_topic"
                    :to="{ name: 'grammar-detail', params: { slug: topic.next_topic.slug } }"
                    class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm transition hover:opacity-80"
                    style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-text-muted); text-decoration: none">
          {{ topic.next_topic.title }} →
        </RouterLink>
        <div v-else></div>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { grammarApi } from '@/api/curriculum.js'
import { useAuthStore } from '@/stores/auth.js'

const route = useRoute()
const auth = useAuthStore()
const { isLoggedIn } = storeToRefs(auth)

const topic = ref(null)
const loading = ref(false)
const error = ref('')

// ── Audio player ─────────────────────────────────────────────────────────────
let _audioEl = null
function playAudio(url) {
  if (!url) return
  if (_audioEl) { _audioEl.pause(); _audioEl = null }
  _audioEl = new Audio(url)
  _audioEl.play().catch(() => {})
}

// ── Mini quiz state ──────────────────────────────────────────────────────────
const quizQuestions = ref([])
const quizSaving = ref(false)
const quizSaved = ref(false)

const quizDone = computed(() =>
  quizQuestions.value.length > 0 &&
  quizQuestions.value.every(q => q.selected !== null)
)
const quizScore = computed(() =>
  quizQuestions.value.filter(q => q.selected === q.correct).length
)
const quizPercent = computed(() =>
  quizQuestions.value.length
    ? Math.round((quizScore.value / quizQuestions.value.length) * 100)
    : 0
)

// Auto-save when quiz is done
watch(quizDone, async (done) => {
  if (!done || !isLoggedIn.value || !topic.value) return
  quizSaving.value = true
  try {
    await grammarApi.submitQuiz(route.params.slug, {
      score: quizPercent.value,
      total_questions: quizQuestions.value.length,
      correct_answers: quizScore.value,
    })
    quizSaved.value = true
  } catch {
    // silently fail — quiz still shows results
  } finally {
    quizSaving.value = false
  }
})

function selectAnswer(qi, oi) {
  if (quizQuestions.value[qi].selected !== null) return
  quizQuestions.value[qi].selected = oi
}

function optionClass(q, oi) {
  if (q.selected === null) return 'hover:bg-white/5 border border-transparent'
  if (oi === q.correct) return 'correct-opt'
  if (oi === q.selected) return 'wrong-opt'
  return 'opacity-50'
}

function resetQuiz() {
  quizQuestions.value.forEach(q => { q.selected = null })
  quizSaved.value = false
}

// ── Quiz type helpers ────────────────────────────────────────────────────────
function quizTypeLabel(type) {
  return { 'gap-fill': 'Điền khuyết', 'mc': 'Trắc nghiệm', 'error': 'Tìm lỗi sai' }[type] || type
}
function quizTypeBadge(type) {
  return {
    'gap-fill': 'background:rgba(99,102,241,0.15);color:#818cf8',
    'mc': 'background:rgba(34,197,94,0.15);color:#86efac',
    'error': 'background:rgba(239,68,68,0.15);color:#fca5a5',
  }[type] || 'background:var(--color-surface-04);color:var(--color-text-muted)'
}

// ── Build quiz (3 types) ─────────────────────────────────────────────────────
function buildQuiz(rules) {
  const questions = []
  const allExamples = []

  for (const rule of rules) {
    if (!rule.examples) continue
    for (const ex of rule.examples) {
      if (ex.sentence && ex.highlight) {
        allExamples.push({ ...ex, ruleTitle: rule.title, formula: rule.formula })
      }
    }
  }

  // Type 1: Gap-fill — replace highlight with ___
  for (const ex of allExamples) {
    if (questions.length >= 5) break
    const blank = ex.sentence.replace(
      new RegExp(ex.highlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i'),
      '<strong style="color:#818cf8">______</strong>'
    )
    if (blank === ex.sentence) continue // highlight not found

    // Generate wrong options from other examples' highlights
    const wrongs = allExamples
      .filter(e => e.highlight !== ex.highlight)
      .map(e => e.highlight)
      .filter((v, i, a) => a.indexOf(v) === i)
      .slice(0, 3)

    if (wrongs.length < 2) continue

    const options = shuffle([ex.highlight, ...wrongs.slice(0, 3)])
    questions.push(reactive({
      type: 'gap-fill',
      prompt: blank,
      options,
      correct: options.indexOf(ex.highlight),
      explanation: ex.translation || '',
      selected: null,
    }))
  }

  // Type 2: MC — choose correct sentence for a rule
  for (const rule of rules) {
    if (questions.length >= 7) break
    if (!rule.examples || rule.examples.length < 2) continue

    const correct = rule.examples[0]
    // Find examples from OTHER rules as wrong answers
    const wrongExamples = rules
      .filter(r => r.id !== rule.id)
      .flatMap(r => (r.examples || []))
      .filter(e => e.sentence)
      .slice(0, 3)

    if (wrongExamples.length < 2) continue

    const options = shuffle([
      correct.sentence,
      ...wrongExamples.slice(0, 3).map(e => e.sentence),
    ])
    questions.push(reactive({
      type: 'mc',
      prompt: `Câu nào đúng theo quy tắc "${rule.title}"?`,
      options,
      correct: options.indexOf(correct.sentence),
      explanation: correct.translation || '',
      selected: null,
    }))
  }

  // Type 3: Error correction — swap a word to create an error
  for (const ex of allExamples) {
    if (questions.length >= 8) break
    if (!ex.highlight || ex.highlight.split(/\s+/).length < 1) continue

    // Create a wrong version by modifying the highlighted part
    const errorVersion = createErrorSentence(ex.sentence, ex.highlight)
    if (!errorVersion) continue

    const options = shuffle([
      `Lỗi ở "${ex.highlight}" — đúng phải là: "${ex.highlight}"`,
      `Câu này đúng, không có lỗi`,
      `Lỗi ở cấu trúc câu chung`,
      `Lỗi ở dấu câu`,
    ])
    // The correct answer is always the first one (before shuffle)
    const correctAnswer = `Lỗi ở "${ex.highlight}" — đúng phải là: "${ex.highlight}"`
    questions.push(reactive({
      type: 'error',
      prompt: 'Tìm lỗi sai trong câu sau:',
      errorSentence: errorVersion,
      options,
      correct: options.indexOf(correctAnswer),
      explanation: `Câu đúng: "${ex.sentence}"`,
      selected: null,
    }))
  }

  return questions.slice(0, 8) // max 8 questions
}

function createErrorSentence(sentence, highlight) {
  if (!highlight) return null
  // Simple error: change verb form
  const errorMap = {
    'is': 'are', 'are': 'is', 'was': 'were', 'were': 'was',
    'has': 'have', 'have': 'has', 'do': 'does', 'does': 'do',
    'goes': 'go', 'go': 'goes', 'plays': 'play', 'play': 'plays',
  }
  const words = highlight.split(/\s+/)
  for (let i = 0; i < words.length; i++) {
    const lower = words[i].toLowerCase()
    if (errorMap[lower]) {
      const errorWords = [...words]
      errorWords[i] = errorMap[lower]
      return sentence.replace(highlight, errorWords.join(' '))
    }
  }
  return null
}

function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

// ── Utilities ────────────────────────────────────────────────────────────────
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

function truncate(str, len) {
  if (!str) return ''
  return str.length > len ? str.slice(0, len) + '…' : str
}

// ── API ──────────────────────────────────────────────────────────────────────
async function fetchTopic() {
  loading.value = true
  error.value = ''
  quizSaved.value = false
  try {
    const res = await grammarApi.getTopic(route.params.slug)
    const d = res.data?.data ?? res.data
    if (d?.rules) {
      d.rules = d.rules.map(r => reactive({ ...r }))
    }
    topic.value = d
    quizQuestions.value = buildQuiz(d?.rules || [])
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Không thể tải chủ điểm này.'
  } finally {
    loading.value = false
  }
}

// Re-fetch when route params change (prev/next navigation)
watch(() => route.params.slug, (newSlug) => {
  if (newSlug) fetchTopic()
})

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
