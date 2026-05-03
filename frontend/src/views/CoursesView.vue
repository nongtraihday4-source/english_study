<template>
    <div class="p-6">
      <h1 class="text-2xl font-bold mb-1" style="color: var(--color-text-base)">Khoá học</h1>
      <p class="text-sm mb-6" style="color: var(--color-text-muted)">Chọn khoá học phù hợp với trình độ của bạn</p>

      <!-- Filters -->
      <div class="flex flex-wrap gap-2 mb-6">
        <button v-for="level in cefrLevels" :key="level"
                @click="activeLevel = activeLevel === level ? '' : level"
                class="px-3 py-1.5 rounded-lg text-xs font-semibold transition"
                :style="activeLevel === level
                  ? 'background-color: var(--color-primary-600); color: white'
                  : 'background-color: var(--color-surface-03); color: var(--color-text-soft)'">
          {{ level }}
        </button>
      </div>

      <!-- Content -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="i in 6" :key="i" class="rounded-2xl h-48 animate-pulse"
             style="background-color: var(--color-surface-02)"></div>
      </div>

      <div v-else-if="error" class="text-center py-16" style="color: var(--color-text-muted)">
        <p class="text-4xl mb-3">⚠️</p>
        <p>{{ error }}</p>
        <button @click="loadCourses" class="mt-4 px-4 py-2 rounded-lg text-sm transition hover:opacity-80"
                style="background-color: var(--color-primary-600); color: white">Thử lại</button>
      </div>

      <div v-else-if="courses.length === 0" class="text-center py-16" style="color: var(--color-text-muted)">
        <p class="text-4xl mb-3">📚</p>
        <p>Không có khoá học nào phù hợp.</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <RouterLink v-for="course in filteredCourses" :key="course.id"
                    :to="`/courses/${course.id}`"
                    class="rounded-2xl p-5 flex flex-col gap-3 transition hover:scale-[1.02]"
                    style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); text-decoration: none">
          <div class="flex items-center justify-between">
            <span class="px-2 py-0.5 rounded text-xs font-bold"
                  :style="levelBadgeStyle(course.level?.code)">
              {{ course.level?.code || course.level }}
            </span>
            <span class="text-xs" style="color: var(--color-text-muted)">{{ course.total_lessons }} bài</span>
          </div>
          <div>
            <h3 class="font-bold text-base" style="color: var(--color-text-base)">{{ course.title }}</h3>
            <p class="text-xs mt-1 text-[10px] font-semibold" :style="levelBadgeStyle(course.level?.code)" style="background:none;padding:0">
              {{ course.level?.name_vi || course.level?.name }}
            </p>
            <p class="text-xs mt-1 line-clamp-2" style="color: var(--color-text-muted)">{{ course.description }}</p>
          </div>
          <div class="mt-auto">
            <div class="w-full h-1.5 rounded-full overflow-hidden" style="background-color: var(--color-surface-04)">
              <div class="h-full rounded-full transition-all"
                   :style="`width: ${course.progress_percent || 0}%; background: linear-gradient(90deg, #6366f1, #8b5cf6)`"></div>
            </div>
            <p class="text-xs mt-1" style="color: var(--color-text-muted)">{{ course.progress_percent || 0 }}% hoàn thành</p>
          </div>
        </RouterLink>
      </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getCourses } from '@/api/curriculum.js'

const cefrLevels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const activeLevel = ref('')
const courses = ref([])
const loading = ref(false)
const error = ref('')

const filteredCourses = computed(() =>
  activeLevel.value
    ? courses.value.filter(c => (c.level?.code || c.level) === activeLevel.value)
    : courses.value
)

function levelBadgeStyle(code) {
  const map = {
    A1: 'background:#d1fae5; color:#065f46',
    A2: 'background:#dbeafe; color:#1e40af',
    B1: 'background:#ede9fe; color:#4c1d95',
    B2: 'background:#fef3c7; color:#92400e',
    C1: 'background:#fee2e2; color:#991b1b',
    C2: 'background:#fce7f3; color:#831843',
  }
  return map[code] || 'background:var(--color-surface-04); color:var(--color-text-muted)'
}

async function loadCourses() {
  loading.value = true
  error.value = ''
  try {
    const res = await getCourses()
    const d = res.data?.data ?? res.data
    courses.value = d?.results || (Array.isArray(d) ? d : [])
  } catch (e) {
    error.value = 'Không thể tải danh sách khoá học.'
  } finally {
    loading.value = false
  }
}

onMounted(loadCourses)
</script>
