<template>
  <div class="p-6 max-w-2xl mx-auto">

    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center justify-center min-h-[60vh]">
      <div class="w-12 h-12 rounded-full border-4 animate-spin mb-4"
           style="border-color: var(--color-surface-04); border-top-color: var(--color-primary-500)"></div>
      <p class="text-sm" style="color: var(--color-text-muted)">Đang tạo bộ câu hỏi...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-20">
      <p class="text-5xl mb-3">⚠️</p>
      <p class="font-semibold mb-2" style="color: var(--color-text-base)">Không thể tải quiz</p>
      <p class="text-sm mb-5" style="color: var(--color-text-muted)">{{ error }}</p>
      <button @click="goBack"
              class="px-6 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
              style="background-color: var(--color-primary-600); color: #fff">
        Quay lại
      </button>
    </div>

    <!-- Results screen -->
    <div v-else-if="quizDone" class="flex flex-col items-center text-center pt-8">
      <p class="text-6xl mb-4">{{ scoreEmoji }}</p>
      <h2 class="text-2xl font-bold mb-1" style="color: var(--color-text-base)">
        {{ score }}/{{ questions.length }} câu đúng
      </h2>
      <p class="text-sm mb-2" style="color: var(--color-text-muted)">{{ deckLabel }}</p>
      <div class="flex gap-3 items-center mb-8">
        <span class="text-3xl font-black"
              :style="accuracyColor">{{ accuracyPct }}%</span>
        <span class="text-sm" style="color: var(--color-text-muted)">chính xác</span>
      </div>

      <!-- Review wrong answers -->
      <div v-if="wrongAnswers.length > 0" class="w-full mb-8">
        <h3 class="text-sm font-bold mb-3 text-left" style="color: var(--color-text-soft)">
          Câu trả lời sai ({{ wrongAnswers.length }})
        </h3>
        <div class="rounded-2xl overflow-hidden"
             style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-03)">
          <div v-for="q in wrongAnswers" :key="q.id"
               class="px-4 py-3"
               style="border-bottom: 1px solid var(--color-surface-03)">
            <p class="text-xs font-medium mb-0.5" style="color: var(--color-text-muted)">{{ questionTypeLabel(q.type) }}</p>
            <p class="font-semibold text-sm mb-1" style="color: var(--color-text-base)">{{ q.prompt }}</p>
            <div class="flex gap-4 text-xs">
              <span style="color: #fca5a5">✗ Em chọn: {{ q.selectedText }}</span>
              <span style="color: #86efac">✓ Đúng: {{ q.correctText }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="flex gap-3 w-full max-w-sm">
        <button v-if="wrongAnswers.length > 0" @click="retryWrong"
                class="flex-1 py-3 rounded-xl text-sm font-semibold transition hover:opacity-80"
                style="background-color: rgba(239,68,68,0.15); color: #fca5a5">
          🔁 Học lại từ sai
        </button>
        <button @click="goBack"
                class="flex-1 py-3 rounded-xl text-sm font-semibold transition hover:opacity-80"
                style="background-color: var(--color-primary-600); color: #fff">
          Quay lại Decks
        </button>
      </div>
    </div>

    <!-- Quiz in progress -->
    <div v-else-if="questions.length > 0">
      <!-- Header + progress -->
      <div class="mb-5">
        <div class="flex items-center justify-between text-xs mb-2" style="color: var(--color-text-muted)">
          <p class="font-medium truncate" style="color: var(--color-text-soft)">{{ deckLabel }}</p>
          <span>{{ currentIdx + 1 }}/{{ questions.length }}</span>
        </div>
        <div class="w-full h-1.5 rounded-full overflow-hidden"
             style="background-color: var(--color-surface-04)">
          <div class="h-full rounded-full transition-all duration-300"
               style="background-color: var(--color-primary-500)"
               :style="{ width: ((currentIdx + (answered ? 1 : 0)) / questions.length * 100) + '%' }"></div>
        </div>
      </div>

      <!-- Question card -->
      <div class="rounded-2xl p-6 mb-5 text-center"
           style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-03)">
        <p class="text-xs uppercase font-bold tracking-wider mb-4"
           style="color: var(--color-primary-400)">{{ questionTypeLabel(currentQuestion.type) }}</p>

        <!-- Audio prompt -->
        <template v-if="currentQuestion.type === 'audio_to_word'">
          <button @click="playPromptAudio"
                  class="flex items-center gap-2 mx-auto px-6 py-3 rounded-xl text-sm font-semibold transition hover:opacity-80 active:scale-95"
                  style="background-color: var(--color-primary-600); color: #fff">
            🔊 Nghe câu hỏi
          </button>
          <p class="text-xs mt-2" style="color: var(--color-text-muted)">Từ nào tương ứng với âm thanh này?</p>
        </template>

        <!-- Text prompt -->
        <template v-else>
          <p class="text-2xl font-bold leading-snug" style="color: var(--color-text-base)">
            {{ currentQuestion.prompt }}
          </p>
          <p v-if="currentQuestion.ipa" class="text-sm mt-1" style="color: var(--color-primary-400)">
            {{ currentQuestion.ipa }}
          </p>
        </template>
      </div>

      <!-- Choices -->
      <div class="grid grid-cols-1 gap-3">
        <button
          v-for="choice in currentQuestion.choices"
          :key="choice.id"
          :disabled="answered"
          @click="selectChoice(choice)"
          class="w-full px-5 py-4 rounded-xl text-sm font-semibold text-left transition"
          :style="choiceStyle(choice.id)">
          {{ choice.text }}
        </button>
      </div>

      <!-- Feedback + Next -->
      <Transition name="slide-up">
        <div v-if="answered" class="mt-5">
          <p class="text-center text-sm font-semibold mb-4"
             :style="selectedChoiceId === currentQuestion.correct_id ? 'color: #86efac' : 'color: #fca5a5'">
            {{ selectedChoiceId === currentQuestion.correct_id ? '✓ Chính xác!' : '✗ Chưa đúng' }}
          </p>
          <button @click="nextQuestion"
                  class="w-full py-3 rounded-xl text-sm font-semibold transition hover:opacity-80"
                  style="background-color: var(--color-primary-600); color: #fff">
            {{ currentIdx < questions.length - 1 ? 'Câu tiếp theo →' : 'Xem kết quả 🎯' }}
          </button>
        </div>
      </Transition>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { vocabularyApi } from '@/api/vocabulary.js'

const router = useRouter()
const route = useRoute()

// ── State ─────────────────────────────────────────────────────────────────────
const loading = ref(false)
const error = ref('')
const questions = ref([])
const deckLabel = ref('')

const currentIdx = ref(0)
const answered = ref(false)
const selectedChoiceId = ref(null)
const score = ref(0)
const quizDone = ref(false)

// Track wrong answers for review
const wrongAnswers = ref([])

// ── Computed ──────────────────────────────────────────────────────────────────
const currentQuestion = computed(() => questions.value[currentIdx.value] ?? {})

const accuracyPct = computed(() =>
  questions.value.length
    ? Math.round((score.value / questions.value.length) * 100)
    : 0
)

const scoreEmoji = computed(() => {
  const p = accuracyPct.value
  if (p === 100) return '🏆'
  if (p >= 80) return '🎉'
  if (p >= 60) return '😊'
  if (p >= 40) return '😓'
  return '😵'
})

const accuracyColor = computed(() => {
  const p = accuracyPct.value
  if (p >= 80) return 'color: #86efac'
  if (p >= 60) return 'color: #93c5fd'
  if (p >= 40) return 'color: #fcd34d'
  return 'color: #fca5a5'
})

// ── Helpers ───────────────────────────────────────────────────────────────────
function questionTypeLabel(type) {
  const map = {
    word_to_meaning: 'Từ → Nghĩa',
    meaning_to_word: 'Nghĩa → Từ',
    audio_to_word: 'Âm thanh → Từ',
  }
  return map[type] || 'Câu hỏi'
}

function choiceStyle(choiceId) {
  const base = 'border: 1px solid '
  if (!answered.value) {
    return base + 'var(--color-surface-04); background-color: var(--color-surface-02); color: var(--color-text-base); cursor: pointer;'
  }
  if (choiceId === currentQuestion.value.correct_id) {
    return 'background-color: rgba(34,197,94,0.15); border: 1px solid #22c55e44; color: #86efac; cursor: default;'
  }
  if (choiceId === selectedChoiceId.value) {
    return 'background-color: rgba(239,68,68,0.15); border: 1px solid #ef444444; color: #fca5a5; cursor: default;'
  }
  return base + 'var(--color-surface-03); background-color: var(--color-surface-02); color: var(--color-text-muted); cursor: default; opacity: 0.5;'
}

function playPromptAudio() {
  const url = currentQuestion.value?.audio_url
  if (url) new Audio(url).play().catch(() => {})
}

// ── Actions ───────────────────────────────────────────────────────────────────
function selectChoice(choice) {
  if (answered.value) return
  selectedChoiceId.value = choice.id
  answered.value = true

  const correct = choice.id === currentQuestion.value.correct_id
  if (correct) {
    score.value++
  } else {
    // Record wrong answer for review
    const correctChoice = currentQuestion.value.choices.find(
      c => c.id === currentQuestion.value.correct_id
    )
    wrongAnswers.value.push({
      id: currentQuestion.value.id,
      type: currentQuestion.value.type,
      prompt: currentQuestion.value.prompt || '🔊',
      selectedText: choice.text,
      correctText: correctChoice?.text ?? '',
    })
  }
}

function nextQuestion() {
  if (currentIdx.value < questions.value.length - 1) {
    currentIdx.value++
    answered.value = false
    selectedChoiceId.value = null
  } else {
    quizDone.value = true
  }
}

function retryWrong() {
  // Build a mini-quiz with only wrong questions
  const wrongIds = new Set(wrongAnswers.value.map(w => w.id))
  questions.value = questions.value.filter(q => wrongIds.has(q.id))
  currentIdx.value = 0
  answered.value = false
  selectedChoiceId.value = null
  score.value = 0
  wrongAnswers.value = []
  quizDone.value = false
}

function goBack() {
  router.push({ name: 'flashcard-decks' })
}

// ── Load quiz ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const deckId = route.params.deckId       // single-deck path
    const deckQuery = route.query.decks      // multi-deck path (?decks=1,2,3)
    const count = parseInt(route.query.count) || 10

    let res
    if (deckId) {
      // Single-deck quiz
      const types = route.query.types || 'word_to_meaning,meaning_to_word'
      const source = route.query.source || 'all'
      res = await vocabularyApi.getDeckQuiz(deckId, { count, types, source })
      const d = res.data?.data ?? res.data
      questions.value = d?.questions ?? []
      deckLabel.value = d?.deck_name ?? 'Quiz'
    } else if (deckQuery) {
      // Multi-deck quiz
      const deckIds = deckQuery.split(',').map(Number).filter(Boolean)
      const types = route.query.types
        ? route.query.types.split(',')
        : ['word_to_meaning', 'meaning_to_word']
      res = await vocabularyApi.generateQuiz({ deck_ids: deckIds, count, types })
      const d = res.data?.data ?? res.data
      questions.value = d?.questions ?? []
      const names = d?.deck_names ?? []
      deckLabel.value = names.length ? names.join(', ') : 'Quiz tổng hợp'
    } else {
      error.value = 'Không tìm thấy deck để kiểm tra.'
    }

    if (questions.value.length === 0 && !error.value) {
      error.value = 'Deck này chưa có đủ từ để tạo bộ câu hỏi.'
    }
  } catch (e) {
    error.value = e?.response?.data?.error || 'Đã xảy ra lỗi khi tải quiz.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.slide-up-enter-active { transition: all 0.25s ease; }
.slide-up-enter-from { opacity: 0; transform: translateY(10px); }
</style>
