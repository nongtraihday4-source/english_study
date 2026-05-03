<template>
  <div class="space-y-6">

    <!-- Header + Create button ───────────────────────────────────────────── -->
    <div class="flex items-center justify-between gap-4">
      <div>
        <h2 class="text-lg font-bold" style="color: var(--color-text-base)">📋 Bài tập giao</h2>
        <p class="text-xs mt-0.5" style="color: var(--color-text-muted)">
          Tạo và quản lý bài tập cho học viên
        </p>
      </div>
      <button
        @click="openModal()"
        class="px-4 py-2 rounded-xl text-sm font-bold text-white hover:opacity-90 transition"
        style="background: linear-gradient(135deg, #4f46e5, #7c3aed)"
      >
        + Tạo bài tập
      </button>
    </div>

    <!-- Filters ──────────────────────────────────────────────────────────── -->
    <div class="flex flex-wrap gap-3">
      <select
        v-model="filterCourse"
        @change="load"
        class="px-3 py-2 rounded-xl text-sm border"
        style="background-color: var(--color-surface-02); color: var(--color-text-base); border-color: var(--color-surface-04)"
      >
        <option value="">Tất cả khoá học</option>
        <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.title }}</option>
      </select>

      <select
        v-model="filterActive"
        @change="load"
        class="px-3 py-2 rounded-xl text-sm border"
        style="background-color: var(--color-surface-02); color: var(--color-text-base); border-color: var(--color-surface-04)"
      >
        <option value="">Tất cả trạng thái</option>
        <option value="true">Đang hoạt động</option>
        <option value="false">Đã tắt</option>
      </select>
    </div>

    <!-- Loading skeleton ─────────────────────────────────────────────────── -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 4" :key="i"
        class="h-16 rounded-2xl animate-pulse"
        style="background-color: var(--color-surface-02)"
      />
    </div>

    <!-- Empty state ──────────────────────────────────────────────────────── -->
    <div v-else-if="!assignments.length"
      class="rounded-2xl py-16 text-center"
      style="background-color: var(--color-surface-02)"
    >
      <p class="text-4xl mb-3">📭</p>
      <p class="text-sm" style="color: var(--color-text-muted)">Chưa có bài tập nào. Nhấn "+ Tạo bài tập" để bắt đầu.</p>
    </div>

    <!-- Assignment cards ─────────────────────────────────────────────────── -->
    <div v-else class="space-y-3">
      <div
        v-for="a in assignments"
        :key="a.id"
        class="rounded-2xl p-4"
        style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span
                class="text-xs px-2 py-0.5 rounded-full font-semibold"
                :style="a.is_active
                  ? 'background-color: rgba(34,197,94,0.15); color: #22c55e'
                  : 'background-color: var(--color-surface-04); color: var(--color-text-muted)'"
              >
                {{ a.is_active ? 'Đang bật' : 'Đã tắt' }}
              </span>
              <span class="text-xs" style="color: var(--color-text-muted)">
                Đến: {{ fmtDate(a.due_date) }}
                <span
                  v-if="isOverdue(a.due_date) && a.is_active"
                  class="ml-1 text-red-400 font-semibold"
                >⚠ Quá hạn</span>
              </span>
            </div>

            <p class="font-semibold truncate" style="color: var(--color-text-base)">
              {{ a.title }}
            </p>
            <p v-if="a.description" class="text-xs mt-0.5 truncate" style="color: var(--color-text-muted)">
              {{ a.description }}
            </p>

            <div class="flex flex-wrap gap-x-4 gap-y-1 mt-2 text-xs" style="color: var(--color-text-soft)">
              <span>📚 {{ a.course_title }}</span>
              <span>📝 {{ a.exam_set_title }}</span>
              <span>{{ a.assign_to_all ? '👥 Toàn bộ học viên' : '👤 Học viên chỉ định' }}</span>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2 shrink-0">
            <button
              @click="viewSubmissions(a)"
              class="px-3 py-1.5 rounded-lg text-xs font-medium hover:opacity-80 transition"
              style="background-color: var(--color-surface-04); color: var(--color-text-base)"
            >
              Xem bài nộp
            </button>
            <button
              @click="openModal(a)"
              class="px-3 py-1.5 rounded-lg text-xs font-medium hover:opacity-80 transition"
              style="background-color: color-mix(in srgb,#6366f1 20%,transparent); color: #818cf8"
            >
              Sửa
            </button>
            <button
              @click="deactivate(a)"
              class="px-3 py-1.5 rounded-lg text-xs font-medium hover:opacity-80 transition"
              style="background-color: color-mix(in srgb,#ef4444 15%,transparent); color: #f87171"
              :disabled="!a.is_active"
            >
              Tắt
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Submissions panel (slide-in) ─────────────────────────────────────── -->
    <Teleport to="body">
      <div v-if="subPanel.show"
        class="fixed inset-0 z-40 flex justify-end"
        @click.self="subPanel.show = false"
        style="background-color: rgba(0,0,0,0.45)"
      >
        <div class="w-full max-w-lg h-full overflow-y-auto p-6 shadow-2xl"
          style="background-color: var(--color-surface-01)"
        >
          <div class="flex items-center justify-between mb-6">
            <div>
              <p class="text-xs uppercase tracking-wider mb-1" style="color: var(--color-text-muted)">Bài nộp</p>
              <h3 class="font-bold" style="color: var(--color-text-base)">{{ subPanel.title }}</h3>
            </div>
            <button @click="subPanel.show = false" class="text-2xl leading-none hover:opacity-70 transition"
              style="color: var(--color-text-muted)">&times;</button>
          </div>

          <div v-if="subPanel.loading" class="space-y-2">
            <div v-for="i in 5" :key="i" class="h-10 rounded-xl animate-pulse"
              style="background-color: var(--color-surface-02)" />
          </div>

          <div v-else-if="!subPanel.results.length" class="text-center py-12 text-sm" style="color: var(--color-text-muted)">
            Chưa có học viên nào
          </div>

          <div v-else>
            <p class="text-xs mb-3" style="color: var(--color-text-muted)">
              {{ subPanel.results.length }} học viên được giao
            </p>
            <div class="space-y-2">
              <div
                v-for="s in subPanel.results"
                :key="s.student_id"
                class="flex items-center gap-3 rounded-xl px-4 py-3"
                style="background-color: var(--color-surface-02)"
              >
                <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0"
                  style="background-color: var(--color-surface-04); color: var(--color-primary-400)"
                >
                  {{ s.student_name.charAt(0).toUpperCase() }}
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium truncate" style="color: var(--color-text-base)">{{ s.student_name }}</p>
                  <p class="text-xs truncate" style="color: var(--color-text-muted)">{{ s.student_email }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Create / Edit modal ──────────────────────────────────────────────── -->
    <Teleport to="body">
      <div v-if="modal.show"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        style="background-color: rgba(0,0,0,0.6)"
      >
        <div class="w-full max-w-lg rounded-2xl p-6 shadow-2xl"
          style="background-color: var(--color-surface-01)"
        >
          <!-- Modal header -->
          <div class="flex items-center justify-between mb-6">
            <h3 class="font-bold" style="color: var(--color-text-base)">
              {{ modal.editId ? 'Sửa bài tập' : 'Tạo bài tập mới' }}
            </h3>
            <button @click="modal.show = false" class="text-2xl leading-none hover:opacity-70 transition"
              style="color: var(--color-text-muted)">&times;</button>
          </div>

          <!-- Form -->
          <div class="space-y-4">
            <!-- Title -->
            <div>
              <label class="block text-xs font-semibold mb-1.5" style="color: var(--color-text-soft)">Tiêu đề *</label>
              <input
                v-model="form.title"
                type="text"
                placeholder="Ví dụ: Bài tập tuần 3 – Unit 5"
                class="w-full px-3 py-2.5 rounded-xl text-sm border focus:outline-none"
                style="background-color: var(--color-surface-02); color: var(--color-text-base); border-color: var(--color-surface-04)"
              />
            </div>

            <!-- Description -->
            <div>
              <label class="block text-xs font-semibold mb-1.5" style="color: var(--color-text-soft)">Mô tả</label>
              <textarea
                v-model="form.description"
                rows="2"
                placeholder="Hướng dẫn cho học viên (tuỳ chọn)"
                class="w-full px-3 py-2.5 rounded-xl text-sm border focus:outline-none resize-none"
                style="background-color: var(--color-surface-02); color: var(--color-text-base); border-color: var(--color-surface-04)"
              />
            </div>

            <!-- Course -->
            <div>
              <label class="block text-xs font-semibold mb-1.5" style="color: var(--color-text-soft)">Khoá học *</label>
              <select
                v-model="form.course"
                class="w-full px-3 py-2.5 rounded-xl text-sm border focus:outline-none"
                style="background-color: var(--color-surface-02); color: var(--color-text-base); border-color: var(--color-surface-04)"
              >
                <option value="" disabled>Chọn khoá học…</option>
                <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.title }}</option>
              </select>
            </div>

            <!-- Exam set -->
            <div>
              <label class="block text-xs font-semibold mb-1.5" style="color: var(--color-text-soft)">Bộ đề *</label>
              <select
                v-model="form.exam_set"
                class="w-full px-3 py-2.5 rounded-xl text-sm border focus:outline-none"
                style="background-color: var(--color-surface-02); color: var(--color-text-base); border-color: var(--color-surface-04)"
              >
                <option value="" disabled>Chọn bộ đề…</option>
                <option v-for="e in examSets" :key="e.id" :value="e.id">{{ e.title }}</option>
              </select>
            </div>

            <!-- Due date -->
            <div>
              <label class="block text-xs font-semibold mb-1.5" style="color: var(--color-text-soft)">Hạn nộp *</label>
              <input
                v-model="form.due_date"
                type="datetime-local"
                class="w-full px-3 py-2.5 rounded-xl text-sm border focus:outline-none"
                style="background-color: var(--color-surface-02); color: var(--color-text-base); border-color: var(--color-surface-04)"
              />
            </div>

            <!-- Assign to all toggle -->
            <label class="flex items-center gap-3 cursor-pointer select-none">
              <div
                @click="form.assign_to_all = !form.assign_to_all"
                class="w-11 h-6 rounded-full transition-colors relative shrink-0"
                :style="form.assign_to_all
                  ? 'background-color: var(--color-primary-600)'
                  : 'background-color: var(--color-surface-04)'"
              >
                <span
                  class="absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform"
                  :style="form.assign_to_all ? 'transform: translateX(20px)' : ''"
                />
              </div>
              <span class="text-sm" style="color: var(--color-text-base)">
                Giao cho toàn bộ học viên trong khoá
              </span>
            </label>
          </div>

          <!-- Footer buttons -->
          <div class="flex items-center justify-end gap-3 mt-6 pt-4 border-t" style="border-color: var(--color-surface-04)">
            <button
              @click="modal.show = false"
              class="px-4 py-2 rounded-xl text-sm font-medium hover:opacity-80 transition"
              style="background-color: var(--color-surface-04); color: var(--color-text-base)"
            >
              Huỷ
            </button>
            <button
              @click="save"
              :disabled="saving"
              class="px-5 py-2 rounded-xl text-sm font-bold text-white hover:opacity-90 transition disabled:opacity-50"
              style="background: linear-gradient(135deg, #4f46e5, #7c3aed)"
            >
              {{ saving ? 'Đang lưu…' : (modal.editId ? 'Cập nhật' : 'Tạo bài tập') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { teacherApi } from '@/api/teacher.js'
import { adminApi } from '@/api/admin.js'

// ── State ──────────────────────────────────────────────────────────────────
const loading       = ref(false)
const saving        = ref(false)
const assignments   = ref([])
const courses       = ref([])
const examSets      = ref([])
const filterCourse  = ref('')
const filterActive  = ref('')

const modal = reactive({ show: false, editId: null })
const form  = reactive({
  title: '', description: '', course: '', exam_set: '',
  due_date: '', assign_to_all: true,
})

const subPanel = reactive({
  show: false, loading: false, title: '', results: []
})

// ── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([load(), loadCourses(), loadExamSets()])
})

// ── Data loaders ───────────────────────────────────────────────────────────
async function load() {
  loading.value = true
  const params = {}
  if (filterCourse.value) params.course_id = filterCourse.value
  if (filterActive.value !== '') params.is_active = filterActive.value
  try {
    const res = await teacherApi.getAssignments(params)
    assignments.value = res.data?.results ?? res.data ?? []
  } catch (e) {
    console.error('load assignments', e)
  } finally {
    loading.value = false
  }
}

async function loadCourses() {
  try {
    const res = await teacherApi.getClasses()
    courses.value = res.data?.results ?? res.data ?? []
  } catch (e) {
    console.error('load courses', e)
  }
}

async function loadExamSets() {
  try {
    const res = await adminApi.getExamSets({ page_size: 200 })
    examSets.value = res.data?.results ?? res.data ?? []
  } catch (e) {
    console.error('load exam sets', e)
  }
}

// ── Modal helpers ──────────────────────────────────────────────────────────
function openModal(a = null) {
  if (a) {
    modal.editId      = a.id
    form.title        = a.title
    form.description  = a.description || ''
    form.course       = a.course
    form.exam_set     = a.exam_set
    form.due_date     = a.due_date ? a.due_date.slice(0, 16) : ''
    form.assign_to_all = a.assign_to_all
  } else {
    modal.editId      = null
    form.title        = ''
    form.description  = ''
    form.course       = courses.value[0]?.id ?? ''
    form.exam_set     = ''
    form.due_date     = ''
    form.assign_to_all = true
  }
  modal.show = true
}

async function save() {
  if (!form.title.trim() || !form.course || !form.exam_set || !form.due_date) {
    alert('Vui lòng điền đầy đủ tiêu đề, khoá học, bộ đề và hạn nộp.')
    return
  }
  saving.value = true
  const payload = {
    title:         form.title.trim(),
    description:   form.description.trim(),
    course:        form.course,
    exam_set:      form.exam_set,
    due_date:      new Date(form.due_date).toISOString(),
    assign_to_all: form.assign_to_all,
    is_active:     true,
  }
  try {
    if (modal.editId) {
      await teacherApi.updateAssignment(modal.editId, payload)
    } else {
      await teacherApi.createAssignment(payload)
    }
    modal.show = false
    await load()
  } catch (e) {
    alert(e.response?.data?.detail || 'Lỗi khi lưu bài tập.')
  } finally {
    saving.value = false
  }
}

async function deactivate(a) {
  if (!confirm(`Tắt bài tập "${a.title}"?`)) return
  try {
    await teacherApi.deleteAssignment(a.id)
    await load()
  } catch (e) {
    alert('Lỗi khi tắt bài tập.')
  }
}

async function viewSubmissions(a) {
  subPanel.title   = a.title
  subPanel.results = []
  subPanel.show    = true
  subPanel.loading = true
  try {
    const res = await teacherApi.getAssignmentSubmissions(a.id)
    subPanel.results = res.data?.results ?? []
  } catch (e) {
    console.error('load submissions', e)
  } finally {
    subPanel.loading = false
  }
}

// ── Utils ──────────────────────────────────────────────────────────────────
function fmtDate(val) {
  if (!val) return '—'
  return new Intl.DateTimeFormat('vi-VN', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
    timeZone: 'Asia/Ho_Chi_Minh'
  }).format(new Date(val))
}

function isOverdue(due) {
  return due && new Date(due) < new Date()
}
</script>
