<template>
  <div class="space-y-6">

    <!-- Course list ─────────────────────────────────────────────────────── -->
    <template v-if="!selectedCourse">
      <div v-if="loadingCourses" class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="i in 6" :key="i"
          class="h-32 rounded-2xl animate-pulse"
          style="background-color: var(--color-surface-02)"
        />
      </div>

      <p v-else-if="!courses.length" class="text-center py-16" style="color: var(--color-text-muted)">
        Không có khoá học nào
      </p>

      <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <button
          v-for="course in courses"
          :key="course.id"
          @click="openCourse(course)"
          class="text-left rounded-2xl p-5 hover:-translate-y-0.5 transition group"
          style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
        >
          <!-- Level badge -->
          <span class="text-xs px-2 py-0.5 rounded-full font-bold mb-3 inline-block"
            :style="levelStyle(course.cefr_level)"
          >
            {{ course.cefr_level || 'N/A' }}
          </span>

          <p class="font-bold group-hover:text-[var(--color-primary-400)] transition text-base"
            style="color: var(--color-text-base)"
          >
            {{ course.title }}
          </p>

          <p class="text-xs mt-2 flex items-center gap-1.5" style="color: var(--color-text-muted)">
            <span>👥</span>
            <span>{{ course.student_count }} học viên</span>
          </p>
        </button>
      </div>
    </template>

    <!-- Student list ─────────────────────────────────────────────────────── -->
    <template v-else>
      <!-- Back header -->
      <div class="flex items-center gap-4">
        <button @click="selectedCourse = null"
          class="flex items-center gap-2 text-sm hover:opacity-80 transition"
          style="color: var(--color-text-muted)"
        >
          ← Quay lại
        </button>
        <div>
          <span class="text-xs px-2 py-0.5 rounded-full font-bold mr-2" :style="levelStyle(selectedCourse.cefr_level)">
            {{ selectedCourse.cefr_level }}
          </span>
          <span class="font-bold" style="color: var(--color-text-base)">{{ selectedCourse.title }}</span>
          <span class="text-xs ml-2" style="color: var(--color-text-muted)">
            ({{ selectedCourse.student_count }} học viên)
          </span>
        </div>
        <button
          @click="exportCsv"
          :disabled="exportingCsv"
          class="ml-auto flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold transition hover:opacity-90 disabled:opacity-50"
          style="background-color: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)"
        >
          <span>📥</span>
          {{ exportingCsv ? 'Đang xuất…' : 'Xuất CSV' }}
        </button>
      </div>

      <!-- Search -->
      <input
        v-model="studentSearch" type="search" placeholder="Tìm học viên…"
        class="w-full max-w-sm px-3 py-2 rounded-xl text-sm focus:outline-none"
        style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-text-base)"
      />

      <!-- Student table -->
      <div class="rounded-2xl overflow-hidden" style="border: 1px solid var(--color-surface-04)">
        <div v-if="loadingStudents" class="p-6 space-y-3">
          <div v-for="i in 5" :key="i" class="h-10 rounded-xl animate-pulse"
            style="background-color: var(--color-surface-02)"
          />
        </div>

        <table v-else class="w-full text-sm border-collapse">
          <thead>
            <tr style="background-color: var(--color-surface-03); color: var(--color-text-muted)">
              <th class="text-left px-4 py-3 font-semibold">Học viên</th>
              <th class="text-left px-4 py-3 font-semibold hidden sm:table-cell">Trình độ</th>
              <th class="text-left px-4 py-3 font-semibold">Tiến độ</th>
              <th class="text-left px-4 py-3 font-semibold hidden md:table-cell">Trạng thái</th>
              <th class="text-left px-4 py-3 font-semibold hidden lg:table-cell">Ngày đăng ký</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!filteredStudents.length">
              <td colspan="5" class="text-center py-10" style="color: var(--color-text-muted)">
                Không có học viên
              </td>
            </tr>
            <tr
              v-for="s in filteredStudents"
              :key="s.student_id"
              style="border-top: 1px solid var(--color-surface-04)"
            >
              <td class="px-4 py-3">
                <p class="font-medium" style="color: var(--color-text-base)">{{ s.student?.full_name || s.full_name }}</p>
                <p class="text-xs" style="color: var(--color-text-muted)">{{ s.student?.email || s.email }}</p>
              </td>
              <td class="px-4 py-3 hidden sm:table-cell">
                <span class="text-xs px-2 py-0.5 rounded-full font-bold" :style="levelStyle(s.student?.current_level || s.current_level)">
                  {{ s.student?.current_level || s.current_level || 'N/A' }}
                </span>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <div class="w-24 h-1.5 rounded-full overflow-hidden" style="background-color: var(--color-surface-04)">
                    <div class="h-full rounded-full" :style="`width: ${s.progress_percent ?? 0}%; background-color: var(--color-primary-500)`" />
                  </div>
                  <span class="text-xs" style="color: var(--color-text-muted)">{{ s.progress_percent ?? 0 }}%</span>
                </div>
              </td>
              <td class="px-4 py-3 hidden md:table-cell">
                <span class="text-xs px-2 py-0.5 rounded-full font-semibold"
                  :style="s.status === 'active'
                    ? 'background-color:color-mix(in srgb,#4ade80 15%,transparent);color:#4ade80'
                    : 'background-color:color-mix(in srgb,#94a3b8 15%,transparent);color:#94a3b8'"
                >
                  {{ s.status === 'active' ? 'Đang học' : s.status }}
                </span>
              </td>
              <td class="px-4 py-3 hidden lg:table-cell text-xs" style="color: var(--color-text-muted)">
                {{ fmtDate(s.enrolled_at) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { teacherApi } from '@/api/teacher.js'

const loadingCourses  = ref(false)
const loadingStudents = ref(false)
const exportingCsv    = ref(false)
const courses         = ref([])
const students        = ref([])
const selectedCourse  = ref(null)
const studentSearch   = ref('')

// ── Helpers ────────────────────────────────────────────────────────────────
function fmtDate(iso) {
  if (!iso) return '—'
  return new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(new Date(iso))
}

const LEVEL_STYLES = {
  A1: 'background-color:color-mix(in srgb,#86efac 20%,transparent);color:#4ade80',
  A2: 'background-color:color-mix(in srgb,#86efac 20%,transparent);color:#4ade80',
  B1: 'background-color:color-mix(in srgb,#93c5fd 20%,transparent);color:#60a5fa',
  B2: 'background-color:color-mix(in srgb,#93c5fd 20%,transparent);color:#60a5fa',
  C1: 'background-color:color-mix(in srgb,#c4b5fd 20%,transparent);color:#a78bfa',
  C2: 'background-color:color-mix(in srgb,#c4b5fd 20%,transparent);color:#a78bfa',
}
function levelStyle(lvl) {
  return LEVEL_STYLES[lvl?.toUpperCase()] ?? 'background-color:color-mix(in srgb,#94a3b8 15%,transparent);color:#94a3b8'
}

// ── Data ──────────────────────────────────────────────────────────────────
async function loadCourses() {
  loadingCourses.value = true
  try {
    const res = await teacherApi.getClasses()
    courses.value = res.data?.data ?? res.data?.results ?? res.data ?? []
  } catch { courses.value = [] }
  finally { loadingCourses.value = false }
}

async function openCourse(course) {
  selectedCourse.value = course
  studentSearch.value = ''
  loadingStudents.value = true
  try {
    const res = await teacherApi.getClassStudents(course.id)
    students.value = res.data?.data ?? res.data?.results ?? res.data ?? []
  } catch { students.value = [] }
  finally { loadingStudents.value = false }
}

const filteredStudents = computed(() => {
  const q = studentSearch.value.toLowerCase().trim()
  if (!q) return students.value
  return students.value.filter(s =>
    s.full_name?.toLowerCase().includes(q) ||
    s.email?.toLowerCase().includes(q)
  )
})

async function exportCsv() {
  if (!selectedCourse.value) return
  exportingCsv.value = true
  try {
    const res = await teacherApi.exportClass(selectedCourse.value.id)
    const url = URL.createObjectURL(new Blob([res.data], { type: 'text/csv' }))
    const a = document.createElement('a')
    a.href = url
    a.download = `class_${selectedCourse.value.id}_students.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    alert('Xuất CSV thất bại, vui lòng thử lại.')
  } finally {
    exportingCsv.value = false
  }
}

onMounted(loadCourses)
</script>
