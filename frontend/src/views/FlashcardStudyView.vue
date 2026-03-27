<template>
  <div>
  <!-- Session complete screen -->
  <div v-if="sessionDone" class="flex flex-col items-center justify-center min-h-[70vh] p-6 text-center">
    <p class="text-6xl mb-4">🎉</p>
    <h2 class="text-2xl font-bold mb-2" style="color: var(--color-text-base)">Phiên học hoàn tất!</h2>
    <p class="text-sm mb-6" style="color: var(--color-text-muted)">{{ deckName }}</p>

    <!-- Stats -->
    <div class="grid grid-cols-3 gap-4 mb-8 w-full max-w-sm">
      <div class="rounded-xl p-4" style="background-color: var(--color-surface-02)">
        <p class="text-2xl font-black" style="color: var(--color-primary-400)">{{ stats.reviewed }}</p>
        <p class="text-xs mt-1" style="color: var(--color-text-muted)">Thẻ đã học</p>
      </div>
      <div class="rounded-xl p-4" style="background-color: var(--color-surface-02)">
        <p class="text-2xl font-black" style="color: #86efac">{{ stats.accuracyPct }}%</p>
        <p class="text-xs mt-1" style="color: var(--color-text-muted)">Chính xác</p>
      </div>
      <div class="rounded-xl p-4" style="background-color: var(--color-surface-02)">
        <p class="text-2xl font-black" style="color: var(--color-text-soft)">{{ stats.timeStr }}</p>
        <p class="text-xs mt-1" style="color: var(--color-text-muted)">Thời gian</p>
      </div>
    </div>

    <!-- Action buttons: quiz + back -->
    <div class="flex gap-3 mb-6">
      <button @click="router.push({ name: 'flashcard-quiz', params: { deckId } })"
              class="flex-1 px-5 py-3 rounded-xl font-semibold transition hover:opacity-80"
              style="background-color: rgba(99,102,241,0.15); color: var(--color-primary-400)">
        🧠 Kiểm tra nhanh
      </button>
      <button @click="goBackToDecks"
              class="flex-1 px-5 py-3 rounded-xl font-semibold transition hover:opacity-80"
              style="background-color: var(--color-primary-600); color: #fff">
        Quay lại Decks
      </button>
    </div>

    <!-- Studied word list toggle -->
    <div v-if="studiedWords.length > 0" class="w-full max-w-sm">
      <button @click="showWordList = !showWordList"
              class="w-full text-sm font-medium py-2 rounded-xl transition hover:opacity-80"
              style="background-color: var(--color-surface-02); color: var(--color-text-muted)">
        {{ showWordList ? '▲ Ẩn danh sách từ đã học' : '▼ Xem danh sách từ đã học (' + studiedWords.length + ')' }}
      </button>

      <Transition name="slide-history">
        <div v-if="showWordList" class="mt-3 rounded-2xl overflow-hidden"
             style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-03)">
          <div v-for="item in studiedWords" :key="item.word_id"
               class="flex items-center justify-between px-4 py-3 gap-3"
               style="border-bottom: 1px solid var(--color-surface-03)">
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-sm truncate" style="color: var(--color-text-base)">
                {{ item.word?.word }}
              </p>
              <p class="text-xs truncate" style="color: var(--color-text-muted)">
                {{ item.word?.meaning_vi }}
              </p>
            </div>
            <span class="text-lg shrink-0">
              {{ item.rating >= 5 ? '🤩' : item.rating >= 4 ? '😊' : item.rating >= 2 ? '😓' : '😵' }}
            </span>
            <button @click="removeWord(item)"
                    class="shrink-0 px-2.5 py-1 rounded-lg text-xs transition hover:opacity-80"
                    style="background-color: rgba(239,68,68,0.12); color: #fca5a5">
              Xoá
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </div>

  <!-- Study session -->
  <div v-else class="p-6 max-w-2xl mx-auto">
    <!-- Stats bar -->
    <div class="mb-5">
      <div class="flex items-center justify-between text-xs mb-2" style="color: var(--color-text-muted)">
        <div class="flex gap-4">
          <span>🆕 Mới: <b style="color: var(--color-text-soft)">{{ sessionNewCount }}</b></span>
          <span>🔄 Ôn lại: <b style="color: var(--color-text-soft)">{{ sessionReviewCount }}</b></span>
          <span>✅ Hoàn thành: <b style="color: #86efac">{{ doneCount }}/{{ totalCount }}</b></span>
        </div>
        <!-- Autoplay controls -->
        <div class="flex items-center gap-2">
          <select v-model.number="autoplayDelay"
                  class="text-xs px-2 py-0.5 rounded-lg outline-none transition"
                  style="background-color: var(--color-surface-03); color: var(--color-text-muted); border: 1px solid var(--color-surface-04)"
                  :title="'Thời gian hiển thị mỗi mặt thẻ (giây)'">
            <option :value="1">1s</option>
            <option :value="2">2s</option>
            <option :value="3">3s</option>
            <option :value="5">5s</option>
            <option :value="8">8s</option>
          </select>
          <button @click="toggleAutoplay"
                  class="flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold transition hover:opacity-80"
                  :style="isAutoplaying
                    ? 'background-color: rgba(239,68,68,0.15); color: #fca5a5'
                    : 'background-color: var(--color-surface-03); color: var(--color-text-muted)'"
                  :title="isAutoplaying ? 'Dừng autoplay' : 'Tự động lướt qua từng thẻ'">
            {{ isAutoplaying ? '⏸ Dừng' : '▶ Autoplay' }}
          </button>
          <span>{{ currentIdx + 1 }}/{{ totalCount }}</span>
        </div>
      </div>
      <!-- Progress bar -->
      <div class="w-full h-1.5 rounded-full overflow-hidden" style="background-color: var(--color-surface-04)">
        <div class="h-full rounded-full transition-all duration-300"
             style="background-color: var(--color-primary-500)"
             :style="{ width: totalCount ? (doneCount / totalCount * 100) + '%' : '0%' }"></div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="h-64 rounded-2xl animate-pulse"
         style="background-color: var(--color-surface-02)"></div>

    <!-- No cards due -->
    <div v-else-if="cards.length === 0" class="text-center py-16" style="color: var(--color-text-muted)">
      <p class="text-4xl mb-3">✨</p>
      <p class="font-semibold" style="color: var(--color-text-primary)">Không có thẻ nào cần ôn hôm nay!</p>
      <p class="text-sm mt-1">Bạn đã hoàn thành lịch học. Muốn luyện thêm?</p>
      <div class="flex flex-col sm:flex-row gap-3 justify-center mt-6">
        <button @click="loadAllCards"
                class="px-5 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
                style="background-color: var(--color-surface-03); color: var(--color-text-secondary)">
          🔁 Ôn lại tất cả từ
        </button>
        <button @click="router.push({ name: 'flashcard-quiz', params: { deckId } })"
                class="px-5 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
                style="background-color: var(--color-primary-600); color: #fff">
          🧠 Tạo quiz
        </button>
        <button @click="goBackToDecks"
                class="px-5 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
                style="background-color: var(--color-surface-02); color: var(--color-text-muted)">
          ← Decks
        </button>
      </div>
    </div>

    <!-- Card -->
    <div v-else>
      <!-- Deck name -->
      <p class="text-xs font-medium mb-3 text-center" style="color: var(--color-text-muted)">{{ deckName }}</p>

      <!-- Flip card -->
      <div class="flip-container cursor-pointer mb-5" :class="{ flipped: isFlipped }"
           @click="isFlipped = !isFlipped" style="height: 280px">
        <div class="flip-card">
          <!-- Front: content depends on card_type -->
          <div class="flip-front rounded-2xl flex flex-col items-center justify-center p-8 text-center gap-3"
               style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">

            <!-- word_to_def: show word + IPA + audio -->
            <template v-if="!currentCard.card_type || currentCard.card_type === 'word_to_def'">
              <p class="text-4xl font-black leading-tight" style="color: var(--color-text-base)">
                {{ currentCard.front_text }}
              </p>
              <p class="text-base" style="color: var(--color-primary-400)">
                {{ currentCard.word_detail?.ipa_uk || currentCard.word_detail?.ipa_us || '' }}
              </p>
              <button v-if="audioUrl" @click.stop="playAudio"
                      class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition hover:opacity-70"
                      style="background-color: var(--color-surface-03); color: var(--color-text-muted)">
                🔊 Nghe
              </button>
            </template>

            <!-- def_to_word: show definition, ask user to recall the word -->
            <template v-else-if="currentCard.card_type === 'def_to_word'">
              <p class="text-xs uppercase font-bold tracking-wider"
                 style="color: var(--color-primary-400)">Đây là từ gì?</p>
              <p class="text-xl font-semibold leading-relaxed" style="color: var(--color-text-base)">
                {{ currentCard.word_detail?.meaning_vi || currentCard.front_text }}
              </p>
              <p v-if="currentCard.word_detail?.definition_en"
                 class="text-sm italic" style="color: var(--color-text-muted)">
                "{{ currentCard.word_detail.definition_en }}"
              </p>
            </template>

            <!-- audio_to_word: big audio button, ask user to recall the word -->
            <template v-else-if="currentCard.card_type === 'audio_to_word'">
              <p class="text-xs uppercase font-bold tracking-wider"
                 style="color: var(--color-primary-400)">Nghe và đoán từ</p>
              <button @click.stop="playAudio"
                      class="flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold transition hover:opacity-80 active:scale-95"
                      style="background-color: var(--color-primary-600); color: #fff">
                🔊 Phát âm
              </button>
            </template>

            <p class="text-xs mt-2" style="color: var(--color-text-muted)">Nhấn để lật thẻ</p>
          </div>

          <!-- Back: content depends on card_type -->
          <div class="flip-back rounded-2xl flex flex-col items-center justify-center p-8 text-center gap-3"
               style="background-color: var(--color-surface-03); border: 1px solid var(--color-primary-600)">

            <!-- word_to_def back: meaning + example -->
            <template v-if="!currentCard.card_type || currentCard.card_type === 'word_to_def'">
              <p class="text-2xl font-bold" style="color: var(--color-text-base)">
                {{ currentCard.back_text }}
              </p>
              <p v-if="currentCard.word_detail?.example_en" class="text-sm italic"
                 style="color: var(--color-text-muted)">
                "{{ currentCard.word_detail.example_en }}"
              </p>
              <p v-if="currentCard.word_detail?.example_vi" class="text-xs"
                 style="color: var(--color-text-soft)">
                {{ currentCard.word_detail.example_vi }}
              </p>
            </template>

            <!-- def_to_word / audio_to_word back: word + IPA + meaning -->
            <template v-else>
              <p class="text-4xl font-black" style="color: var(--color-text-base)">
                {{ currentCard.back_text }}
              </p>
              <p class="text-base" style="color: var(--color-primary-400)">
                {{ currentCard.word_detail?.ipa_uk || currentCard.word_detail?.ipa_us || '' }}
              </p>
              <p class="text-base" style="color: var(--color-text-soft)">
                {{ currentCard.word_detail?.meaning_vi || '' }}
              </p>
              <button v-if="audioUrl" @click.stop="playAudio"
                      class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition hover:opacity-70"
                      style="background-color: var(--color-surface-02); color: var(--color-text-muted)">
                🔊 Nghe lại
              </button>
            </template>

            <img v-if="currentCard.word_detail?.image_url" :src="currentCard.word_detail.image_url"
                 class="rounded-xl mt-2 max-h-24 object-contain" alt="" />
          </div>
        </div>
      </div>

      <!-- Rating buttons — only visible after flip -->
      <Transition name="slide-up">
        <div v-if="isFlipped" class="grid grid-cols-4 gap-2">
          <button @click="stopAutoplay(); rateCard(1)"
                  class="py-3 rounded-xl text-sm font-semibold transition hover:scale-105 active:scale-95"
                  style="background-color: rgba(239,68,68,0.15); color: #fca5a5">
            <span class="block text-lg">😵</span>Quên
          </button>
          <button @click="stopAutoplay(); rateCard(2)"
                  class="py-3 rounded-xl text-sm font-semibold transition hover:scale-105 active:scale-95"
                  style="background-color: rgba(234,179,8,0.15); color: #fde68a">
            <span class="block text-lg">😓</span>Khó
          </button>
          <button @click="stopAutoplay(); rateCard(4)"
                  class="py-3 rounded-xl text-sm font-semibold transition hover:scale-105 active:scale-95"
                  style="background-color: rgba(34,197,94,0.15); color: #86efac">
            <span class="block text-lg">😊</span>Nhớ
          </button>
          <button @click="stopAutoplay(); rateCard(5)"
                  class="py-3 rounded-xl text-sm font-semibold transition hover:scale-105 active:scale-95"
                  style="background-color: rgba(99,102,241,0.15); color: var(--color-primary-400)">
            <span class="block text-lg">🤩</span>Dễ
          </button>
        </div>
      </Transition>

      <!-- Hint text when card not flipped -->
      <div v-if="!isFlipped" class="mt-3 text-center">
        <p class="text-xs" style="color: var(--color-text-muted)">
          <kbd class="px-1 py-0.5 rounded" style="background-color: var(--color-surface-03)">Space</kbd> lật
          &nbsp;·&nbsp;
          <kbd class="px-1 py-0.5 rounded" style="background-color: var(--color-surface-03)">1</kbd> Quên
          <kbd class="px-1 py-0.5 rounded ml-1" style="background-color: var(--color-surface-03)">2</kbd> Khó
          <kbd class="px-1 py-0.5 rounded ml-1" style="background-color: var(--color-surface-03)">3</kbd> Nhớ
          <kbd class="px-1 py-0.5 rounded ml-1" style="background-color: var(--color-surface-03)">4</kbd> Dễ
        </p>
        <p v-if="isAutoplaying" class="text-xs mt-1" style="color: var(--color-primary-400)">
          ▶ Autoplay đang chạy — lật thẻ sau {{ autoplayDelay }}s &nbsp;·&nbsp; nhấn <kbd class="px-1 py-0.5 rounded" style="background-color: var(--color-surface-03)">Space</kbd> để dừng
        </p>
      </div>
      <div v-else class="mt-3 text-center">
        <p class="text-xs" style="color: var(--color-text-muted)">
          <kbd class="px-1 py-0.5 rounded" style="background-color: var(--color-surface-03)">1</kbd> 😵 Quên
          &nbsp;
          <kbd class="px-1 py-0.5 rounded" style="background-color: var(--color-surface-03)">2</kbd> 😓 Khó
          &nbsp;
          <kbd class="px-1 py-0.5 rounded" style="background-color: var(--color-surface-03)">3</kbd> 😊 Nhớ
          &nbsp;
          <kbd class="px-1 py-0.5 rounded" style="background-color: var(--color-surface-03)">4</kbd> 🤩 Dễ
        </p>
        <p v-if="isAutoplaying" class="text-xs mt-1" style="color: #fbbf24">
          ⏩ Autoplay: tự động chuyển sau {{ autoplayDelay }}s
        </p>
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { vocabularyApi } from '@/api/vocabulary.js'
import { useTTS } from '@/composables/useTTS.js'

const router = useRouter()
const route = useRoute()

const deckId = route.params.deckId

// ── State ─────────────────────────────────────────────────────────────────────
const cards = ref([])
const loading = ref(false)
const currentIdx = ref(0)
const isFlipped = ref(false)
const sessionDone = ref(false)
const deckName = ref('')

// session counters
const doneCount = ref(0)
const goodCount = ref(0)   // rated 4 or 5 → "correct" for accuracy
const sessionNewCount = ref(0)
const sessionReviewCount = ref(0)
const totalCount = ref(0)

// timing
const startTime = ref(null)

// post-study word list
const studiedWords = ref([])   // { word, word_id, deck_id, rating } — deduped by word_id
const showWordList = ref(false)

// autoplay
const isAutoplaying = ref(false)
const autoplayDelay = ref(3)   // seconds per face
let autoplayTimer = null

function stopAutoplay() {
  isAutoplaying.value = false
  clearTimeout(autoplayTimer)
  autoplayTimer = null
}

function scheduleAutoplayStep() {
  clearTimeout(autoplayTimer)
  autoplayTimer = setTimeout(() => {
    if (!isAutoplaying.value || sessionDone.value || cards.value.length === 0) return
    if (!isFlipped.value) {
      // Step 1: flip to back after delay
      isFlipped.value = true
      scheduleAutoplayStep()
    } else {
      // Step 2: auto-rate as "Nhớ" (4) and move to next card
      rateCard(4)
      // rateCard resets isFlipped and advances idx; schedule next front
      if (!sessionDone.value) scheduleAutoplayStep()
    }
  }, autoplayDelay.value * 1000)
}

function toggleAutoplay() {
  if (isAutoplaying.value) {
    stopAutoplay()
  } else {
    if (sessionDone.value || cards.value.length === 0) return
    isAutoplaying.value = true
    scheduleAutoplayStep()
  }
}

// ── Computed ──────────────────────────────────────────────────────────────────
const currentCard = computed(() => cards.value[currentIdx.value] ?? {})

const audioUrl = computed(() => {
  const w = currentCard.value?.word_detail
  return w?.audio_uk_url || w?.audio_us_url || null
})

const stats = computed(() => {
  const elapsed = startTime.value ? Math.floor((Date.now() - startTime.value) / 1000) : 0
  const m = Math.floor(elapsed / 60)
  const s = elapsed % 60
  const accuracy = doneCount.value > 0
    ? Math.round((goodCount.value / doneCount.value) * 100)
    : 0
  return {
    reviewed: doneCount.value,
    accuracyPct: accuracy,
    timeStr: `${m}:${String(s).padStart(2, '0')}`,
  }
})

// ── Methods ───────────────────────────────────────────────────────────────────
const tts = useTTS()

function playAudio() {
  if (audioUrl.value) {
    new Audio(audioUrl.value).play().catch(() => {})
  } else {
    const word = currentCard.value?.word_detail?.word
    if (word) tts.speak(word)
  }
}

async function rateCard(quality) {
  const card = currentCard.value
  if (!card?.id) return

  // Optimistic SM-2 call (fire & forget — UI shouldn't block)
  vocabularyApi.updateSM2(card.id, quality).catch(() => {})

  if (quality >= 4) goodCount.value++
  doneCount.value++
  isFlipped.value = false

  // Track for post-study word list (only once per word, via word_to_def card)
  if (!card.card_type || card.card_type === 'word_to_def') {
    const wid = card.word_detail?.id
    if (wid && !studiedWords.value.find(w => w.word_id === wid)) {
      studiedWords.value.push({
        word: card.word_detail,
        word_id: wid,
        deck_id: deckId,
        rating: quality,
      })
    }
  }

  // Move to next card
  if (currentIdx.value < cards.value.length - 1) {
    currentIdx.value++
  } else {
    // Save session to backend (fire & forget — requires migration)
    const elapsed = startTime.value ? Math.floor((Date.now() - startTime.value) / 1000) : 0
    vocabularyApi.completeSession(deckId, {
      new_cards: sessionNewCount.value,
      review_cards: sessionReviewCount.value,
      total_reviewed: doneCount.value,
      correct_count: goodCount.value,
      duration_seconds: elapsed,
    }).catch(() => {})
    sessionDone.value = true
  }
}

function goBackToDecks() {
  router.push({ name: 'flashcard-decks' })
}

async function removeWord(item) {
  try {
    await vocabularyApi.removeWordFromDeck({ word_id: item.word_id, deck_id: item.deck_id })
    studiedWords.value = studiedWords.value.filter(w => w.word_id !== item.word_id)
  } catch { /* ignore */ }
}

async function loadAllCards() {
  loading.value = true
  sessionDone.value = false
  startTime.value = Date.now()
  try {
    const res = await vocabularyApi.getStudyCards(deckId, { mode: 'all' })
    const d = res.data?.data ?? res.data
    cards.value = d?.flashcards ?? []
    deckName.value = d?.name ?? deckName.value
    totalCount.value = d?.total_count ?? cards.value.length
    sessionNewCount.value = 0
    sessionReviewCount.value = d?.total_count ?? 0
  } catch {
    cards.value = []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  loading.value = true
  startTime.value = Date.now()
  try {
    const res = await vocabularyApi.getStudyCards(deckId)
    const d = res.data?.data ?? res.data
    cards.value = d?.flashcards ?? []
    deckName.value = d?.name ?? 'Flashcard Deck'
    totalCount.value = d?.total_count ?? cards.value.length
    sessionNewCount.value = d?.new_count ?? 0
    sessionReviewCount.value = d?.due_count ?? 0
    if (cards.value.length === 0) totalCount.value = 0
  } catch {
    cards.value = []
  } finally {
    loading.value = false
  }

  // ── Keyboard shortcuts ───────────────────────────────────────────────────
  function handleKey(e) {
    // Don't trigger when typing in an input / textarea
    if (e.target?.tagName === 'INPUT' || e.target?.tagName === 'TEXTAREA') return
    if (sessionDone.value || cards.value.length === 0) return

    if (e.code === 'Space') {
      e.preventDefault()
      if (isAutoplaying.value) {
        stopAutoplay()  // Space pauses autoplay
      } else {
        isFlipped.value = !isFlipped.value
      }
    } else if (isFlipped.value) {
      if (e.key === '1') { stopAutoplay(); rateCard(1) }
      else if (e.key === '2') { stopAutoplay(); rateCard(2) }
      else if (e.key === '3') { stopAutoplay(); rateCard(4) }  // map 3 → rating 4 (Nhớ)
      else if (e.key === '4') { stopAutoplay(); rateCard(5) }  // map 4 → rating 5 (Dễ)
    }
  }
  window.addEventListener('keydown', handleKey)
  onUnmounted(() => {
    window.removeEventListener('keydown', handleKey)
    stopAutoplay()
  })
})
</script>

<style scoped>
.flip-container { perspective: 1000px; }
.flip-card {
  position: relative; width: 100%; height: 100%;
  transform-style: preserve-3d;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.flipped .flip-card { transform: rotateY(180deg); }
.flip-front, .flip-back { position: absolute; inset: 0; backface-visibility: hidden; }
.flip-back { transform: rotateY(180deg); }

.slide-up-enter-active { transition: all 0.25s ease; }
.slide-up-enter-from { opacity: 0; transform: translateY(10px); }

.slide-history-enter-active { transition: max-height 0.25s ease, opacity 0.2s ease; }
.slide-history-leave-active  { transition: max-height 0.2s ease, opacity 0.15s ease; }
.slide-history-enter-from, .slide-history-leave-to { max-height: 0; opacity: 0; }
.slide-history-enter-to, .slide-history-leave-from { max-height: 600px; opacity: 1; }
</style>
