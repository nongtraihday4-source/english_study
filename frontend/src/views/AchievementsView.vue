<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold" style="color: var(--color-text-base)">🏅 Thành tựu</h1>
      <p class="mt-1" style="color: var(--color-text-muted)">
        Bạn đã đạt được
        <span class="font-semibold text-indigo-600 dark:text-indigo-400">{{ earnedCount }}</span>
        /
        <span class="font-semibold">{{ allAchievements.length }}</span>
        thành tựu
      </p>

      <!-- Progress bar -->
      <div class="mt-3 h-2 w-full max-w-md rounded-full" style="background-color: var(--color-border)">
        <div
          class="h-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-700"
          :style="{ width: progressPct + '%' }"
        />
      </div>
    </div>

    <!-- Category tabs -->
    <div class="mb-6 flex flex-wrap gap-2">
      <button
        v-for="cat in categories"
        :key="cat.value"
        @click="activeCategory = cat.value"
        :class="[
          'rounded-full px-4 py-1.5 text-sm font-medium transition-colors',
          activeCategory === cat.value
            ? 'bg-indigo-600 text-white shadow'
            : 'bg-white text-gray-600 hover:bg-indigo-50 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700',
        ]"
        :style="activeCategory !== cat.value ? { backgroundColor: 'var(--color-surface)', color: 'var(--color-text-muted)' } : {}"
      >
        {{ cat.label }}
        <span class="ml-1 text-xs opacity-70">({{ countForCategory(cat.value) }})</span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-24">
      <div class="h-10 w-10 animate-spin rounded-full border-4 border-indigo-300 border-t-indigo-600" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="rounded-xl bg-red-50 dark:bg-red-900/20 p-6 text-center text-red-600 dark:text-red-400">
      {{ error }}
    </div>

    <!-- Achievement grid -->
    <div v-else class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
      <div
        v-for="ach in filteredAchievements"
        :key="ach.id"
        :class="[
          'group relative flex flex-col items-center rounded-2xl border-2 p-5 text-center transition-transform hover:-translate-y-0.5',
          ach.earned
            ? 'border-indigo-300 dark:border-indigo-500 shimmer-card'
            : 'border-gray-200 dark:border-gray-700 opacity-50 grayscale',
        ]"
        :style="{ backgroundColor: 'var(--color-surface)' }"
      >
        <!-- Earned glow ring -->
        <div
          v-if="ach.earned"
          class="absolute inset-0 rounded-2xl ring-2 ring-indigo-400 ring-offset-2 opacity-60 dark:ring-offset-gray-800"
        />

        <!-- Emoji -->
        <div class="relative z-10 text-5xl leading-none mb-3">{{ ach.icon_emoji }}</div>

        <!-- Name -->
        <h3 class="relative z-10 text-sm font-semibold leading-tight" style="color: var(--color-text-base)">
          {{ ach.name_vi }}
        </h3>

        <!-- Description (tooltip on hover for unearned) -->
        <p class="relative z-10 mt-1 text-xs line-clamp-2" style="color: var(--color-text-muted)">
          {{ ach.description }}
        </p>

        <!-- XP badge -->
        <span class="relative z-10 mt-2 inline-flex items-center gap-0.5 rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-bold text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-400">
          ⚡ {{ ach.xp_reward }} XP
        </span>

        <!-- Earned date -->
        <p v-if="ach.earned" class="relative z-10 mt-2 text-xs font-medium text-indigo-600 dark:text-indigo-400">
          ✓ {{ formatDate(ach.earned_at) }}
        </p>

        <!-- Threshold hint for unearned -->
        <p v-else class="relative z-10 mt-2 text-xs text-gray-400 dark:text-gray-500">
          Mục tiêu: {{ ach.threshold_value }}
        </p>
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-if="!loading && !error && filteredAchievements.length === 0"
      class="mt-10 text-center"
      style="color: var(--color-text-muted)"
    >
      <p class="text-4xl">🏜️</p>
      <p class="mt-2">Không có thành tựu nào trong mục này.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { gamificationApi } from '@/api/gamification'

const allAchievements = ref([])
const earnedMap = ref({})     // achievement_id → earned_at
const loading = ref(true)
const error = ref(null)
const activeCategory = ref('all')

const categories = [
  { value: 'all',    label: 'Tất cả' },
  { value: 'streak', label: 'Streak 🔥' },
  { value: 'skill',  label: 'Kỹ năng 🎯' },
  { value: 'level',  label: 'Cấp độ ⭐' },
  { value: 'social', label: 'Cộng đồng 🏆' },
]

const enrichedAchievements = computed(() =>
  allAchievements.value.map((a) => ({
    ...a,
    earned: earnedMap.value.hasOwnProperty(a.id),
    earned_at: earnedMap.value[a.id] ?? null,
  }))
)

const filteredAchievements = computed(() => {
  if (activeCategory.value === 'all') return enrichedAchievements.value
  return enrichedAchievements.value.filter((a) => a.category === activeCategory.value)
})

const earnedCount = computed(() => Object.keys(earnedMap.value).length)

const progressPct = computed(() =>
  allAchievements.value.length ? (earnedCount.value / allAchievements.value.length) * 100 : 0
)

function countForCategory(cat) {
  if (cat === 'all') return enrichedAchievements.value.filter((a) => a.earned).length + '/' + allAchievements.value.length
  const in_cat = enrichedAchievements.value.filter((a) => a.category === cat)
  return in_cat.filter((a) => a.earned).length + '/' + in_cat.length
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

onMounted(async () => {
  try {
    const [achRes, myRes] = await Promise.all([
      gamificationApi.getAchievements(),
      gamificationApi.getMyAchievements(),
    ])
    const achData = achRes.data?.data ?? achRes.data
    const myData = myRes.data?.data ?? myRes.data
    allAchievements.value = Array.isArray(achData) ? achData : []
    earnedMap.value = {}
    ;(Array.isArray(myData) ? myData : []).forEach((ua) => {
      earnedMap.value[ua.achievement.id] = ua.earned_at
    })
  } catch (e) {
    error.value = 'Không thể tải dữ liệu thành tựu. Vui lòng thử lại.'
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
@keyframes shimmer-border {
  0% { box-shadow: 0 0 0 2px #6366f1, 0 0 0 4px transparent; }
  50% { box-shadow: 0 0 0 2px #a855f7, 0 0 12px 4px #a855f755; }
  100% { box-shadow: 0 0 0 2px #6366f1, 0 0 0 4px transparent; }
}

.shimmer-card {
  animation: shimmer-border 2.5s ease-in-out infinite;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
