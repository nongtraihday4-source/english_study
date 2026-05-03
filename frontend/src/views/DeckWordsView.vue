<template>
  <div class="min-h-screen py-8 px-4" style="background-color: var(--color-bg)">
    <div class="max-w-2xl mx-auto">

      <!-- Header -->
      <div class="flex items-center gap-3 mb-6">
        <button @click="$router.back()"
                class="p-2 rounded-lg transition hover:opacity-70"
                style="background-color: var(--color-surface-02); color: var(--color-text-muted)">
          ←
        </button>
        <div class="flex-1">
          <h1 class="text-xl font-bold" style="color: var(--color-text-primary)">
            {{ deckName || 'Tất cả từ trong deck' }}
          </h1>
          <p class="text-sm" style="color: var(--color-text-muted)">
            📖 {{ stats.learning }} đang học &nbsp;·&nbsp; ✅ {{ stats.mastered }} đã nhớ
          </p>
        </div>
        <button v-if="stats.mastered > 0"
                @click="quizMastered"
                class="px-3 py-2 rounded-xl text-xs font-semibold transition hover:opacity-80"
                style="background-color: var(--color-primary-600); color: #fff">
          🧠 Quiz từ nhớ
        </button>
      </div>

      <!-- Tab bar -->
      <div class="flex gap-1 mb-4 p-1 rounded-xl"
           style="background-color: var(--color-surface-02)">
        <button v-for="tab in tabs" :key="tab.key"
                @click="activeTab = tab.key; subFilter = 'all'"
                class="flex-1 py-2 px-3 rounded-lg text-sm font-medium transition"
                :style="activeTab === tab.key
                  ? 'background-color: var(--color-primary-600); color: #fff'
                  : 'color: var(--color-text-muted)'">
          {{ tab.label }}
          <span class="ml-1 text-xs opacity-80">({{ tab.count }})</span>
        </button>
      </div>

      <!-- Search + filter + sort toolbar -->
      <div class="flex flex-wrap gap-2 mb-4">
        <div class="flex-1 min-w-0 relative">
          <span class="absolute left-2.5 top-1/2 -translate-y-1/2 text-sm"
                style="color: var(--color-text-muted)">🔍</span>
          <input v-model="searchQuery"
                 placeholder="Tìm từ hoặc nghĩa..."
                 class="w-full pl-7 pr-3 py-2 rounded-xl text-sm outline-none"
                 style="background-color: var(--color-surface-02); color: var(--color-text-primary); border: 1px solid var(--color-surface-04)" />
        </div>

        <!-- Sub-status filter (only on Đang học tab) -->
        <select v-if="activeTab === 'learning'"
                v-model="subFilter"
                class="px-3 py-2 rounded-xl text-xs outline-none"
                style="background-color: var(--color-surface-02); color: var(--color-text-muted); border: 1px solid var(--color-surface-04)">
          <option value="all">Tất cả</option>
          <option value="new">🆕 Mới</option>
          <option value="learning">📖 Học</option>
          <option value="review">🔁 Ôn tập</option>
        </select>

        <!-- Sort -->
        <select v-model="sortBy"
                class="px-3 py-2 rounded-xl text-xs outline-none"
                style="background-color: var(--color-surface-02); color: var(--color-text-muted); border: 1px solid var(--color-surface-04)">
          <option value="alpha">A → Z</option>
          <option value="alpha_desc">Z → A</option>
          <option value="interval">Interval ↑</option>
          <option value="interval_desc">Interval ↓</option>
        </select>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-16" style="color: var(--color-text-muted)">
        <div class="animate-spin text-3xl mb-3">⟳</div>
        Đang tải...
      </div>

      <!-- Empty state -->
      <div v-else-if="displayedWords.length === 0" class="text-center py-16"
           style="color: var(--color-text-muted)">
        <div class="text-4xl mb-3">{{ activeTab === 'mastered' ? '🎯' : '📚' }}</div>
        <p v-if="searchQuery || subFilter !== 'all'" class="text-sm">Không tìm thấy từ nào khớp với bộ lọc.</p>
        <p v-else-if="activeTab === 'mastered'" class="text-sm">Chưa có từ nào được đánh dấu "đã nhớ".<br>Học flashcard và đánh dấu những từ bạn nhớ tốt!</p>
        <p v-else class="text-sm">Không có từ nào đang học.</p>
      </div>

      <!-- Word list -->
      <TransitionGroup v-else name="word-list" tag="div" class="flex flex-col gap-3">
        <div v-for="item in displayedWords" :key="item.word_id"
             class="rounded-xl p-4 transition"
             style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-03)">
          <div class="flex justify-between items-start gap-3">
            <!-- Word info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="font-bold text-base" style="color: var(--color-text-primary)">
                  {{ item.word }}
                </span>
                <span v-if="item.part_of_speech"
                      class="text-xs px-1.5 py-0.5 rounded"
                      style="background-color: var(--color-surface-04); color: var(--color-text-muted)">
                  {{ item.part_of_speech }}
                </span>
                <span v-if="item.cefr_level"
                      class="text-xs px-1.5 py-0.5 rounded font-semibold"
                      :style="cefrColor(item.cefr_level)">
                  {{ item.cefr_level }}
                </span>
                <span class="text-xs px-1.5 py-0.5 rounded"
                      :style="statusBadgeStyle(item.status)">
                  {{ statusLabel(item.status) }}
                </span>
              </div>
              <p v-if="item.ipa_uk || item.ipa_us"
                 class="text-xs mt-0.5" style="color: var(--color-text-muted)">
                {{ item.ipa_uk || item.ipa_us }}
              </p>
              <p class="text-sm mt-1" style="color: var(--color-text-secondary)">
                {{ item.meaning_vi }}
              </p>

              <!-- SM-2 progress bar (only for non-mastered) -->
              <div v-if="item.progress && item.status !== 'mastered'" class="mt-2">
                <div class="flex items-center gap-2">
                  <div class="flex-1 h-1.5 rounded-full overflow-hidden"
                       style="background-color: var(--color-surface-04)">
                    <div class="h-full rounded-full transition-all"
                         :style="`width: ${progressWidth(item.progress)}%; background-color: var(--color-primary-500)`">
                    </div>
                  </div>
                  <span class="text-xs" style="color: var(--color-text-muted)">
                    {{ item.progress.repetitions }}x · {{ item.progress.interval_days }}d
                  </span>
                </div>
              </div>
            </div>

            <!-- Action buttons -->
            <div class="flex flex-col gap-2 shrink-0">
              <button v-if="item.status !== 'mastered'"
                      @click="markMastered(item)"
                      :disabled="toggling === item.word_id"
                      class="px-3 py-1.5 rounded-lg text-xs font-medium transition hover:opacity-80"
                      style="background-color: #16a34a22; color: #22c55e; border: 1px solid #22c55e44">
                {{ toggling === item.word_id ? '...' : '✅ Đã nhớ' }}
              </button>
              <button v-else
                      @click="unmarkMastered(item)"
                      :disabled="toggling === item.word_id"
                      class="px-3 py-1.5 rounded-lg text-xs font-medium transition hover:opacity-80"
                      style="background-color: var(--color-surface-04); color: var(--color-text-muted)">
                {{ toggling === item.word_id ? '...' : '↩ Ôn lại' }}
              </button>
              <button @click="deleteWord(item)"
                      :disabled="deleting === item.word_id"
                      class="px-3 py-1.5 rounded-lg text-xs font-medium transition hover:opacity-80"
                      style="background-color: #ef444422; color: #f87171; border: 1px solid #ef444430">
                {{ deleting === item.word_id ? '...' : '🗑 Xoá' }}
              </button>
            </div>
          </div>
        </div>
      </TransitionGroup>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { vocabularyApi } from '@/api/vocabulary.js'

const route = useRoute()
const router = useRouter()

const deckId = route.params.deckId
const deckName = ref('')
const allWords = ref([])
const loading = ref(true)
const toggling = ref(null)   // word_id currently being toggled
const deleting = ref(null)   // word_id currently being deleted
const activeTab = ref('learning')
const searchQuery = ref('')
const subFilter = ref('all')  // 'all' | 'new' | 'learning' | 'review'
const sortBy = ref('alpha')   // 'alpha' | 'alpha_desc' | 'interval' | 'interval_desc'

const stats = computed(() => ({
  learning: allWords.value.filter(w => w.status !== 'mastered').length,
  mastered: allWords.value.filter(w => w.status === 'mastered').length,
}))

const tabs = computed(() => [
  { key: 'learning', label: 'Đang học', count: stats.value.learning },
  { key: 'mastered', label: 'Đã nhớ',  count: stats.value.mastered  },
])

const displayedWords = computed(() => {
  let list = activeTab.value === 'mastered'
    ? allWords.value.filter(w => w.status === 'mastered')
    : allWords.value.filter(w => w.status !== 'mastered')

  // sub-status filter
  if (activeTab.value !== 'mastered' && subFilter.value !== 'all') {
    list = list.filter(w => w.status === subFilter.value)
  }

  // search
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter(w =>
      w.word.toLowerCase().includes(q) ||
      (w.meaning_vi || '').toLowerCase().includes(q)
    )
  }

  // sort
  list = [...list]
  if (sortBy.value === 'alpha') list.sort((a, b) => a.word.localeCompare(b.word))
  else if (sortBy.value === 'alpha_desc') list.sort((a, b) => b.word.localeCompare(a.word))
  else if (sortBy.value === 'interval') list.sort((a, b) => (a.progress?.interval_days ?? 0) - (b.progress?.interval_days ?? 0))
  else if (sortBy.value === 'interval_desc') list.sort((a, b) => (b.progress?.interval_days ?? 0) - (a.progress?.interval_days ?? 0))

  return list
})

async function loadWords() {
  loading.value = true
  try {
    const res = await vocabularyApi.getDeckWords(deckId)
    const data = res.data?.data ?? res.data
    deckName.value = data.deck_name ?? ''
    allWords.value = Array.isArray(data.words) ? data.words : []
  } catch {
    allWords.value = []
  } finally {
    loading.value = false
  }
}

async function markMastered(item) {
  toggling.value = item.word_id
  try {
    await vocabularyApi.toggleMastered(deckId, item.word_id, true)
    item.status = 'mastered'
    if (item.progress) item.progress.is_mastered = true
  } catch { /* ignore */ } finally {
    toggling.value = null
  }
}

async function unmarkMastered(item) {
  toggling.value = item.word_id
  try {
    await vocabularyApi.toggleMastered(deckId, item.word_id, false)
    // Revert to learning/review based on existing progress
    if (item.progress) {
      item.progress.is_mastered = false
      item.status = (item.progress.repetitions >= 3 && item.progress.interval_days >= 7)
        ? 'review' : 'learning'
    } else {
      item.status = 'new'
    }
  } catch { /* ignore */ } finally {
    toggling.value = null
  }
}

function quizMastered() {
  router.push({
    name: 'flashcard-quiz',
    params: { deckId },
    query: { source: 'mastered' },
  })
}

async function deleteWord(item) {
  if (!confirm(`Xoá từ "${item.word}" khỏi deck?`)) return
  deleting.value = item.word_id
  try {
    await vocabularyApi.removeWordFromDeck({ word_id: item.word_id, deck_id: Number(deckId) })
    allWords.value = allWords.value.filter(w => w.word_id !== item.word_id)
  } catch { /* ignore */ } finally {
    deleting.value = null
  }
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function progressWidth(p) {
  // 0–100% based on interval (capped at 30 days)
  return Math.min((p.interval_days / 30) * 100, 100)
}

function statusLabel(s) {
  return { new: '🆕 Mới', learning: '📖 Học', review: '🔁 Ôn', mastered: '✅ Nhớ' }[s] || s
}

function statusBadgeStyle(s) {
  const map = {
    new:      'background-color: #3b82f622; color: #60a5fa',
    learning: 'background-color: #f59e0b22; color: #fbbf24',
    review:   'background-color: #8b5cf622; color: #a78bfa',
    mastered: 'background-color: #22c55e22; color: #4ade80',
  }
  return map[s] || ''
}

function cefrColor(level) {
  const map = {
    A1: 'background-color: #22c55e22; color: #4ade80',
    A2: 'background-color: #22c55e22; color: #4ade80',
    B1: 'background-color: #3b82f622; color: #60a5fa',
    B2: 'background-color: #3b82f622; color: #60a5fa',
    C1: 'background-color: #f59e0b22; color: #fbbf24',
    C2: 'background-color: #ef444422; color: #f87171',
  }
  return map[level] || 'background-color: var(--color-surface-04); color: var(--color-text-muted)'
}

onMounted(loadWords)
</script>

<style scoped>
.word-list-enter-active,
.word-list-leave-active {
  transition: all 0.25s ease;
}
.word-list-enter-from,
.word-list-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
