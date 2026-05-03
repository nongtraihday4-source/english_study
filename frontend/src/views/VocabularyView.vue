<template>
  <div class="p-6 max-w-7xl">
    <!-- Header -->
    <h1 class="text-2xl font-bold mb-1" style="color: var(--color-text-base)">Từ vựng</h1>
    <p class="text-sm mb-6" style="color: var(--color-text-muted)">Học và ôn tập từ vựng theo chủ đề</p>

    <!-- Filter bar -->
    <div class="flex flex-col gap-3 mb-6">
      <!-- Search -->
      <input v-model="search" type="search" placeholder="Tìm kiếm từ vựng..."
             class="w-full px-4 py-2.5 rounded-xl text-sm outline-none"
             style="background-color: var(--color-surface-02); color: var(--color-text-base); border: 1px solid var(--color-surface-04)" />

      <!-- CEFR level pills -->
      <div class="flex flex-wrap gap-2">
        <button v-for="lv in LEVELS" :key="lv"
                @click="selectedLevel = lv; resetAndLoad()"
                class="px-3 py-1 rounded-full text-xs font-semibold border transition"
                :style="selectedLevel === lv
                  ? levelActiveStyle(lv)
                  : 'background-color: var(--color-surface-02); color: var(--color-text-muted); border-color: var(--color-surface-04)'">
          {{ lv === 'All' ? 'Tất cả' : lv }}
        </button>
      </div>

      <!-- Domain + POS dropdowns + count -->
      <div class="flex flex-wrap items-center gap-3">
        <select v-model="selectedDomain" @change="resetAndLoad()"
                class="px-3 py-2 rounded-xl text-sm outline-none"
                style="background-color: var(--color-surface-02); color: var(--color-text-base); border: 1px solid var(--color-surface-04)">
          <option value="">Tất cả chủ đề</option>
          <option v-for="d in DOMAINS" :key="d.value" :value="d.value">{{ d.label }}</option>
        </select>
        <select v-model="selectedPos" @change="resetAndLoad()"
                class="px-3 py-2 rounded-xl text-sm outline-none"
                style="background-color: var(--color-surface-02); color: var(--color-text-base); border: 1px solid var(--color-surface-04)">
          <option value="">Tất cả từ loại</option>
          <option v-for="p in POS_LIST" :key="p.value" :value="p.value">{{ p.label }}</option>
        </select>
        <span v-if="!loading && totalCount > 0" class="text-xs" style="color: var(--color-text-muted)">
          {{ totalCount }} từ
        </span>
      </div>
    </div>

    <!-- Skeleton (first load) -->
    <div v-if="loading && words.length === 0" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
      <div v-for="i in 12" :key="i" class="rounded-xl h-28 animate-pulse"
           style="background-color: var(--color-surface-02)"></div>
    </div>

    <!-- Word grid -->
    <div v-else-if="words.length" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
      <div v-for="word in words" :key="word.id"
           class="word-card rounded-xl p-4 cursor-pointer transition"
           @click="openWord(word)">
        <!-- Word + inline audio -->
        <div class="flex items-start justify-between gap-1">
          <p class="font-bold text-sm leading-tight" style="color: var(--color-text-base)">{{ word.word }}</p>
          <button @click.stop="playAudio(word.audio_uk_url || word.audio_us_url, word.word)"
                  class="shrink-0 mt-0.5 text-xs hover:opacity-70 transition"
                  style="color: var(--color-primary-400)" title="Phát âm">🔊</button>
        </div>
        <!-- IPA -->
        <p v-if="word.ipa_uk || word.ipa_us" class="text-xs mt-0.5" style="color: var(--color-primary-400)">
          /{{ word.ipa_uk || word.ipa_us }}/
        </p>
        <!-- POS badge -->
        <span v-if="word.part_of_speech"
              class="inline-block mt-1 px-1.5 py-0.5 rounded text-[10px] font-medium"
              style="background-color: var(--color-surface-03); color: var(--color-text-muted)">
          {{ posLabel(word.part_of_speech) }}
        </span>
        <!-- Meaning -->
        <p class="text-xs mt-1.5 line-clamp-2" style="color: var(--color-text-muted)">{{ word.meaning_vi }}</p>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="!loading" class="text-center py-16" style="color: var(--color-text-muted)">
      <p class="text-4xl mb-3">🔤</p>
      <p>Không tìm thấy từ vựng nào.</p>
    </div>

    <!-- Load more -->
    <div v-if="hasMore || (loading && words.length > 0)" class="mt-6 text-center">
      <button @click="loadMore()" :disabled="loading"
              class="px-6 py-2.5 rounded-xl text-sm font-medium transition disabled:opacity-60"
              style="background-color: var(--color-surface-02); color: var(--color-text-base); border: 1px solid var(--color-surface-04)">
        {{ loading ? 'Đang tải...' : 'Xem thêm' }}
      </button>
    </div>

    <!-- Word Detail Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="selected"
             class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4"
             style="background: rgba(0,0,0,0.65)"
             @click.self="closeModal()">
          <div class="rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto"
               style="background-color: var(--color-surface-01)">

            <!-- Modal header (sticky) -->
            <div class="px-6 pt-6 pb-4 sticky top-0 z-10"
                 style="background-color: var(--color-surface-01); border-bottom: 1px solid var(--color-surface-03)">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <h2 class="text-2xl font-bold" style="color: var(--color-text-base)">{{ selected.word }}</h2>
                  <div class="flex flex-wrap items-center gap-2 mt-0.5">
                    <span v-if="selected.ipa_uk" class="text-sm" style="color: var(--color-primary-400)">
                      UK /{{ selected.ipa_uk }}/
                    </span>
                    <span v-if="selected.ipa_us" class="text-sm" style="color: var(--color-primary-400)">
                      US /{{ selected.ipa_us }}/
                    </span>
                  </div>
                </div>
                <div class="flex items-center gap-2 shrink-0">
                  <span v-if="selected.cefr_level" class="px-2 py-0.5 rounded text-xs font-bold"
                        :style="levelBadgeStyle(selected.cefr_level)">
                    {{ selected.cefr_level }}
                  </span>
                  <button @click="closeModal()" class="text-xl hover:opacity-60 transition"
                          style="color: var(--color-text-muted)">✕</button>
                </div>
              </div>
              <!-- Audio buttons (always visible) -->
              <div class="flex gap-2 mt-3">
                <button v-if="selected.audio_uk_url" @click="playAudio(selected.audio_uk_url)"
                        class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition hover:opacity-80"
                        style="background-color: var(--color-surface-02); color: var(--color-text-base); border: 1px solid var(--color-surface-04)">
                  🔊 UK
                </button>
                <button v-if="selected.audio_us_url" @click="playAudio(selected.audio_us_url)"
                        class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition hover:opacity-80"
                        style="background-color: var(--color-surface-02); color: var(--color-text-base); border: 1px solid var(--color-surface-04)">
                  🔊 US
                </button>
                <!-- TTS button: always available as fallback or extra -->
                <button @click="tts.speak(selected.word, pronunciationStore.voice)"
                        class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition hover:opacity-80"
                        :style="tts.speaking.value && tts.speakingText.value === selected.word.toLowerCase()
                          ? 'background-color: var(--color-primary-600); color: #fff'
                          : 'background-color: var(--color-surface-02); color: var(--color-text-base); border: 1px solid var(--color-surface-04)'"
                        :title="'Phát âm TTS: ' + selected.word">
                  {{ tts.loadingText.value === selected.word.toLowerCase() ? '⏳' : '🔊' }} TTS
                </button>
              </div>
            </div>

            <!-- Modal body -->
            <div class="p-6 space-y-5">
              <!-- POS + meaning + definition -->
              <div>
                <span v-if="selected.part_of_speech"
                      class="inline-block mb-1.5 px-2 py-0.5 rounded text-xs font-medium"
                      style="background-color: var(--color-surface-03); color: var(--color-text-muted)">
                  {{ posLabel(selected.part_of_speech) }}
                </span>
                <p class="font-semibold" style="color: var(--color-text-base)">{{ selected.meaning_vi }}</p>
                <p v-if="selected.definition_en" class="text-sm mt-1 italic"
                   style="color: var(--color-text-muted)">{{ selected.definition_en }}</p>
              </div>

              <!-- Example sentences -->
              <div v-if="selected.example_en">
                <p class="text-xs font-semibold uppercase tracking-wider mb-2" style="color: var(--color-text-muted)">Ví dụ</p>
                <div class="rounded-xl p-3 text-sm" style="background-color: var(--color-surface-02)">
                  <p v-html="highlightWord(selected.example_en, selected.word)"
                     style="color: var(--color-text-base)"></p>
                  <p v-if="selected.example_vi" class="text-xs mt-1.5" style="color: var(--color-text-muted)">
                    {{ selected.example_vi }}
                  </p>
                </div>
              </div>

              <!-- Synonyms -->
              <div v-if="selected.synonyms_json?.length">
                <p class="text-xs font-semibold uppercase tracking-wider mb-2" style="color: var(--color-text-muted)">Từ đồng nghĩa</p>
                <div class="flex flex-wrap gap-1.5">
                  <span v-for="syn in selected.synonyms_json" :key="syn"
                        class="px-2.5 py-1 rounded-full text-xs font-medium"
                        style="background-color: rgba(16,185,129,0.15); color: #10b981">{{ syn }}</span>
                </div>
              </div>

              <!-- Antonyms -->
              <div v-if="selected.antonyms_json?.length">
                <p class="text-xs font-semibold uppercase tracking-wider mb-2" style="color: var(--color-text-muted)">Từ trái nghĩa</p>
                <div class="flex flex-wrap gap-1.5">
                  <span v-for="ant in selected.antonyms_json" :key="ant"
                        class="px-2.5 py-1 rounded-full text-xs font-medium"
                        style="background-color: rgba(239,68,68,0.15); color: #ef4444">{{ ant }}</span>
                </div>
              </div>

              <!-- Collocations -->
              <div v-if="selected.collocations_json?.length">
                <p class="text-xs font-semibold uppercase tracking-wider mb-2" style="color: var(--color-text-muted)">Cụm từ kết hợp</p>
                <div class="flex flex-wrap gap-1.5">
                  <span v-for="col in selected.collocations_json" :key="col"
                        class="px-2.5 py-1 rounded-full text-xs"
                        style="background-color: var(--color-surface-02); color: var(--color-text-muted)">{{ col }}</span>
                </div>
              </div>

              <!-- Flashcard section: status + deck picker -->
              <div class="mt-4">
                <!-- Loading status -->
                <div v-if="statusLoading" class="text-xs py-1" style="color: var(--color-text-muted)">Đang kiểm tra flashcard...</div>

                <!-- Already-in-deck chips -->
                <div v-else-if="wordDeckStatus.length" class="mb-3">
                  <p class="text-xs font-semibold mb-1.5" style="color: var(--color-text-muted)">📚 Đã có trong deck:</p>
                  <div class="flex flex-wrap gap-1.5">
                    <span v-for="item in wordDeckStatus" :key="item.deck_id"
                          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium"
                          style="background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3)">
                      ✓ {{ item.deck_name }}
                      <button @click.stop="removeFromDeckHandler(item)"
                              class="hover:opacity-60 transition font-bold text-sm leading-none"
                              title="Xóa khỏi deck này">✕</button>
                    </span>
                  </div>
                </div>

                <!-- Toggle deck-picker button -->
                <button @click="showDeckPicker = !showDeckPicker; loadUserDecks()"
                        class="w-full py-3 rounded-xl text-sm font-semibold transition hover:opacity-90"
                        style="background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white">
                  {{ showDeckPicker ? '✕ Đóng danh sách deck' : '+ Thêm vào deck Flashcard' }}
                </button>

                <!-- Inline deck list picker -->
                <Transition name="slide-deck">
                  <div v-if="showDeckPicker" class="mt-2 rounded-xl overflow-hidden"
                       style="border: 1px solid var(--color-surface-04)">
                    <div v-if="decksLoading" class="p-4 text-xs text-center" style="color: var(--color-text-muted)">
                      Đang tải...
                    </div>
                    <template v-else>
                      <div v-for="deck in userDecks" :key="deck.id"
                           class="deck-pick-item flex items-center justify-between px-4 py-3 cursor-pointer"
                           :style="isDeckContainingWord(deck.id)
                             ? 'background: rgba(16,185,129,0.08)'
                             : 'background-color: var(--color-surface-02)'"
                           @click="toggleDeckMembership(deck)">
                        <div class="min-w-0">
                          <p class="text-sm font-medium truncate" style="color: var(--color-text-base)">{{ deck.name }}</p>
                          <p class="text-xs" style="color: var(--color-text-muted)">{{ deck.card_count || 0 }} thẻ</p>
                        </div>
                        <span v-if="isDeckContainingWord(deck.id)"
                              class="shrink-0 text-xs font-bold px-2.5 py-1 rounded-full ml-2"
                              style="background: rgba(16,185,129,0.2); color: #10b981">✓ Đã có</span>
                        <span v-else class="shrink-0 text-xs font-medium ml-2" style="color: var(--color-primary-400)">
                          + Thêm
                        </span>
                      </div>
                      <p v-if="!userDecks.length" class="p-4 text-xs text-center" style="color: var(--color-text-muted)">
                        Chưa có deck nào. Tạo deck mới ở trang Flashcards.
                      </p>
                    </template>
                  </div>
                </Transition>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { vocabularyApi } from '@/api/vocabulary.js'
import { useTTS } from '@/composables/useTTS.js'
import { usePronunciationStore } from '@/stores/pronunciation.js'

const LEVELS = ['All', 'A1', 'A2', 'B1', 'B2', 'C1']

const DOMAINS = [
  { value: 'general',    label: 'Tổng quát' },
  { value: 'everyday',   label: 'Đời sống' },
  { value: 'business',   label: 'Kinh doanh' },
  { value: 'technology', label: 'Công nghệ' },
  { value: 'academic',   label: 'Học thuật' },
  { value: 'medical',    label: 'Y tế' },
  { value: 'health',     label: 'Sức khoẻ' },
  { value: 'travel',     label: 'Du lịch' },
  { value: 'food',       label: 'Ẩm thực' },
  { value: 'vegetables', label: 'Rau/Quả' },
  { value: 'animals',    label: 'Động vật' },
  { value: 'nature',     label: 'Thiên nhiên' },
  { value: 'art',        label: 'Nghệ thuật' },
]

const POS_LIST = [
  { value: 'noun',      label: 'Danh từ' },
  { value: 'verb',      label: 'Động từ' },
  { value: 'adjective', label: 'Tính từ' },
  { value: 'adverb',    label: 'Trạng từ' },
  { value: 'phrase',    label: 'Cụm từ' },
  { value: 'other',     label: 'Khác' },
]

const words        = ref([])
const loading      = ref(false)
const search       = ref('')
const selectedLevel  = ref('All')
const selectedDomain = ref('')
const selectedPos    = ref('')
const page         = ref(1)
const hasMore      = ref(false)
const totalCount   = ref(0)

const selected         = ref(null)
const wordDeckStatus   = ref([])   // [{ deck_id, deck_name, flashcard_id }]
const statusLoading    = ref(false)
const showDeckPicker   = ref(false)
const userDecks        = ref([])
const userDecksLoaded  = ref(false)
const decksLoading     = ref(false)

let debounceTimer = null

function buildParams() {
  const p = { page: page.value, page_size: 24 }
  if (search.value)              p.search        = search.value
  if (selectedLevel.value !== 'All') p.cefr_level = selectedLevel.value
  if (selectedDomain.value)      p.domain        = selectedDomain.value
  if (selectedPos.value)         p.part_of_speech = selectedPos.value
  return p
}

async function fetchWords(append = false) {
  loading.value = true
  try {
    const res = await vocabularyApi.listWords(buildParams())
    const d   = res.data?.data ?? res.data
    const results = d?.results || (Array.isArray(d) ? d : [])
    totalCount.value = d?.count ?? 0
    hasMore.value    = !!d?.next
    words.value = append ? [...words.value, ...results] : results
  } catch {
    if (!append) words.value = []
  } finally {
    loading.value = false
  }
}

function resetAndLoad() {
  page.value = 1
  fetchWords(false)
}

function loadMore() {
  page.value += 1
  fetchWords(true)
}

watch(search, () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { page.value = 1; fetchWords(false) }, 350)
})

onMounted(() => fetchWords(false))

// ── Modal ──────────────────────────────────────────────────────

async function openWord(word) {
  selected.value      = word
  wordDeckStatus.value = []
  showDeckPicker.value = false
  statusLoading.value = true

  // Auto-play when pronunciation mode is ON
  if (pronunciationStore.enabled) {
    const audioUrl = word.audio_uk_url || word.audio_us_url
    if (audioUrl) {
      try { new Audio(audioUrl).play() } catch { /* ignore */ }
    } else {
      tts.speak(word.word, pronunciationStore.voice)
    }
  }

  try {
    const res = await vocabularyApi.getWordFlashcardStatus(word.id)
    const d = res.data?.data ?? res.data
    wordDeckStatus.value = d?.in_decks ?? []
  } catch {
    wordDeckStatus.value = []
  } finally {
    statusLoading.value = false
  }
}

function closeModal() {
  selected.value = null
  showDeckPicker.value = false
}

async function loadUserDecks() {
  if (userDecksLoaded.value || decksLoading.value) return
  decksLoading.value = true
  try {
    const res = await vocabularyApi.getDecks()
    const d = res.data?.data ?? res.data
    userDecks.value = d?.results ?? (Array.isArray(d) ? d : [])
    userDecksLoaded.value = true
  } catch {
    userDecks.value = []
  } finally {
    decksLoading.value = false
  }
}

function isDeckContainingWord(deckId) {
  return wordDeckStatus.value.some(s => s.deck_id === deckId)
}

async function toggleDeckMembership(deck) {
  const existing = wordDeckStatus.value.find(s => s.deck_id === deck.id)
  if (existing) {
    await removeFromDeckHandler(existing)
  } else {
    try {
      const res = await vocabularyApi.addWordToDeck(selected.value.id, deck.id)
      const d = res.data?.data ?? res.data
      wordDeckStatus.value = [
        ...wordDeckStatus.value,
        { deck_id: deck.id, deck_name: deck.name, flashcard_id: d?.card_id },
      ]
    } catch { /* silent */ }
  }
}

async function removeFromDeckHandler(item) {
  if (!item?.flashcard_id) return
  try {
    await vocabularyApi.removeWordFromDeck(item.flashcard_id)
    wordDeckStatus.value = wordDeckStatus.value.filter(s => s.deck_id !== item.deck_id)
  } catch { /* silent */ }
}

const tts = useTTS()
const pronunciationStore = usePronunciationStore()
let _vocabAudio = null

function playAudio(url, word) {
  if (url) {
    if (_vocabAudio) { _vocabAudio.pause(); _vocabAudio = null }
    const audio = new Audio(url)
    _vocabAudio = audio
    audio.play().catch(() => {})
  } else if (word) {
    tts.speak(word)
  }
}

/**
 * Wrap the target word in <mark> for v-html rendering.
 * Input is from trusted backend database content only.
 */
function highlightWord(text, word) {
  if (!text || !word) return text
  const escaped = word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(
    new RegExp(`\\b${escaped}\\b`, 'gi'),
    '<mark>$&</mark>',
  )
}

function posLabel(pos) {
  return { noun: 'n.', verb: 'v.', adjective: 'adj.', adverb: 'adv.', phrase: 'phr.', other: '...' }[pos] ?? pos
}

function levelActiveStyle(lv) {
  const colors = {
    All: '#6366f1', A1: '#6366f1', A2: '#3b82f6',
    B1: '#8b5cf6', B2: '#f59e0b', C1: '#ef4444',
  }
  const c = colors[lv] ?? '#6366f1'
  return `background: ${c}; color: white; border-color: ${c}`
}

function levelBadgeStyle(lv) {
  const map = {
    A1: 'background:rgba(99,102,241,.2);color:#818cf8',
    A2: 'background:rgba(59,130,246,.2);color:#60a5fa',
    B1: 'background:rgba(139,92,246,.2);color:#a78bfa',
    B2: 'background:rgba(245,158,11,.2);color:#fbbf24',
    C1: 'background:rgba(239,68,68,.2);color:#f87171',
    C2: 'background:rgba(239,68,68,.2);color:#f87171',
  }
  return map[lv] ?? ''
}
</script>

<style scoped>
.word-card {
  background-color: var(--color-surface-02);
  border: 1px solid var(--color-surface-04);
}
.word-card:hover { border-color: #6366f1; }

.deck-pick-item { border-bottom: 1px solid var(--color-surface-03); transition: background 0.15s; }
.deck-pick-item:last-child { border-bottom: none; }
.deck-pick-item:hover { filter: brightness(1.08); }

.modal-enter-active,
.modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from,
.modal-leave-to     { opacity: 0; }
.modal-enter-active :deep(.rounded-2xl),
.modal-leave-active :deep(.rounded-2xl) { transition: transform 0.2s ease; }
.modal-enter-from   :deep(.rounded-2xl),
.modal-leave-to     :deep(.rounded-2xl) { transform: translateY(24px); }

.slide-deck-enter-active { transition: all 0.2s ease; }
.slide-deck-enter-from { opacity: 0; transform: translateY(-6px); }
.slide-deck-leave-active { transition: all 0.15s ease; }
.slide-deck-leave-to { opacity: 0; transform: translateY(-6px); }

mark { background: rgba(250,204,21,.3); color: #fde68a; border-radius: 2px; padding: 0 2px; }
</style>

