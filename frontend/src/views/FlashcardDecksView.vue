<template>
  <div class="p-6 max-w-7xl">
    <!-- Header -->
    <div class="flex items-center justify-between mb-1">
      <div>
        <h1 class="text-2xl font-bold" style="color: var(--color-text-base)">Flashcards</h1>
        <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">
          Ôn tập từ vựng theo phương pháp Spaced Repetition (SM-2)
        </p>
      </div>
      <!-- Header action buttons -->
      <div class="flex items-center gap-2">
        <!-- Notification hour picker -->
        <div class="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm"
             style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
          <span title="Giờ nhận thông báo ôn lại">🔔</span>
          <select v-model="notifyHour" @change="saveNotifyHour"
                  class="outline-none text-xs bg-transparent"
                  style="color: var(--color-text-base)">
            <option v-for="h in 24" :key="h - 1" :value="h - 1">
              {{ String(h - 1).padStart(2, '0') }}:00
            </option>
          </select>
        </div>

        <!-- Multi-select mode toggle -->
        <button @click="toggleSelectMode"
                class="px-4 py-2 rounded-xl text-sm font-semibold transition hover:opacity-80"
                :style="selectMode
                  ? 'background-color: var(--color-primary-600)33; color: var(--color-primary-400); border: 1px solid var(--color-primary-600)55'
                  : 'background-color: var(--color-surface-02); color: var(--color-text-muted); border: 1px solid var(--color-surface-04)'">
          {{ selectMode ? `Đã chọn ${selectedDeckIds.size}` : 'Chọn deck' }}
        </button>

        <button @click="showCreateModal = true"
                class="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold transition hover:opacity-80"
                style="background-color: var(--color-primary-600); color: #fff">
          + Tạo deck mới
        </button>
      </div>
    </div>

    <!-- Multi-deck quiz bar (shown when decks are selected) -->
    <Transition name="slide-up">
      <div v-if="selectMode && selectedDeckIds.size > 0"
           class="flex items-center justify-between gap-3 mt-4 px-5 py-3 rounded-2xl"
           style="background-color: var(--color-surface-02); border: 1px solid var(--color-primary-600)44">
        <p class="text-sm" style="color: var(--color-text-soft)">
          Đã chọn <b style="color: var(--color-primary-400)">{{ selectedDeckIds.size }}</b> deck
        </p>
        <div class="flex gap-2">
          <button @click="clearSelection"
                  class="px-3 py-1.5 rounded-lg text-xs font-medium transition hover:opacity-80"
                  style="background-color: var(--color-surface-03); color: var(--color-text-muted)">
            Bỏ chọn tất cả
          </button>
          <button @click="startMultiQuiz"
                  class="px-4 py-1.5 rounded-lg text-xs font-semibold transition hover:opacity-80"
                  style="background-color: var(--color-primary-600); color: #fff">
            🧠 Kiểm tra tổng hợp
          </button>
        </div>
      </div>
    </Transition>

    <!-- Filters -->
    <div class="flex flex-wrap items-center gap-2 mt-5 mb-6">
      <!-- CEFR pills -->
      <button v-for="lv in LEVELS" :key="lv"
              @click="selectedLevel = lv; loadDecks()"
              class="px-3 py-1 rounded-full text-xs font-semibold border transition"
              :style="selectedLevel === lv
                ? levelActiveStyle(lv)
                : 'background-color: var(--color-surface-02); color: var(--color-text-muted); border-color: var(--color-surface-04)'">
        {{ lv === 'All' ? 'Tất cả' : lv }}
      </button>

      <!-- Domain dropdown -->
      <select v-model="selectedDomain" @change="loadDecks()"
              class="ml-2 px-3 py-1.5 rounded-xl text-xs outline-none"
              style="background-color: var(--color-surface-02); color: var(--color-text-base); border: 1px solid var(--color-surface-04)">
        <option value="">Tất cả chủ đề</option>
        <option v-for="d in DOMAINS" :key="d.value" :value="d.value">{{ d.label }}</option>
      </select>
    </div>

    <!-- Loading skeletons -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="i in 6" :key="i" class="rounded-2xl h-48 animate-pulse"
           style="background-color: var(--color-surface-02)"></div>
    </div>

    <!-- Empty state -->
    <div v-else-if="decks.length === 0" class="text-center py-20"
         style="color: var(--color-text-muted)">
      <p class="text-5xl mb-3">🃏</p>
      <p class="font-semibold">Chưa có deck nào</p>
      <p class="text-sm mt-1">Hãy tạo deck đầu tiên hoặc thay đổi bộ lọc.</p>
    </div>

    <!-- Deck grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="deck in decks" :key="deck.id"
           class="deck-card rounded-2xl p-5 flex flex-col gap-3 transition"
           :class="{ 'deck-selected': selectMode && selectedDeckIds.has(deck.id) }"
           :style="selectMode && selectedDeckIds.has(deck.id)
             ? 'background-color: var(--color-surface-02); border: 2px solid var(--color-primary-500)'
             : 'background-color: var(--color-surface-02); border: 1px solid var(--color-surface-03)'"
           @click="selectMode ? toggleDeckSelect(deck.id) : null">
        <!-- Top row: checkbox (select mode) + name + level badge -->
        <div class="flex items-start justify-between gap-2">
          <!-- Checkbox in select mode -->
          <div v-if="selectMode"
               class="shrink-0 mt-0.5 w-5 h-5 rounded-md border-2 flex items-center justify-center transition"
               :style="selectedDeckIds.has(deck.id)
                 ? 'background-color: var(--color-primary-600); border-color: var(--color-primary-600)'
                 : 'border-color: var(--color-surface-04)'">
            <span v-if="selectedDeckIds.has(deck.id)" class="text-white text-xs">✓</span>
          </div>
          <h3 class="font-bold text-base leading-snug flex-1" style="color: var(--color-text-base)">
            {{ deck.name }}
          </h3>
          <span v-if="deck.cefr_level"
                class="shrink-0 text-xs font-bold px-2 py-0.5 rounded-full"
                :style="levelBadgeStyle(deck.cefr_level)">
            {{ deck.cefr_level }}
          </span>
        </div>

        <!-- Description -->
        <p v-if="deck.description" class="text-xs line-clamp-2"
           style="color: var(--color-text-muted)">{{ deck.description }}</p>

        <!-- Progress bar: mastered / total words -->
        <div>
          <div class="flex justify-between text-xs mb-1" style="color: var(--color-text-muted)">
            <span>Đã thuộc: {{ deck.mastered_count }} / {{ deck.word_count ?? deck.card_count }} từ</span>
            <span>{{ progressPct(deck) }}%</span>
          </div>
          <div class="w-full h-1.5 rounded-full overflow-hidden"
               style="background-color: var(--color-surface-04)">
            <div class="h-full rounded-full transition-all"
                 style="background-color: var(--color-primary-500)"
                 :style="{ width: progressPct(deck) + '%' }"></div>
          </div>
        </div>

        <!-- Due badge + CTA (hidden in select mode) -->
        <div v-if="!selectMode" class="flex items-center justify-between mt-auto pt-1">
          <span v-if="deck.due_count > 0"
                class="text-xs font-semibold px-2.5 py-1 rounded-lg"
                style="background-color: rgba(239,68,68,0.12); color: #fca5a5">
            🔔 {{ deck.due_count }} thẻ cần ôn
          </span>
          <span v-else class="text-xs" style="color: var(--color-text-muted)">
            ✓ Không có thẻ đến hạn
          </span>

          <div class="flex items-center gap-2">
            <button @click.stop="toggleHistory(deck)"
                    class="px-2.5 py-1.5 rounded-lg text-xs transition hover:opacity-80"
                    :style="openHistoryDeckId === deck.id
                      ? 'background-color: var(--color-primary-600)22; color: var(--color-primary-400)'
                      : 'background-color: var(--color-surface-03); color: var(--color-text-muted)'">
              📊
            </button>
            <button @click.stop="$router.push({ name: 'deck-words', params: { deckId: deck.id } })"
                    class="px-2.5 py-1.5 rounded-lg text-xs transition hover:opacity-80"
                    style="background-color: var(--color-surface-03); color: var(--color-text-muted)">
              📖
            </button>
            <button @click.stop="startStudy(deck)"
                    :disabled="deck.due_count === 0 && deck.card_count === 0"
                    class="px-4 py-2 rounded-xl text-xs font-semibold transition"
                    :style="deck.due_count > 0 || deck.card_count > 0
                      ? 'background-color: var(--color-primary-600); color: #fff; cursor: pointer;'
                      : 'background-color: var(--color-surface-04); color: var(--color-text-muted); cursor: not-allowed;'">
              Học ngay →
            </button>
          </div>
        </div>

        <!-- Select mode hint -->
        <p v-if="selectMode" class="text-xs text-center pt-1"
           style="color: var(--color-text-muted)">
          {{ selectedDeckIds.has(deck.id) ? '✓ Đã chọn' : 'Nhấn để chọn' }}
        </p>

        <!-- Study history chart (lazy loaded, only in normal mode) -->
        <Transition name="slide-history">
          <div v-if="!selectMode && openHistoryDeckId === deck.id"
               class="mt-3 pt-3 overflow-hidden"
               style="border-top: 1px solid var(--color-surface-04)">
            <DeckHistoryChart :deck-id="deck.id" />
          </div>
        </Transition>
      </div>
    </div>

    <!-- Create deck modal -->
    <Transition name="fade">
      <div v-if="showCreateModal"
           class="fixed inset-0 z-50 flex items-center justify-center p-4"
           style="background: rgba(0,0,0,0.5)">
        <div class="rounded-2xl p-6 w-full max-w-sm"
             style="background-color: var(--color-surface-01)">
          <h2 class="font-bold text-lg mb-4" style="color: var(--color-text-base)">Tạo deck mới</h2>

          <input v-model="newDeck.name" placeholder="Tên deck *" type="text"
                 class="w-full px-3 py-2.5 rounded-xl text-sm mb-3 outline-none"
                 style="background-color: var(--color-surface-02); color: var(--color-text-base); border: 1px solid var(--color-surface-04)" />

          <textarea v-model="newDeck.description" placeholder="Mô tả (tuỳ chọn)" rows="2"
                    class="w-full px-3 py-2.5 rounded-xl text-sm mb-3 outline-none resize-none"
                    style="background-color: var(--color-surface-02); color: var(--color-text-base); border: 1px solid var(--color-surface-04)"></textarea>

          <select v-model="newDeck.cefr_level"
                  class="w-full px-3 py-2.5 rounded-xl text-sm mb-4 outline-none"
                  style="background-color: var(--color-surface-02); color: var(--color-text-base); border: 1px solid var(--color-surface-04)">
            <option value="">-- Cấp độ CEFR --</option>
            <option v-for="lv in CEFR_CHOICES" :key="lv" :value="lv">{{ lv }}</option>
          </select>

          <div class="flex gap-3">
            <button @click="showCreateModal = false"
                    class="flex-1 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
                    style="background-color: var(--color-surface-03); color: var(--color-text-muted)">
              Huỷ
            </button>
            <button @click="createDeck"
                    :disabled="!newDeck.name.trim() || creating"
                    class="flex-1 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
                    style="background-color: var(--color-primary-600); color: #fff">
              {{ creating ? 'Đang tạo...' : 'Tạo deck' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { vocabularyApi } from '@/api/vocabulary.js'
import { usersApi } from '@/api/users.js'
import DeckHistoryChart from '@/components/DeckHistoryChart.vue'

const router = useRouter()

const LEVELS = ['All', 'A1', 'A2', 'B1', 'B2', 'C1']
const CEFR_CHOICES = ['A1', 'A2', 'B1', 'B2', 'C1']
const DOMAINS = [
  { value: 'business', label: 'Business' },
  { value: 'casual', label: 'Casual' },
  { value: 'academic', label: 'Academic' },
  { value: 'medical', label: 'Medical' },
  { value: 'travel', label: 'Travel' },
]

const decks = ref([])
const loading = ref(false)
const selectedLevel = ref('All')
const selectedDomain = ref('')

const showCreateModal = ref(false)
const creating = ref(false)
const newDeck = ref({ name: '', description: '', cefr_level: '' })

// Track which deck's history panel is open
const openHistoryDeckId = ref(null)

// ── Feature: notification hour ─────────────────────────────────────────────
const notifyHour = ref(8)

async function loadSettings() {
  try {
    const res = await usersApi.getSettings()
    const d = res.data?.data ?? res.data
    notifyHour.value = d?.flashcard_notify_hour ?? 8
  } catch { /* ignore */ }
}

async function saveNotifyHour() {
  try {
    await usersApi.updateSettings({ flashcard_notify_hour: notifyHour.value })
  } catch { /* ignore */ }
}

// ── Feature: multi-deck select mode ────────────────────────────────────────
const selectMode = ref(false)
const selectedDeckIds = ref(new Set())

function toggleSelectMode() {
  selectMode.value = !selectMode.value
  if (!selectMode.value) selectedDeckIds.value = new Set()
}

function toggleDeckSelect(deckId) {
  const s = new Set(selectedDeckIds.value)
  if (s.has(deckId)) s.delete(deckId)
  else s.add(deckId)
  selectedDeckIds.value = s
}

function clearSelection() {
  selectedDeckIds.value = new Set()
}

function startMultiQuiz() {
  if (selectedDeckIds.value.size === 0) return
  const ids = [...selectedDeckIds.value].join(',')
  router.push({ name: 'flashcard-quiz-multi', query: { decks: ids, count: 20 } })
}

// ── History toggle ──────────────────────────────────────────────────────────
function toggleHistory(deck) {
  openHistoryDeckId.value = openHistoryDeckId.value === deck.id ? null : deck.id
}

async function loadDecks() {
  loading.value = true
  try {
    const params = {}
    if (selectedLevel.value !== 'All') params.cefr_level = selectedLevel.value
    if (selectedDomain.value) params.domain = selectedDomain.value
    const res = await vocabularyApi.getDecks(params)
    const d = res.data?.data ?? res.data
    decks.value = d?.results ?? (Array.isArray(d) ? d : [])
  } catch {
    decks.value = []
  } finally {
    loading.value = false
  }
}

async function createDeck() {
  if (!newDeck.value.name.trim()) return
  creating.value = true
  try {
    const payload = {
      name: newDeck.value.name.trim(),
      description: newDeck.value.description.trim() || undefined,
      cefr_level: newDeck.value.cefr_level || undefined,
      is_public: false,
    }
    await vocabularyApi.createDeck(payload)
    showCreateModal.value = false
    newDeck.value = { name: '', description: '', cefr_level: '' }
    await loadDecks()
  } catch { /* ignore */ } finally {
    creating.value = false
  }
}

function startStudy(deck) {
  router.push({ name: 'flashcard-study', params: { deckId: deck.id } })
}

function progressPct(deck) {
  const total = deck.word_count ?? deck.card_count
  if (!total) return 0
  return Math.round((deck.mastered_count / total) * 100)
}

function levelActiveStyle(lv) {
  const map = {
    All: 'background-color: var(--color-primary-600); color: #fff; border-color: var(--color-primary-600)',
    A1: 'background-color: #22c55e22; color: #86efac; border-color: #22c55e44',
    A2: 'background-color: #3b82f622; color: #93c5fd; border-color: #3b82f644',
    B1: 'background-color: #a855f722; color: #d8b4fe; border-color: #a855f744',
    B2: 'background-color: #f59e0b22; color: #fcd34d; border-color: #f59e0b44',
    C1: 'background-color: #ef444422; color: #fca5a5; border-color: #ef444444',
  }
  return map[lv] || map.All
}

function levelBadgeStyle(lv) {
  const map = {
    A1: 'background-color: #22c55e22; color: #86efac',
    A2: 'background-color: #3b82f622; color: #93c5fd',
    B1: 'background-color: #a855f722; color: #d8b4fe',
    B2: 'background-color: #f59e0b22; color: #fcd34d',
    C1: 'background-color: #ef444422; color: #fca5a5',
  }
  return map[lv] || 'background-color: var(--color-surface-03); color: var(--color-text-muted)'
}

onMounted(() => {
  loadDecks()
  loadSettings()
})
</script>

<style scoped>
.deck-card { transition: transform 0.15s, box-shadow 0.15s; }
.deck-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}
.deck-selected { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(99,102,241,0.2); }
.line-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-history-enter-active { transition: max-height 0.25s ease, opacity 0.2s ease; }
.slide-history-leave-active  { transition: max-height 0.2s ease, opacity 0.15s ease; }
.slide-history-enter-from, .slide-history-leave-to { max-height: 0; opacity: 0; }
.slide-history-enter-to, .slide-history-leave-from { max-height: 200px; opacity: 1; }

.slide-up-enter-active { transition: all 0.2s ease; }
.slide-up-enter-from { opacity: 0; transform: translateY(-8px); }
.slide-up-leave-active { transition: all 0.15s ease; }
.slide-up-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
