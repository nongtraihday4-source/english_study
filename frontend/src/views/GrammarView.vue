<template>
  <div class="p-6 max-w-4xl mx-auto">
    <h1 class="text-2xl font-bold mb-1" style="color: var(--color-text-base)">Ngữ pháp</h1>
    <p class="text-sm mb-5" style="color: var(--color-text-muted)">Ôn tập và luyện tập các chủ điểm ngữ pháp</p>

    <!-- Search + filter bar -->
    <div class="space-y-3 mb-6">
      <input
        v-model="searchRaw"
        type="search"
        placeholder="Tìm chủ điểm ngữ pháp..."
        class="w-full px-4 py-2.5 rounded-xl text-sm outline-none transition"
        style="background-color: var(--color-surface-02);
               border: 1px solid var(--color-surface-04);
               color: var(--color-text-base);"
      />
      <div class="flex flex-wrap gap-2">
        <button
          v-for="lv in LEVELS" :key="lv"
          @click="setLevel(lv)"
          class="px-3 py-1 rounded-full text-xs font-semibold transition"
          :style="selectedLevel === lv
            ? 'background:#6366f1; color:#fff'
            : 'background-color:var(--color-surface-02); color:var(--color-text-muted); border:1px solid var(--color-surface-04)'"
        >{{ lv }}</button>
      </div>
    </div>

    <!-- Enrollment notice (logged in but no enrolled courses) -->
    <div v-if="isLoggedIn && unlockedLevels.size === 0 && !loading"
         class="flex items-start gap-3 rounded-xl px-4 py-3 mb-5 text-sm"
         style="background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.25); color:#a5b4fc">
      <span class="flex-shrink-0 text-base">ℹ️</span>
      <span>
        Đăng ký khoá học để mở khoá các chủ điểm ngữ pháp.
        <RouterLink to="/courses" class="font-semibold underline ml-1" style="color:#818cf8">Xem khoá học →</RouterLink>
      </span>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="rounded-xl h-16 animate-pulse"
           style="background-color: var(--color-surface-02)"></div>
    </div>

    <!-- Content -->
    <div v-else-if="levelSections.length">
      <template v-for="section in levelSections" :key="section.level">

        <!-- Level separator (All mode) -->
        <div v-if="selectedLevel === 'All'" class="flex items-center gap-3 mt-6 mb-3">
          <span class="text-xs font-bold px-2 py-0.5 rounded"
                :style="levelColor(section.level)">{{ section.level }}</span>
          <div class="flex-1 h-px" style="background: var(--color-surface-04)"></div>
          <span v-if="isLocked(section.level)"
                class="text-xs" style="color:var(--color-text-muted)">🔒 Chưa đăng ký</span>
          <span v-else class="text-xs" style="color:#86efac">✓ Đã đăng ký</span>
        </div>

        <!-- Concept groups in this level -->
        <div class="space-y-2">
          <div v-for="group in section.groups" :key="group.key"
               class="rounded-xl overflow-hidden"
               :style="isLocked(section.level)
                 ? 'background-color:var(--color-surface-02); border:1px solid var(--color-surface-04); opacity:0.55'
                 : 'background-color:var(--color-surface-02); border:1px solid var(--color-surface-04)'">

            <!-- Group header -->
            <div
              @click="isLocked(section.level) ? null : toggleGroup(group.key)"
              class="flex items-center gap-3 p-4 transition"
              :class="isLocked(section.level) ? 'cursor-not-allowed' : 'cursor-pointer hover:bg-white/5'"
            >
              <span class="text-xl flex-shrink-0">{{ group.icon }}</span>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <p class="font-semibold text-sm" style="color: var(--color-text-base)">{{ group.title }}</p>
                  <span v-if="selectedLevel === 'All'" class="px-1.5 py-0.5 rounded text-xs font-bold"
                        :style="levelColor(section.level)">{{ section.level }}</span>
                </div>
                <p class="text-xs mt-0.5" style="color: var(--color-text-muted)">
                  {{ group.topics.length }} chủ điểm
                </p>
              </div>
              <span class="flex-shrink-0">
                <span v-if="isLocked(section.level)" style="color:var(--color-text-muted)">🔒</span>
                <span v-else style="color: var(--color-text-soft)">
                  {{ isGroupOpen(group.key) ? '▲' : '▼' }}
                </span>
              </span>
            </div>

            <!-- Locked message -->
            <div v-if="isLocked(section.level)"
                 class="px-5 pb-4 text-xs"
                 style="color: var(--color-text-muted)">
              Đăng ký khoá học cấp <strong>{{ section.level }}</strong> để học nhóm chủ điểm này.
              <RouterLink to="/courses" class="ml-1 underline" style="color:#818cf8">Xem khoá học</RouterLink>
            </div>

            <!-- Topics list (if unlocked + expanded) -->
            <Transition name="fold">
              <div v-if="!isLocked(section.level) && isGroupOpen(group.key)"
                   class="border-t" style="border-color: var(--color-surface-04)">
                <RouterLink
                  v-for="topic in group.topics" :key="topic.id"
                  :to="{ name: 'grammar-detail', params: { slug: topic.slug } }"
                  class="flex items-center gap-3 px-5 py-3 transition hover:bg-white/5"
                  style="border-top: 1px solid var(--color-surface-04); text-decoration: none; display: flex"
                >
                  <span class="text-sm" style="color: var(--color-text-base)">{{ topic.title }}</span>
                  <span class="ml-auto flex-shrink-0 text-xs"
                        style="color: var(--color-text-muted)">
                    {{ topic.rule_count || 0 }} quy tắc
                  </span>
                  <span class="flex-shrink-0 text-xs ml-2" style="color:#818cf8">→</span>
                </RouterLink>
              </div>
            </Transition>

          </div>
        </div>

      </template>

      <!-- Load more -->
      <div v-if="hasMore" class="text-center mt-5">
        <button @click="loadMore" :disabled="loadingMore"
                class="px-6 py-2 rounded-xl text-sm font-medium transition hover:opacity-80 disabled:opacity-50"
                style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-text-muted)">
          {{ loadingMore ? 'Đang tải...' : 'Xem thêm' }}
        </button>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="text-center py-16" style="color: var(--color-text-muted)">
      <p class="text-4xl mb-3">📖</p>
      <p>{{ search ? 'Không tìm thấy chủ điểm phù hợp.' : 'Chưa có chủ điểm ngữ pháp nào.' }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { grammarApi } from '@/api/curriculum.js'
import { useAuthStore } from '@/stores/auth.js'
import { useDashboardStore } from '@/stores/dashboard.js'

const LEVELS = ['All', 'A1', 'A2', 'B1', 'B2', 'C1']
const LEVEL_ORDER = { A1: 0, A2: 1, B1: 2, B2: 3, C1: 4, C2: 5 }

const auth = useAuthStore()
const dashboard = useDashboardStore()
const { isLoggedIn } = storeToRefs(auth)

// ── Topics ───────────────────────────────────────────────────────────────────
const topics      = ref([])
const loading     = ref(false)
const loadingMore = ref(false)
const nextUrl     = ref(null)

// ── Filter state ─────────────────────────────────────────────────────────────
const searchRaw      = ref('')
const search         = ref('')
const selectedLevel  = ref('All')

// Debounce search input (300 ms)
let _debTimer = null
watch(searchRaw, (v) => {
  clearTimeout(_debTimer)
  _debTimer = setTimeout(() => { search.value = v.trim() }, 300)
})

// ── Unlock logic ─────────────────────────────────────────────────────────────
// Compute which CEFR levels are unlocked from enrolled courses.
// Enrolling at level X unlocks all levels ≤ X (cumulative).
const unlockedLevels = computed(() => {
  if (!isLoggedIn.value) return new Set()
  const enrolled = dashboard.enrolledCourses()
  if (!enrolled.length) return new Set()
  const codes = enrolled.map(e => e.course_level_code).filter(Boolean)
  if (!codes.length) return new Set()
  const maxOrder = Math.max(...codes.map(c => LEVEL_ORDER[c] ?? -1))
  return new Set(LEVELS.filter(lv => lv !== 'All' && (LEVEL_ORDER[lv] ?? 99) <= maxOrder))
})

function isLocked(level) {
  if (!isLoggedIn.value) return true
  return !unlockedLevels.value.has(level)
}

// ── Group expand/collapse state ───────────────────────────────────────────────
const collapsedGroups = ref(new Set())

function toggleGroup(key) {
  const s = new Set(collapsedGroups.value)
  if (s.has(key)) s.delete(key)
  else s.add(key)
  collapsedGroups.value = s
}

function isGroupOpen(key) {
  return !collapsedGroups.value.has(key)
}

// ── Grouping helpers ─────────────────────────────────────────────────────────
function extractGroupKey(title) {
  // Remove leading "The ", split on separator chars, remove "of be" / "or X" modifiers
  let t = title
    .replace(/^the\s+/i, '')
    .replace(/[:\-–]/g, '\x00') // replace separators with null sentinel
    .split('\x00')[0]           // keep text before first separator
    .replace(/\s+or\s+.*/i, '')
    .replace(/\s+of\s+be.*/i, '')
    .replace(/\s+with\s+.*/i, '')
    .replace(/\?.*/, '')        // remove trailing question marks
    .toLowerCase().trim()
  // Take first 2 meaningful words as the group key
  const words = t.split(/\s+/).filter(w => w.length > 1)
  return words.slice(0, 2).join(' ')
}

function groupDisplayTitle(key) {
  return key.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
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

// ── Derived display data ──────────────────────────────────────────────────────
const levelSections = computed(() => {
  // 1. Filter by search
  let list = topics.value
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(t =>
      t.title.toLowerCase().includes(q) ||
      (t.description || '').toLowerCase().includes(q)
    )
  }

  // 2. Build concept groups (key → group)
  const groupMap = new Map()
  for (const topic of list) {
    const key = extractGroupKey(topic.title)
    if (!groupMap.has(key)) {
      groupMap.set(key, {
        key,
        title: groupDisplayTitle(key),
        level: topic.level,
        icon: topic.icon || '📖',
        topics: [],
      })
    }
    groupMap.get(key).topics.push(topic)
  }

  // 3. Group groups by level → level sections
  const sectionMap = new Map()
  for (const [key, group] of groupMap) {
    const lv = group.level
    if (!sectionMap.has(lv)) sectionMap.set(lv, [])
    sectionMap.get(lv).push(group)
  }

  // 4. Sort sections by CEFR order, sort groups within each section alphabetically
  return [...sectionMap.entries()]
    .sort(([a], [b]) => (LEVEL_ORDER[a] ?? 99) - (LEVEL_ORDER[b] ?? 99))
    .map(([level, groups]) => ({
      level,
      groups: groups.sort((a, b) => a.key.localeCompare(b.key)),
    }))
})

const hasMore = computed(() => !!nextUrl.value)

// ── API calls ─────────────────────────────────────────────────────────────────
async function fetchTopics() {
  loading.value = true
  topics.value = []
  nextUrl.value = null
  try {
    const params = { page_size: 100 }
    if (selectedLevel.value !== 'All') params.level = selectedLevel.value
    const res = await grammarApi.listTopics(params)
    const d = res.data?.data ?? res.data
    topics.value = d?.results || (Array.isArray(d) ? d : [])
    nextUrl.value = d?.next || null
  } catch {
    topics.value = []
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  if (!nextUrl.value || loadingMore.value) return
  loadingMore.value = true
  try {
    // Extract `page` (or full URL) from nextUrl
    const url = new URL(nextUrl.value)
    const params = Object.fromEntries(url.searchParams.entries())
    const res = await grammarApi.listTopics(params)
    const d = res.data?.data ?? res.data
    topics.value.push(...(d?.results || []))
    nextUrl.value = d?.next || null
  } catch {
    // keep current data
  } finally {
    loadingMore.value = false
  }
}

function setLevel(lv) {
  if (selectedLevel.value === lv) return
  selectedLevel.value = lv
  collapsedGroups.value = new Set() // reset collapse state when switching filter
  fetchTopics()
}

onMounted(async () => {
  // Ensure dashboard is loaded so unlockedLevels is computed correctly
  await dashboard.fetch()
  fetchTopics()
})
</script>

<style scoped>
.fold-enter-active, .fold-leave-active { transition: opacity .2s ease; }
.fold-enter-from, .fold-leave-to { opacity: 0; }
</style>
