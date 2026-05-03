<template>
  <div class="p-4 md:p-6 max-w-4xl mx-auto">
    <div class="flex items-center justify-between mb-4">
      <button
        class="rounded-xl px-3 py-2 text-sm font-medium transition hover:opacity-80"
        style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-text-muted)"
        @click="goBack"
      >
        ← Quay lại 4 giai đoạn
      </button>
      <span
        v-if="lesson?.is_completed"
        class="text-xs px-2 py-1 rounded-full font-semibold"
        style="background-color: rgba(34,197,94,0.15); color: #86efac; border: 1px solid rgba(34,197,94,0.35)"
      >
        Đã hoàn thành
      </span>
    </div>

    <div v-if="loading" class="space-y-4">
      <div class="h-24 rounded-2xl animate-pulse" style="background-color: var(--color-surface-02)" />
      <div v-for="i in 4" :key="i" class="h-40 rounded-2xl animate-pulse" style="background-color: var(--color-surface-02)" />
    </div>

    <div
      v-else-if="error"
      class="text-center py-16 rounded-2xl"
      style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
    >
      <p class="text-4xl mb-3">⚠️</p>
      <p style="color: #fca5a5">{{ error }}</p>
      <button
        class="mt-4 px-4 py-2 rounded-xl text-sm font-semibold transition hover:opacity-80"
        style="background-color: var(--color-primary-600); color: #fff"
        @click="fetchLesson"
      >
        Thử lại
      </button>
    </div>

    <template v-else-if="lesson">
      <section
        class="rounded-3xl p-5 mb-5"
        style="background: linear-gradient(145deg, color-mix(in srgb, var(--color-primary-600) 20%, transparent), color-mix(in srgb, var(--color-surface-02) 85%, transparent)); border: 1px solid var(--color-surface-04)"
      >
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="text-xs mb-1" style="color: var(--color-text-muted)">Bài học phát âm</p>
            <h1 class="text-xl md:text-2xl font-bold" style="color: var(--color-text-base)">{{ lesson.title }}</h1>
            <p v-if="lesson.description" class="mt-2 text-sm" style="color: var(--color-text-soft)">{{ lesson.description }}</p>
          </div>
          <span class="text-xs px-2 py-1 rounded-full font-semibold" style="background-color: var(--color-surface-02); border:1px solid var(--color-surface-04); color: var(--color-primary-400)">
            {{ lesson.cefr_level }}
          </span>
        </div>

        <div v-if="lesson.phonemes?.length" class="mt-4 flex flex-wrap gap-2">
          <button
            v-for="ph in lesson.phonemes"
            :key="ph.id"
            class="rounded-xl px-3 py-1.5 text-sm font-semibold transition hover:opacity-80"
            style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-primary-400)"
            @click="ph.audio_url ? playAudio(ph.audio_url) : tts.speak(ph.example_words?.[0]?.word || bare(ph.symbol), pronunciationStore.voice)"
          >
            {{ bare(ph.symbol) }}
          </button>
        </div>
      </section>

      <section
        v-for="section in displaySections"
        :key="section.id"
        class="rounded-2xl p-5 mb-4"
        :style="sectionCardStyle(section.section_type)"
      >
        <h2 class="text-lg font-bold mb-2" style="color: var(--color-text-base)">
          {{ sectionIcon(section.section_type) }} {{ section.title }}
        </h2>
        <p v-if="section.body" class="text-sm leading-relaxed mb-4 whitespace-pre-line" style="color: var(--color-text-muted)">
          {{ section.body }}
        </p>

        <div v-if="section.section_type === 'examples'" class="grid md:grid-cols-2 gap-3">
          <div
            v-for="(item, idx) in section.items || []"
            :key="idx"
            class="rounded-xl p-3"
            style="background-color: var(--color-surface-01); border: 1px solid var(--color-surface-04)"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-semibold" style="color: var(--color-text-base)">{{ item.word || item.phrase || item.connected_form }}</p>
                <p v-if="item.ipa" class="text-xs" style="color: var(--color-primary-400)">{{ item.ipa }}</p>
              </div>
              <button
                class="rounded-lg px-2 py-1 text-xs font-semibold hover:opacity-80 transition"
                style="background-color: var(--color-primary-600); color: #fff"
                @click="tts.speak(item.word || item.phrase || item.connected_form, pronunciationStore.voice)"
              >
                🔊 Phát
              </button>
            </div>
            <p v-if="item.meaning" class="text-xs mt-1" style="color: var(--color-text-muted)">{{ item.meaning }}</p>
            <p v-if="item.sentence" class="text-xs mt-2" style="color: var(--color-text-soft)">{{ item.sentence }}</p>
            <p v-if="item.connected_form" class="text-xs mt-2" style="color: var(--color-primary-400)">Dạng nối: {{ item.connected_form }}</p>
            <p v-if="item.explanation" class="text-xs mt-1" style="color: var(--color-text-muted)">{{ item.explanation }}</p>
          </div>
        </div>

        <div v-if="section.section_type === 'practice'" class="space-y-2">
          <div
            v-for="(item, idx) in section.items || []"
            :key="idx"
            class="rounded-xl px-3 py-2 flex items-center justify-between gap-3"
            style="background-color: var(--color-surface-01); border: 1px solid var(--color-surface-04)"
          >
            <div>
              <p class="text-sm font-medium" style="color: var(--color-text-base)">{{ item.text }}</p>
              <p v-if="item.hint" class="text-xs" style="color: var(--color-text-muted)">{{ item.hint }}</p>
            </div>
            <button
              class="rounded-lg px-2 py-1 text-xs font-semibold hover:opacity-80 transition"
              style="background-color: var(--color-primary-600); color: #fff"
              @click="tts.speak(item.text, pronunciationStore.voice)"
            >
              🔊
            </button>
          </div>
        </div>

        <div v-if="section.section_type === 'quiz'" class="space-y-4">
          <div
            v-for="(q, qi) in quizQuestions"
            :key="qi"
            class="rounded-xl p-4"
            style="background-color: var(--color-surface-01); border: 1px solid var(--color-surface-04)"
          >
            <div class="flex items-center justify-between gap-3 mb-3">
              <p class="text-sm font-semibold" style="color: var(--color-text-base)">
                Câu {{ qi + 1 }}. {{ q.question || 'Nghe và chọn đáp án đúng' }}
              </p>
              <button
                class="rounded-lg px-2 py-1 text-xs font-semibold hover:opacity-80 transition"
                style="background-color: var(--color-primary-600); color: #fff"
                @click="tts.speak(q.audio_text || q.answer, pronunciationStore.voice)"
              >
                🎧 Nghe
              </button>
            </div>

            <div class="grid md:grid-cols-2 gap-2">
              <button
                v-for="(opt, oi) in q.options"
                :key="oi"
                class="rounded-xl px-3 py-2 text-left text-sm transition"
                :style="optionStyle(q, opt)"
                :disabled="q.selected !== null"
                @click="selectOption(qi, opt)"
              >
                {{ opt }}
              </button>
            </div>

            <p v-if="q.selected !== null" class="text-xs mt-3" :style="q.selected === q.answer ? 'color:#86efac' : 'color:#fca5a5'">
              {{ q.selected === q.answer ? 'Chính xác' : `Chưa đúng. Đáp án: ${q.answer}` }}
            </p>
          </div>

          <div class="rounded-xl p-4" style="background-color: var(--color-surface-01); border: 1px solid var(--color-surface-04)">
            <p class="text-sm" style="color: var(--color-text-muted)">
              Điểm hiện tại: <strong style="color: var(--color-text-base)">{{ quizScore }}</strong> / {{ quizQuestions.length }}
              ({{ quizPercent }}%)
            </p>
            <div class="mt-3 flex gap-2 items-center">
              <span
                v-if="savingCompletion"
                class="text-xs px-3 py-2 rounded-xl font-semibold"
                style="background-color: var(--color-surface-03); color: var(--color-text-muted)"
              >
                ⏳ Đang lưu kết quả...
              </span>
              <span
                v-else-if="lesson?.is_completed && quizDone"
                class="text-xs px-3 py-2 rounded-xl font-semibold"
                style="background-color: rgba(34,197,94,0.15); color: #86efac; border: 1px solid rgba(34,197,94,0.35)"
              >
                ✅ Đã hoàn thành!
              </span>
              <button
                v-else-if="quizDone && quizPercent < 70"
                class="px-4 py-2 rounded-xl text-sm font-semibold transition hover:opacity-80"
                style="background-color: var(--color-surface-03); color: var(--color-text-muted)"
                @click="resetQuiz"
              >
                Làm lại quiz
              </button>
              <button
                v-if="quizDone"
                class="px-4 py-2 rounded-xl text-sm font-semibold transition hover:opacity-80"
                style="background-color: var(--color-surface-03); color: var(--color-text-muted)"
                @click="resetQuiz"
              >
                {{ quizPercent < 70 ? 'Làm lại quiz' : '🔄 Làm lại' }}
              </button>
            </div>
            <p v-if="quizDone && !lesson?.is_completed" class="text-xs mt-2" :style="quizPercent >= 70 ? 'color:#86efac' : 'color:#fbbf24'">
              {{ quizPercent >= 70 ? '🎉 Đạt yêu cầu! Đang lưu kết quả...' : `Cần tối thiểu 70% để hoàn thành. Bạn đạt ${quizPercent}% — hãy thử lại!` }}
            </p>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { pronunciationApi } from '@/api/pronunciation.js'
import { usePronunciationStore } from '@/stores/pronunciation.js'
import { useTTS } from '@/composables/useTTS.js'

const route = useRoute()
const router = useRouter()
const tts = useTTS()
const pronunciationStore = usePronunciationStore()

const lesson = ref(null)
const loading = ref(false)
const error = ref('')
const quizQuestions = ref([])
const savingCompletion = ref(false)

function bare(sym) {
  return (sym || '').replace(/^\//, '').replace(/\/$/, '')
}

function sectionIcon(type) {
  if (type === 'explanation') return '📘'
  if (type === 'tip') return '💡'
  if (type === 'examples') return '🧩'
  if (type === 'common_mistakes') return '⚠️'
  if (type === 'practice') return '🎙️'
  if (type === 'quiz') return '✅'
  return '•'
}

function sectionCardStyle(type) {
  if (type === 'tip') {
    return 'background-color: color-mix(in srgb, #f59e0b 10%, var(--color-surface-02)); border: 1px solid rgba(245,158,11,0.4)'
  }
  if (type === 'common_mistakes') {
    return 'background-color: color-mix(in srgb, #ef4444 10%, var(--color-surface-02)); border: 1px solid rgba(239,68,68,0.35)'
  }
  if (type === 'quiz') {
    return 'background-color: color-mix(in srgb, #22c55e 8%, var(--color-surface-02)); border: 1px solid rgba(34,197,94,0.28)'
  }
  return 'background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)'
}

function optionStyle(question, option) {
  if (question.selected === null) {
    return 'background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-text-base)'
  }
  if (option === question.answer) {
    return 'background-color: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.35); color: #86efac'
  }
  if (option === question.selected && question.selected !== question.answer) {
    return 'background-color: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.35); color: #fca5a5'
  }
  return 'background-color: var(--color-surface-03); border: 1px solid var(--color-surface-04); color: var(--color-text-muted)'
}

const displaySections = computed(() => {
  const sections = lesson.value?.sections || []
  return [...sections].sort((a, b) => (a.order || 0) - (b.order || 0))
})

const quizDone = computed(() => {
  return quizQuestions.value.length > 0 && quizQuestions.value.every((q) => q.selected !== null)
})

const quizScore = computed(() => {
  return quizQuestions.value.reduce((sum, q) => sum + (q.selected === q.answer ? 1 : 0), 0)
})

const quizPercent = computed(() => {
  if (!quizQuestions.value.length) return 0
  return Math.round((quizScore.value / quizQuestions.value.length) * 100)
})

function buildQuizQuestions() {
  const quizSection = displaySections.value.find((s) => s.section_type === 'quiz')
  const items = Array.isArray(quizSection?.items) ? quizSection.items : []
  quizQuestions.value = items.map((it) => ({
    question: it.question || 'Nghe và chọn đáp án đúng',
    audio_text: it.audio_text || it.answer || '',
    options: Array.isArray(it.options) ? it.options : [],
    answer: it.answer || '',
    selected: null,
  }))
}

function selectOption(qi, option) {
  if (quizQuestions.value[qi].selected !== null) return
  quizQuestions.value[qi].selected = option
}

// Auto-complete: tự động gọi completeLesson ngay khi quiz đạt >= 70%
watch(quizDone, (done) => {
  if (done && quizPercent.value >= 70 && !lesson.value?.is_completed) {
    submitCompletion()
  }
})

function resetQuiz() {
  quizQuestions.value = quizQuestions.value.map((q) => ({ ...q, selected: null }))
}

async function fetchLesson() {
  loading.value = true
  error.value = ''
  try {
    const res = await pronunciationApi.getLessonBySlug(route.params.slug)
    const data = res.data?.data ?? res.data
    lesson.value = data
    buildQuizQuestions()
  } catch {
    error.value = 'Không thể tải chi tiết bài học. Vui lòng thử lại.'
  } finally {
    loading.value = false
  }
}

let _lessonAudio = null
function playAudio(url) {
  if (!url) return
  if (_lessonAudio) {
    _lessonAudio.pause()
    _lessonAudio = null
  }
  const a = new Audio(url)
  _lessonAudio = a
  a.play().catch(() => {})
}

async function submitCompletion() {
  if (!lesson.value?.id || !quizDone.value) return
  savingCompletion.value = true
  try {
    await pronunciationApi.completeLesson(lesson.value.id, quizPercent.value)
    lesson.value = {
      ...lesson.value,
      is_completed: quizPercent.value >= 70,
      progress_score: quizPercent.value,
    }
  } catch {
    // Silent: keeping UI responsive even if save fails.
  } finally {
    savingCompletion.value = false
  }
}

function goBack() {
  router.push({ name: 'pronunciation', query: { tab: 'stages' } })
}

onMounted(fetchLesson)
</script>
