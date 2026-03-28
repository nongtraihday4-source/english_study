<template>
  <div class="space-y-5">
    <!-- Header -->
    <div>
      <h2 class="text-xl font-bold" style="color: var(--color-text-base)">Quản lý nội dung</h2>
      <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">Khoá học, chương và bài học</p>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 p-1 rounded-xl w-fit" style="background-color: var(--color-surface-02)">
      <button
        v-for="tab in TABS"
        :key="tab.id"
        class="px-4 py-2 rounded-lg text-sm font-medium transition"
        :style="activeTab === tab.id
          ? 'background-color:var(--color-primary-600);color:#fff'
          : 'color:var(--color-text-muted)'"
        @click="activeTab = tab.id"
      >{{ tab.label }}</button>
    </div>

    <!-- ─── COURSES TAB ──────────────────────────────────────────────────────── -->
    <template v-if="activeTab === 'courses'">
      <div class="flex justify-end">
        <button
          class="px-4 py-2 rounded-xl text-sm font-semibold transition hover:opacity-90"
          style="background-color: var(--color-primary-500); color: #fff"
          @click="openCourseForm()"
        >+ Thêm khoá học</button>
      </div>

      <div class="rounded-2xl overflow-hidden border" style="border-color: var(--color-surface-04)">
        <div v-if="coursesLoading" class="p-8 text-center text-sm" style="color: var(--color-text-muted)">
          Đang tải...
        </div>
        <div v-else-if="!courses.length" class="p-8 text-center text-sm" style="color: var(--color-text-muted)">
          Chưa có khoá học nào.
        </div>
        <table v-else class="w-full text-sm border-collapse">
          <thead>
            <tr style="background-color: var(--color-surface-02); border-bottom: 1px solid var(--color-surface-04)">
              <th class="text-left px-4 py-3 font-semibold" style="color: var(--color-text-muted)">Tên khoá học</th>
              <th class="text-left px-4 py-3 font-semibold" style="color: var(--color-text-muted)">Cấp độ</th>
              <th class="text-left px-4 py-3 font-semibold hidden sm:table-cell" style="color: var(--color-text-muted)">Học viên</th>
              <th class="text-left px-4 py-3 font-semibold hidden md:table-cell" style="color: var(--color-text-muted)">Loại</th>
              <th class="text-left px-4 py-3 font-semibold" style="color: var(--color-text-muted)">Trạng thái</th>
              <th class="text-right px-4 py-3 font-semibold" style="color: var(--color-text-muted)">Thao tác</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="course in courses"
              :key="course.id"
              class="border-t transition cursor-pointer hover:opacity-90"
              style="border-color: var(--color-surface-04); background-color: var(--color-surface-01)"
              @click="selectCourse(course)"
            >
              <td class="px-4 py-3 font-medium" style="color: var(--color-text-base)">{{ course.title }}</td>
              <td class="px-4 py-3">
                <span
                  class="text-xs px-2 py-0.5 rounded-full font-semibold"
                  style="background-color:color-mix(in srgb,var(--color-primary-600) 18%,transparent);color:var(--color-primary-400)"
                >{{ course.cefr_level }}</span>
              </td>
              <td class="px-4 py-3 hidden sm:table-cell text-xs" style="color: var(--color-text-muted)">
                {{ course.student_count }} học viên
              </td>
              <td class="px-4 py-3 hidden md:table-cell">
                <span
                  class="text-xs px-2 py-0.5 rounded-full font-medium"
                  :style="course.is_premium
                    ? 'background-color:color-mix(in srgb,#eab308 18%,transparent);color:#facc15'
                    : 'background-color:var(--color-surface-03);color:var(--color-text-muted)'"
                >{{ course.is_premium ? 'Premium' : 'Miễn phí' }}</span>
              </td>
              <td class="px-4 py-3">
                <span
                  class="text-xs px-2 py-0.5 rounded-full font-medium"
                  :style="course.is_active
                    ? 'background-color:color-mix(in srgb,#22c55e 18%,transparent);color:#4ade80'
                    : 'background-color:color-mix(in srgb,#ef4444 18%,transparent);color:#f87171'"
                >{{ course.is_active ? 'Hiển thị' : 'Ẩn' }}</span>
              </td>
              <td class="px-4 py-3 text-right" @click.stop>
                <button
                  class="text-xs px-2 py-1 rounded-lg mr-1 transition hover:opacity-80"
                  style="background-color:color-mix(in srgb,var(--color-primary-600) 18%,transparent);color:var(--color-primary-400)"
                  @click="openCourseForm(course)"
                >Sửa</button>
                <button
                  class="text-xs px-2 py-1 rounded-lg transition hover:opacity-80"
                  style="background-color:color-mix(in srgb,#ef4444 16%,transparent);color:#f87171"
                  @click="confirmDeleteCourse(course)"
                >Xoá</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Selected course: show chapters/lessons drill-down -->
      <div v-if="selectedCourse" class="rounded-2xl p-5 space-y-4" style="background-color: var(--color-surface-02)">
        <div class="flex items-center justify-between">
          <h3 class="font-semibold text-sm" style="color: var(--color-text-base)">
            📚 {{ selectedCourse.title }} — Chương học
          </h3>
          <button class="text-xs" style="color: var(--color-text-muted)" @click="selectedCourse = null">
            ✕ Đóng
          </button>
        </div>

        <div v-if="chaptersLoading" class="text-sm text-center py-4" style="color: var(--color-text-muted)">Đang tải...</div>
        <div v-else-if="!chapters.length" class="text-sm text-center py-4" style="color: var(--color-text-muted)">
          Chưa có chương nào.
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="ch in chapters"
            :key="ch.id"
            class="rounded-xl overflow-hidden border"
            style="border-color: var(--color-surface-04)"
          >
            <button
              class="w-full flex items-center justify-between px-4 py-3 text-sm font-medium transition hover:opacity-80"
              style="background-color: var(--color-surface-03); color: var(--color-text-base)"
              @click="toggleChapter(ch)"
            >
              <span>{{ ch.order }}. {{ ch.title }}</span>
              <span class="text-xs ml-2" style="color: var(--color-text-muted)">
                {{ ch.lesson_count }} bài · {{ expandedChapter === ch.id ? '▲' : '▼' }}
              </span>
            </button>

            <div v-if="expandedChapter === ch.id" class="divide-y" style="border-color: var(--color-surface-04)">
              <div v-if="lessonsLoading" class="px-4 py-3 text-xs" style="color: var(--color-text-muted)">Đang tải...</div>
              <div
                v-for="lesson in lessons[ch.id] || []"
                :key="lesson.id"
                class="flex items-center gap-3 px-4 py-2.5 text-xs"
                style="background-color: var(--color-surface-01); color: var(--color-text-base)"
              >
                <span>{{ lessonTypeIcon(lesson.lesson_type) }}</span>
                <span class="flex-1">{{ lesson.order }}. {{ lesson.title }}</span>
                <span style="color: var(--color-text-muted)">{{ lesson.estimated_minutes }}p</span>
                <span
                  class="px-1.5 py-0.5 rounded-full"
                  :style="lesson.is_active
                    ? 'background-color:color-mix(in srgb,#22c55e 15%,transparent);color:#4ade80'
                    : 'background-color:color-mix(in srgb,#ef4444 15%,transparent);color:#f87171'"
                >{{ lesson.is_active ? '✓' : '✕' }}</span>
              </div>
              <div v-if="!(lessons[ch.id]?.length)" class="px-4 py-3 text-xs" style="color: var(--color-text-muted)">
                Chưa có bài học.
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Error -->
    <div
      v-if="error"
      class="rounded-xl p-4 text-sm"
      style="background-color:color-mix(in srgb,#ef4444 12%,transparent);color:#f87171"
    >{{ error }}</div>

    <!-- ─── COURSE FORM MODAL ─────────────────────────────────────────────────── -->
    <Teleport to="body">
      <div
        v-if="showForm"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        style="background-color: rgba(0,0,0,0.6)"
        @click.self="showForm = false"
      >
        <div
          class="w-full max-w-lg rounded-2xl p-6 space-y-4"
          style="background-color: var(--color-surface-01)"
        >
          <h3 class="text-base font-bold" style="color: var(--color-text-base)">
            {{ formData.id ? 'Sửa khoá học' : 'Thêm khoá học mới' }}
          </h3>

          <div class="space-y-3">
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Tiêu đề *</label>
              <input
                v-model="formData.title"
                type="text"
                class="w-full rounded-xl px-3 py-2 text-sm border outline-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)"
              />
            </div>
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Slug (URL) *</label>
              <input
                v-model="formData.slug"
                type="text"
                class="w-full rounded-xl px-3 py-2 text-sm border outline-none font-mono"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)"
              />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Cấp độ CEFR *</label>
                <select
                  v-model="formData.level"
                  class="w-full rounded-xl px-3 py-2 text-sm border outline-none"
                  style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)"
                >
                  <option value="">Chọn cấp độ</option>
                  <option v-for="lvl in cefrLevels" :key="lvl.id" :value="lvl.id">
                    {{ lvl.code }} — {{ lvl.name_vi }}
                  </option>
                </select>
              </div>
              <div>
                <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Thứ tự</label>
                <input
                  v-model.number="formData.order"
                  type="number"
                  min="1"
                  class="w-full rounded-xl px-3 py-2 text-sm border outline-none"
                  style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)"
                />
              </div>
            </div>
            <div class="flex items-center gap-6">
              <label class="flex items-center gap-2 text-sm cursor-pointer" style="color: var(--color-text-base)">
                <input v-model="formData.is_premium" type="checkbox" class="rounded" />
                Premium
              </label>
              <label class="flex items-center gap-2 text-sm cursor-pointer" style="color: var(--color-text-base)">
                <input v-model="formData.is_active" type="checkbox" class="rounded" />
                Hiển thị
              </label>
            </div>
            <div>
              <label class="text-xs font-medium block mb-1" style="color: var(--color-text-muted)">Mô tả</label>
              <textarea
                v-model="formData.description"
                rows="3"
                class="w-full rounded-xl px-3 py-2 text-sm border outline-none resize-none"
                style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)"
              />
            </div>
          </div>

          <div
            v-if="formError"
            class="rounded-xl p-3 text-sm"
            style="background-color:color-mix(in srgb,#ef4444 12%,transparent);color:#f87171"
          >{{ formError }}</div>

          <div class="flex justify-end gap-3 pt-2">
            <button
              class="px-4 py-2 text-sm rounded-xl transition hover:opacity-80"
              style="background-color: var(--color-surface-03); color: var(--color-text-muted)"
              @click="showForm = false"
            >Huỷ</button>
            <button
              class="px-4 py-2 text-sm rounded-xl font-semibold transition hover:opacity-90"
              style="background-color: var(--color-primary-500); color: #fff"
              :disabled="formLoading"
              @click="submitCourseForm"
            >{{ formLoading ? 'Đang lưu...' : 'Lưu' }}</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ─── DELETE CONFIRM ─────────────────────────────────────────────────── -->
    <Teleport to="body">
      <div
        v-if="deleteTarget"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        style="background-color: rgba(0,0,0,0.6)"
        @click.self="deleteTarget = null"
      >
        <div class="w-full max-w-sm rounded-2xl p-6 space-y-4" style="background-color: var(--color-surface-01)">
          <h3 class="text-base font-bold" style="color: var(--color-text-base)">Xác nhận xoá</h3>
          <p class="text-sm" style="color: var(--color-text-muted)">
            Xoá khoá học "<strong>{{ deleteTarget.title }}</strong>"? Hành động này không thể hoàn tác.
          </p>
          <div class="flex justify-end gap-3">
            <button
              class="px-4 py-2 text-sm rounded-xl"
              style="background-color: var(--color-surface-03); color: var(--color-text-muted)"
              @click="deleteTarget = null"
            >Huỷ</button>
            <button
              class="px-4 py-2 text-sm rounded-xl font-semibold transition hover:opacity-90"
              style="background-color: #ef4444; color: #fff"
              :disabled="deleteLoading"
              @click="deleteCourse"
            >{{ deleteLoading ? 'Đang xoá...' : 'Xoá' }}</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { adminApi } from '@/api/admin.js'

const TABS = [{ id: 'courses', label: '📚 Khoá học' }]
const activeTab = ref('courses')

// ── Courses ────────────────────────────────────────────────────────────────
const courses = ref([])
const coursesLoading = ref(false)
const error = ref(null)

// ── Chapter / Lesson drill-down ────────────────────────────────────────────
const selectedCourse = ref(null)
const chapters = ref([])
const chaptersLoading = ref(false)
const expandedChapter = ref(null)
const lessons = reactive({})
const lessonsLoading = ref(false)

// ── Form ───────────────────────────────────────────────────────────────────
const showForm = ref(false)
const formLoading = ref(false)
const formError = ref(null)
const cefrLevels = ref([])
const formData = reactive({
  id: null, title: '', slug: '', level: '', order: 1,
  is_premium: false, is_active: true, description: '',
})

// ── Delete ─────────────────────────────────────────────────────────────────
const deleteTarget = ref(null)
const deleteLoading = ref(false)

async function fetchCourses() {
  coursesLoading.value = true
  error.value = null
  try {
    const { data } = await adminApi.getCourses()
    courses.value = data.results ?? data
  } catch {
    error.value = 'Không thể tải danh sách khoá học.'
  } finally {
    coursesLoading.value = false
  }
}

async function selectCourse(course) {
  if (selectedCourse.value?.id === course.id) {
    selectedCourse.value = null
    return
  }
  selectedCourse.value = course
  expandedChapter.value = null
  chaptersLoading.value = true
  try {
    const { data } = await adminApi.getChapters(course.id)
    chapters.value = data.results ?? data
  } catch {
    error.value = 'Không thể tải chương học.'
  } finally {
    chaptersLoading.value = false
  }
}

async function toggleChapter(ch) {
  if (expandedChapter.value === ch.id) {
    expandedChapter.value = null
    return
  }
  expandedChapter.value = ch.id
  if (lessons[ch.id]) return
  lessonsLoading.value = true
  try {
    const { data } = await adminApi.getLessons(selectedCourse.value.id, ch.id)
    lessons[ch.id] = data.results ?? data
  } catch {
    error.value = 'Không thể tải bài học.'
  } finally {
    lessonsLoading.value = false
  }
}

// ── Course form ────────────────────────────────────────────────────────────
async function openCourseForm(course = null) {
  formError.value = null
  if (!cefrLevels.value.length) {
    const { data } = await adminApi.getCEFRLevels()
    cefrLevels.value = data
  }
  if (course) {
    Object.assign(formData, {
      id: course.id,
      title: course.title,
      slug: course.slug,
      level: course.level,
      order: course.order,
      is_premium: course.is_premium,
      is_active: course.is_active,
      description: course.description || '',
    })
  } else {
    Object.assign(formData, {
      id: null, title: '', slug: '', level: '', order: 1,
      is_premium: false, is_active: true, description: '',
    })
  }
  showForm.value = true
}

async function submitCourseForm() {
  formError.value = null
  if (!formData.title || !formData.slug || !formData.level) {
    formError.value = 'Vui lòng điền đầy đủ tiêu đề, slug và cấp độ.'
    return
  }
  formLoading.value = true
  try {
    const payload = {
      title: formData.title,
      slug: formData.slug,
      level: formData.level,
      order: formData.order,
      is_premium: formData.is_premium,
      is_active: formData.is_active,
      description: formData.description,
    }
    if (formData.id) {
      await adminApi.updateCourse(formData.id, payload)
    } else {
      await adminApi.createCourse(payload)
    }
    showForm.value = false
    await fetchCourses()
  } catch (e) {
    formError.value = e?.response?.data?.detail || 'Không thể lưu khoá học.'
  } finally {
    formLoading.value = false
  }
}

function confirmDeleteCourse(course) {
  deleteTarget.value = course
}

async function deleteCourse() {
  deleteLoading.value = true
  try {
    await adminApi.deleteCourse(deleteTarget.value.id)
    deleteTarget.value = null
    if (selectedCourse.value?.id === deleteTarget.value?.id) {
      selectedCourse.value = null
    }
    await fetchCourses()
  } catch {
    error.value = 'Không thể xoá khoá học.'
    deleteTarget.value = null
  } finally {
    deleteLoading.value = false
  }
}

function lessonTypeIcon(type) {
  const map = {
    listening: '🎧', speaking: '🎤', reading: '📖', writing: '✍️',
    grammar: '📘', vocabulary: '📝', pronunciation: '🔊', assessment: '📊',
  }
  return map[type] || '📄'
}

onMounted(fetchCourses)
</script>
