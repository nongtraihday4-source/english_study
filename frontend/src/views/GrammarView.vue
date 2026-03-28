<template>
  <div class="p-6 max-w-4xl mx-auto">
    <h1 class="text-2xl font-bold mb-1" style="color: var(--color-text-base)">Ngữ pháp</h1>
    <p class="text-sm mb-5" style="color: var(--color-text-muted)">Lộ trình ngữ pháp theo từng cấp độ CEFR</p>

    <!-- Level tabs -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button
        v-for="lv in LEVELS" :key="lv"
        @click="setLevel(lv)"
        class="px-4 py-1.5 rounded-full text-xs font-semibold transition"
        :style="selectedLevel === lv
          ? 'background:#6366f1; color:#fff'
          : 'background-color:var(--color-surface-02); color:var(--color-text-muted); border:1px solid var(--color-surface-04)'"
      >{{ lv }}</button>
    </div>

    <!-- Enrollment notice -->
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
    <div v-if="loading" class="space-y-6">
      <div v-for="i in 3" :key="i" class="space-y-3">
        <div class="h-8 w-48 rounded-lg animate-pulse" style="background-color: var(--color-surface-02)"></div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div v-for="j in 3" :key="j" class="h-28 rounded-xl animate-pulse"
               style="background-color: var(--color-surface-02)"></div>
        </div>
      </div>
    </div>

    <!-- Content: chapter-grouped learning path -->
    <div v-else-if="chapters.length">
      <template v-for="(section, si) in displaySections" :key="section.level">

        <!-- Level header (only in "All" mode) -->
        <div v-if="selectedLevel === 'All'" class="flex items-center gap-3 mt-8 mb-4 first:mt-0">
          <span class="text-sm font-bold px-2.5 py-1 rounded-lg"
                :style="levelColor(section.level)">{{ section.level }}</span>
          <div class="flex-1 h-px" style="background: var(--color-surface-04)"></div>
          <span class="text-xs" :style="isLocked(section.level) ? 'color:var(--color-text-muted)' : 'color:#86efac'">
            {{ isLocked(section.level) ? '🔒 Chưa đăng ký' : '✓ Đã đăng ký' }}
          </span>
        </div>

        <!-- Chapters in this level -->
        <div v-for="(chapter, ci) in section.chapters" :key="chapter.name" class="mb-8">
          <!-- Chapter header -->
          <div class="flex items-center gap-3 mb-3">
            <div class="flex items-center justify-center w-8 h-8 rounded-lg text-sm font-bold"
                 style="background: rgba(99,102,241,0.15); color: #818cf8">
              {{ ci + 1 }}
            </div>
            <h2 class="font-bold text-base" style="color: var(--color-text-base)">
              {{ chapter.name || 'Chưa phân chương' }}
            </h2>
            <span class="text-xs px-2 py-0.5 rounded-full"
                  style="background: var(--color-surface-04); color: var(--color-text-muted)">
              {{ chapter.topics.length }} chủ điểm
            </span>
            <!-- Chapter progress -->
            <span v-if="chapter.completedCount > 0" class="ml-auto text-xs font-medium" style="color: #34d399">
              {{ chapter.completedCount }}/{{ chapter.topics.length }} ✓
            </span>
          </div>

          <!-- Topic nodes grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <component
              :is="isLocked(section.level) ? 'div' : 'RouterLink'"
              v-for="(topic, ti) in chapter.topics" :key="topic.id"
              :to="isLocked(section.level) ? undefined : { name: 'grammar-detail', params: { slug: topic.slug } }"
              class="group relative rounded-xl p-4 transition-all duration-200"
              :class="[
                isLocked(section.level)
                  ? 'cursor-not-allowed opacity-50'
                  : 'cursor-pointer hover:scale-[1.02] hover:shadow-lg'
              ]"
              :style="nodeStyle(topic, section.level)"
            >
              <!-- Status indicator -->
              <div class="absolute top-3 right-3">
                <span v-if="isLocked(section.level)" class="text-sm">🔒</span>
                <span v-else-if="isTopicCompleted(topic.slug)" class="text-sm">🟢</span>
                <span v-else class="text-sm">🔵</span>
              </div>

              <!-- Topic content -->
              <div class="flex items-start gap-3">
                <span class="text-2xl flex-shrink-0">{{ topic.icon || '📖' }}</span>
                <div class="flex-1 min-w-0">
                  <p class="font-semibold text-sm leading-tight mb-1" style="color: var(--color-text-base)">
                    {{ topic.title }}
                  </p>
                  <p v-if="topic.description" class="text-xs line-clamp-2" style="color: var(--color-text-muted)">
                    {{ topic.description }}
                  </p>
                </div>
              </div>

              <!-- Bottom row: rule count + quiz score -->
              <div class="flex items-center justify-between mt-3">
                <span class="text-xs" style="color: var(--color-text-muted)">
                  {{ topic.rule_count || 0 }} quy tắc
                </span>
                <span v-if="getQuizScore(topic.slug) !== null"
                      class="text-xs font-bold px-2 py-0.5 rounded-full"
                      :style="getQuizScore(topic.slug) >= 80
                        ? 'background:rgba(34,197,94,0.15);color:#86efac'
                        : 'background:rgba(251,191,36,0.15);color:#fbbf24'">
                  {{ getQuizScore(topic.slug) }}%
                </span>
              </div>

              <!-- Progress bar at bottom -->
              <div v-if="getQuizScore(topic.slug) !== null"
                   class="mt-2 h-1 rounded-full overflow-hidden"
                   style="background: var(--color-surface-04)">
                <div class="h-full rounded-full transition-all duration-500"
                     :style="`width:${getQuizScore(topic.slug)}%; background:${getQuizScore(topic.slug) >= 80 ? '#34d399' : '#fbbf24'}`"></div>
              </div>
            </component>
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
      <p>Chưa có chủ điểm ngữ pháp nào.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { grammarApi } from '@/api/curriculum.js'
import { useAuthStore } from '@/stores/auth.js'
import { useDashboardStore } from '@/stores/dashboard.js'

const LEVELS = ['All', 'A1', 'A2', 'B1', 'B2', 'C1']
const LEVEL_ORDER = { A1: 0, A2: 1, B1: 2, B2: 3, C1: 4, C2: 5 }

const auth = useAuthStore()
const dashboard = useDashboardStore()
const { isLoggedIn } = storeToRefs(auth)

// ── Data ─────────────────────────────────────────────────────────────────────
const topics      = ref([])
const progress    = ref({})    // { slug: { score, ... } }
const loading     = ref(false)
const loadingMore = ref(false)
const nextUrl     = ref(null)
const selectedLevel = ref('All')

// ── Unlock logic ─────────────────────────────────────────────────────────────
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

// ── Progress helpers ─────────────────────────────────────────────────────────
function getQuizScore(slug) {
  return progress.value[slug]?.score ?? null
}

function isTopicCompleted(slug) {
  const s = getQuizScore(slug)
  return s !== null && s >= 70
}

// ── Group topics by chapter ──────────────────────────────────────────────────
const chapters = computed(() => {
  const byLevel = new Map()

  for (const topic of topics.value) {
    if (!byLevel.has(topic.level)) byLevel.set(topic.level, new Map())
    const levelChapters = byLevel.get(topic.level)
    const chapterName = topic.chapter || ''
    if (!levelChapters.has(chapterName)) {
      levelChapters.set(chapterName, { name: chapterName, topics: [] })
    }
    levelChapters.get(chapterName).topics.push(topic)
  }

  const result = []
  for (const [level, chaptersMap] of byLevel) {
    const chs = [...chaptersMap.values()].map(ch => ({
      ...ch,
      completedCount: ch.topics.filter(t => isTopicCompleted(t.slug)).length,
    }))
    result.push({ level, chapters: chs })
  }

  return result.sort((a, b) => (LEVEL_ORDER[a.level] ?? 99) - (LEVEL_ORDER[b.level] ?? 99))
})

const displaySections = computed(() => chapters.value)

const hasMore = computed(() => !!nextUrl.value)

// ── Styling ──────────────────────────────────────────────────────────────────
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

function nodeStyle(topic, level) {
  if (isLocked(level)) {
    return 'background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04);'
  }
  if (isTopicCompleted(topic.slug)) {
    return 'background-color: var(--color-surface-02); border: 1px solid rgba(34,197,94,0.3);'
  }
  return 'background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04);'
}

// ── API calls ────────────────────────────────────────────────────────────────
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

async function fetchProgress() {
  if (!isLoggedIn.value) return
  try {
    const res = await grammarApi.getProgress()
    progress.value = res.data?.data ?? res.data ?? {}
  } catch {
    progress.value = {}
  }
}

async function loadMore() {
  if (!nextUrl.value || loadingMore.value) return
  loadingMore.value = true
  try {
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
  fetchTopics()
}

onMounted(async () => {
  await dashboard.fetch()
  fetchTopics()
  fetchProgress()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
