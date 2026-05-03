<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-xl font-bold" style="color: var(--color-text-base)">Bài thi & Bài tập</h2>
      <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">Quản lý Exam Sets và Exercises</p>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 p-1 rounded-xl w-fit" style="background-color: var(--color-surface-02)">
      <button v-for="tab in TABS" :key="tab.key" @click="activeTab = tab.key"
        class="px-4 py-2 text-sm rounded-lg font-medium transition-all"
        :style="activeTab === tab.key ? 'background-color:var(--color-primary-500);color:#fff' : 'color:var(--color-text-muted)'">
        {{ tab.label }}
      </button>
    </div>
    <!-- ── Exam Sets ────────────────────────────────────────────────── -->
    <section v-if="activeTab === 'exam-sets'">
      <div class="flex flex-wrap gap-3 mb-4">
        <input v-model="examSearch" @input="loadExamSets" placeholder="Tìm tên bài thi..." class="input-sm" />
        <select v-model="examSkill" @change="loadExamSets" class="input-sm">
          <option value="">Tất cả kỹ năng</option>
          <option value="listening">Nghe</option>
          <option value="reading">Đọc</option>
          <option value="mixed">Tổng hợp</option>
        </select>
        <select v-model="examLevel" @change="loadExamSets" class="input-sm">
          <option value="">Tất cả cấp độ</option>
          <option v-for="l in cefrLevels" :key="l.id" :value="l.code">{{ l.code }}</option>
        </select>
        <button @click="openExamModal(null)" class="btn-primary text-sm px-4 py-2 rounded-lg ml-auto">+ Thêm Exam Set</button>
      </div>

      <div v-if="examLoading" class="space-y-2">
        <div v-for="n in 5" :key="n" class="h-14 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
      </div>
      <div v-else class="rounded-2xl overflow-hidden" style="background-color:var(--color-surface-02)">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b" style="border-color:var(--color-border);color:var(--color-text-muted)">
              <th class="px-4 py-3">Tên bài thi</th>
              <th class="px-4 py-3">Loại</th>
              <th class="px-4 py-3">Kỹ năng</th>
              <th class="px-4 py-3">Cấp độ</th>
              <th class="px-4 py-3">Câu hỏi</th>
              <th class="px-4 py-3">Trạng thái</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in examSets" :key="e.id" class="border-b last:border-0" style="border-color:var(--color-border)">
              <td class="px-4 py-3 font-medium" style="color:var(--color-text-base)">{{ e.title }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ e.exam_type }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ e.skill }}</td>
              <td class="px-4 py-3"><span class="text-xs px-2 py-0.5 rounded font-mono" style="background:var(--color-surface-03);color:var(--color-text-base)">{{ e.cefr_level }}</span></td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ e.total_questions }}</td>
              <td class="px-4 py-3">
                <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                  :style="e.is_active ? 'background:#dcfce7;color:#166534' : 'background:#fee2e2;color:#991b1b'">
                  {{ e.is_active ? 'Hoạt động' : 'Ẩn' }}
                </span>
              </td>
              <td class="px-4 py-3 flex gap-2">
                <button @click="openExamModal(e)" class="text-xs px-3 py-1 rounded-lg" style="background-color:var(--color-surface-03);color:var(--color-text-base)">Sửa</button>
                <button @click="deleteExam(e)" class="text-xs px-3 py-1 rounded-lg text-red-500" style="background-color:var(--color-surface-03)">Xoá</button>
              </td>
            </tr>
          </tbody>
        </table>
        <PaginationBar :pagination="examPagination" @change="loadExamPage" />
      </div>
    </section>

    <!-- ── Exercises ───────────────────────────────────────────────── -->
    <section v-if="activeTab === 'exercises'">
      <div class="flex flex-wrap gap-3 mb-4">
        <select v-model="exType" @change="loadExercises" class="input-sm">
          <option value="listening">Nghe (Listening)</option>
          <option value="speaking">Nói (Speaking)</option>
          <option value="reading">Đọc (Reading)</option>
          <option value="writing">Viết (Writing)</option>
        </select>
        <select v-model="exLevel" @change="loadExercises" class="input-sm">
          <option value="">Tất cả cấp độ</option>
          <option v-for="l in cefrLevels" :key="l.id" :value="l.code">{{ l.code }}</option>
        </select>
        <input v-model="exSearch" @input="loadExercises" placeholder="Tìm tiêu đề..." class="input-sm" />
      </div>
      <div v-if="exLoading" class="space-y-2">
        <div v-for="n in 5" :key="n" class="h-12 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
      </div>
      <div v-else class="rounded-2xl overflow-hidden" style="background-color:var(--color-surface-02)">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b" style="border-color:var(--color-border);color:var(--color-text-muted)">
              <th class="px-4 py-3">Tiêu đề</th>
              <th class="px-4 py-3">Cấp độ</th>
              <th class="px-4 py-3">Điểm tối đa</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ex in exercises" :key="ex.id" class="border-b last:border-0" style="border-color:var(--color-border)">
              <td class="px-4 py-3 font-medium" style="color:var(--color-text-base)">{{ ex.title }}</td>
              <td class="px-4 py-3"><span class="text-xs px-2 py-0.5 rounded font-mono" style="background:var(--color-surface-03)">{{ ex.cefr_level }}</span></td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ ex.max_score ?? '—' }}</td>
            </tr>
          </tbody>
        </table>
        <p v-if="exercises.length === 0" class="text-center text-sm py-8" style="color:var(--color-text-muted)">Không tìm thấy bài tập.</p>
      </div>
    </section>

    <!-- ── Questions ──────────────────────────────────────────────── -->
    <section v-if="activeTab === 'questions'">
      <div class="flex flex-wrap gap-3 mb-4">
        <input v-model="qSearch" @input="loadQuestions" placeholder="Tìm câu hỏi..." class="input-sm" />
        <select v-model="qExType" @change="loadQuestions" class="input-sm">
          <option value="">Tất cả exercise_type</option>
          <option value="listening">Listening</option>
          <option value="reading">Reading</option>
          <option value="grammar">Grammar</option>
          <option value="exam">Exam</option>
        </select>
        <select v-model="qType" @change="loadQuestions" class="input-sm">
          <option value="">Tất cả loại</option>
          <option value="mc">Trắc nghiệm</option>
          <option value="gap_fill">Điền từ</option>
          <option value="drag_drop">Kéo thả</option>
        </select>
        <button @click="openQModal(null)" class="btn-primary text-sm px-4 py-2 rounded-lg ml-auto">+ Thêm câu hỏi</button>
      </div>
      <div v-if="qLoading" class="space-y-2">
        <div v-for="n in 5" :key="n" class="h-12 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
      </div>
      <div v-else class="rounded-2xl overflow-hidden" style="background-color:var(--color-surface-02)">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b" style="border-color:var(--color-border);color:var(--color-text-muted)">
              <th class="px-4 py-3">Câu hỏi</th>
              <th class="px-4 py-3">Loại</th>
              <th class="px-4 py-3">Exercise</th>
              <th class="px-4 py-3">Điểm</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="q in questions" :key="q.id" class="border-b last:border-0" style="border-color:var(--color-border)">
              <td class="px-4 py-3 font-medium max-w-xs truncate" style="color:var(--color-text-base)" :title="q.question_text">
                {{ q.question_text }}
              </td>
              <td class="px-4 py-3">
                <span class="text-xs px-2 py-0.5 rounded font-mono" style="background:var(--color-surface-03);color:var(--color-text-base)">
                  {{ q.question_type }}
                </span>
              </td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">
                {{ q.exercise_type }}/{{ q.exercise_id }}
              </td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ q.points }}đ</td>
              <td class="px-4 py-3 flex gap-2">
                <button @click="openQModal(q)" class="text-xs px-3 py-1 rounded-lg" style="background-color:var(--color-surface-03);color:var(--color-text-base)">Sửa</button>
                <button @click="deleteQuestion(q)" class="text-xs px-3 py-1 rounded-lg text-red-500" style="background-color:var(--color-surface-03)">Xoá</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="!qLoading && questions.length === 0" class="text-center text-sm py-8" style="color:var(--color-text-muted)">Không tìm thấy câu hỏi.</p>
        <PaginationBar :pagination="qPagination" @change="loadQPage" />
      </div>
    </section>

    <!-- ── Exam Set Modal ──────────────────────────────────────────── -->
    <div v-if="examModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="w-full max-w-md rounded-2xl p-6 space-y-4" style="background-color:var(--color-surface-01)">
        <h3 class="text-base font-bold" style="color:var(--color-text-base)">
          {{ examModal.item ? 'Sửa Exam Set' : 'Thêm Exam Set mới' }}
        </h3>
        <div class="space-y-3">
          <input v-model="examForm.title" placeholder="Tiêu đề*" class="input-base w-full" />
          <div class="grid grid-cols-2 gap-3">
            <select v-model="examForm.exam_type" class="input-base">
              <option value="progress_check">Progress Check</option>
              <option value="mock_test">Mock Test</option>
              <option value="placement">Placement</option>
            </select>
            <select v-model="examForm.skill" class="input-base">
              <option value="listening">Nghe</option>
              <option value="reading">Đọc</option>
              <option value="mixed">Tổng hợp</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <select v-model="examForm.cefr_level" class="input-base">
              <option value="">-- Chọn cấp độ --</option>
              <option v-for="l in cefrLevels" :key="l.id" :value="l.code">{{ l.code }}</option>
            </select>
            <input v-model.number="examForm.time_limit_minutes" type="number" placeholder="Thời gian (phút)" class="input-base" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <input v-model.number="examForm.passing_score" type="number" placeholder="Điểm đậu" class="input-base" />
            <input v-model.number="examForm.total_questions" type="number" placeholder="Số câu hỏi" class="input-base" />
          </div>
          <label class="flex items-center gap-2 text-sm" style="color:var(--color-text-muted)">
            <input type="checkbox" v-model="examForm.is_active" />
            Kích hoạt
          </label>
        </div>
        <div class="flex gap-3 justify-end">
          <button @click="examModal.open = false" class="text-sm px-4 py-2 rounded-lg" style="background-color:var(--color-surface-02);color:var(--color-text-base)">Huỷ</button>
          <button @click="saveExam" :disabled="examSaving" class="btn-primary text-sm px-4 py-2 rounded-lg">
            {{ examSaving ? '...' : 'Lưu' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Question Modal ─────────────────────────────────────────── -->
    <div v-if="qModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div class="w-full max-w-2xl rounded-2xl p-6 space-y-4 overflow-y-auto max-h-[90vh]"
           style="background-color:var(--color-surface-01)">
        <h3 class="text-base font-bold" style="color:var(--color-text-base)">
          {{ qModal.item ? 'Sửa câu hỏi' : 'Thêm câu hỏi mới' }}
        </h3>
        <div class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <select v-model="qForm.question_type" class="input-base">
              <option value="mc">Trắc nghiệm (MC)</option>
              <option value="gap_fill">Điền từ (Gap Fill)</option>
              <option value="drag_drop">Kéo thả (Drag & Drop)</option>
            </select>
            <div class="grid grid-cols-2 gap-2">
              <select v-model="qForm.exercise_type" class="input-base">
                <option value="listening">Listening</option>
                <option value="reading">Reading</option>
                <option value="grammar">Grammar</option>
                <option value="exam">Exam</option>
              </select>
              <input v-model.number="qForm.exercise_id" type="number" placeholder="Exercise ID" class="input-base" />
            </div>
          </div>
          <textarea v-model="qForm.question_text" rows="3" placeholder="Nội dung câu hỏi*" class="input-base w-full resize-none" />
          <div class="grid grid-cols-3 gap-3">
            <input v-model.number="qForm.points" type="number" min="1" placeholder="Điểm" class="input-base" />
            <input v-model.number="qForm.order" type="number" min="0" placeholder="Thứ tự" class="input-base" />
            <input v-model="qForm.explanation" placeholder="Giải thích (tuỳ chọn)" class="input-base" />
          </div>

          <!-- MC Options -->
          <div v-if="qForm.question_type === 'mc'" class="space-y-2">
            <p class="text-xs font-semibold uppercase tracking-wide" style="color:var(--color-text-muted)">Đáp án lựa chọn</p>
            <div v-for="(opt, i) in qForm.options" :key="i" class="flex items-center gap-2">
              <input type="checkbox" :value="opt.option_text" v-model="qForm.correct_answers_json"
                     class="rounded" title="Chọn là đáp án đúng" />
              <input v-model="opt.option_text" :placeholder="`Lựa chọn ${i+1}`" class="input-base flex-1" />
              <button @click="qForm.options.splice(i, 1)" class="text-red-400 text-xs px-1.5 py-0.5 rounded">✕</button>
            </div>
            <button @click="qForm.options.push({ option_text: '', order: qForm.options.length })"
                    class="text-xs px-3 py-1.5 rounded-lg" style="background-color:var(--color-surface-02);color:var(--color-text-muted)">
              + Thêm lựa chọn
            </button>
          </div>

          <!-- Gap Fill / Drag Drop correct answers -->
          <div v-else class="space-y-2">
            <p class="text-xs font-semibold uppercase tracking-wide" style="color:var(--color-text-muted)">
              Đáp án đúng (mỗi dòng một đáp án)
            </p>
            <textarea v-model="qForm.correctAnswersText" rows="3" placeholder="Nhập từng đáp án đúng, mỗi dòng một đáp án"
                      class="input-base w-full resize-none text-sm" />
          </div>
        </div>
        <div class="flex gap-3 justify-end pt-2">
          <button @click="qModal.open = false" class="text-sm px-4 py-2 rounded-lg" style="background-color:var(--color-surface-02);color:var(--color-text-base)">Huỷ</button>
          <button @click="saveQuestion" :disabled="qSaving" class="btn-primary text-sm px-4 py-2 rounded-lg">
            {{ qSaving ? '...' : 'Lưu câu hỏi' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { adminApi } from '@/api/admin.js'
import PaginationBar from '@/components/PaginationBar.vue'

const TABS = [
  { key: 'exam-sets', label: 'Exam Sets' },
  { key: 'exercises', label: 'Exercises' },
  { key: 'questions', label: '📋 Ngân hàng câu hỏi' },
]
const activeTab = ref('exam-sets')

const cefrLevels = ref([])

// Exam Sets
const examSets = ref([])
const examLoading = ref(false)
const examSearch = ref('')
const examSkill = ref('')
const examLevel = ref('')
const examPagination = reactive({ count: 0, next: null, previous: null, page: 1 })
const examModal = reactive({ open: false, item: null })
const examForm = reactive({ title: '', exam_type: 'progress_check', skill: 'listening', cefr_level: '', time_limit_minutes: 60, passing_score: 70, total_questions: 20, is_active: true })
const examSaving = ref(false)

// Exercises
const exercises = ref([])
const exLoading = ref(false)
const exType = ref('listening')
const exLevel = ref('')
const exSearch = ref('')

watch(activeTab, (tab) => {
  if (tab === 'exercises' && exercises.value.length === 0) loadExercises()
  if (tab === 'questions' && questions.value.length === 0) loadQuestions()
})

onMounted(async () => {
  const r = await adminApi.getCEFRLevels()
  cefrLevels.value = r.data
  loadExamSets()
})

async function loadExamSets(page = 1) {
  examLoading.value = true
  try {
    const r = await adminApi.getExamSets({
      search: examSearch.value || undefined,
      skill: examSkill.value || undefined,
      cefr_level: examLevel.value || undefined,
      page,
    })
    examSets.value = r.data.results ?? r.data
    Object.assign(examPagination, { count: r.data.count, next: r.data.next, previous: r.data.previous, page })
  } finally { examLoading.value = false }
}
function loadExamPage(p) { loadExamSets(p) }

async function loadExercises() {
  exLoading.value = true
  try {
    const r = await adminApi.getExercises({ type: exType.value, level: exLevel.value || undefined, search: exSearch.value || undefined })
    exercises.value = r.data
  } finally { exLoading.value = false }
}

function openExamModal(item) {
  examModal.item = item
  if (item) Object.assign(examForm, { title: item.title, exam_type: item.exam_type, skill: item.skill, cefr_level: item.cefr_level, time_limit_minutes: item.time_limit_minutes, passing_score: item.passing_score, total_questions: item.total_questions, is_active: item.is_active })
  else Object.assign(examForm, { title: '', exam_type: 'progress_check', skill: 'listening', cefr_level: '', time_limit_minutes: 60, passing_score: 70, total_questions: 20, is_active: true })
  examModal.open = true
}
async function saveExam() {
  examSaving.value = true
  try {
    if (examModal.item) await adminApi.updateExamSet(examModal.item.id, examForm)
    else await adminApi.createExamSet(examForm)
    examModal.open = false
    await loadExamSets()
  } finally { examSaving.value = false }
}
async function deleteExam(e) {
  if (!confirm(`Xoá Exam Set "${e.title}"?`)) return
  await adminApi.deleteExamSet(e.id)
  await loadExamSets()
}

// ── Questions ──────────────────────────────────────────────────────────────
const questions = ref([])
const qLoading = ref(false)
const qSearch = ref('')
const qExType = ref('')
const qType = ref('')
const qPagination = reactive({ count: 0, next: null, previous: null, page: 1 })
const qModal = reactive({ open: false, item: null })
const qForm = reactive({
  exercise_type: 'listening', exercise_id: '',
  question_type: 'mc', question_text: '', order: 0,
  points: 1, explanation: '',
  options: [],
  correct_answers_json: [],
  correctAnswersText: '',
})
const qSaving = ref(false)

async function loadQuestions(page = 1) {
  qLoading.value = true
  try {
    const r = await adminApi.getQuestions({
      search: qSearch.value || undefined,
      exercise_type: qExType.value || undefined,
      question_type: qType.value || undefined,
      page,
    })
    questions.value = r.data.results ?? r.data
    Object.assign(qPagination, { count: r.data.count, next: r.data.next, previous: r.data.previous, page })
  } finally { qLoading.value = false }
}
function loadQPage(p) { loadQuestions(p) }

function openQModal(item) {
  qModal.item = item
  if (item) {
    Object.assign(qForm, {
      exercise_type: item.exercise_type,
      exercise_id: item.exercise_id,
      question_type: item.question_type,
      question_text: item.question_text,
      order: item.order,
      points: item.points,
      explanation: item.explanation || '',
      options: item.options ? item.options.map(o => ({ ...o })) : [],
      correct_answers_json: item.correct_answers_json ? [...item.correct_answers_json] : [],
      correctAnswersText: item.correct_answers_json ? item.correct_answers_json.join('\n') : '',
    })
  } else {
    Object.assign(qForm, {
      exercise_type: 'listening', exercise_id: '',
      question_type: 'mc', question_text: '', order: 0,
      points: 1, explanation: '',
      options: [],
      correct_answers_json: [],
      correctAnswersText: '',
    })
  }
  qModal.open = true
}

async function saveQuestion() {
  qSaving.value = true
  try {
    const payload = {
      exercise_type: qForm.exercise_type,
      exercise_id: qForm.exercise_id,
      question_type: qForm.question_type,
      question_text: qForm.question_text,
      order: qForm.order,
      points: qForm.points,
      explanation: qForm.explanation,
      options: qForm.question_type === 'mc'
        ? qForm.options.map((o, i) => ({ option_text: o.option_text, order: i }))
        : [],
      correct_answers_json: qForm.question_type === 'mc'
        ? qForm.correct_answers_json
        : qForm.correctAnswersText.split('\n').map(s => s.trim()).filter(Boolean),
    }
    if (qModal.item) await adminApi.updateQuestion(qModal.item.id, payload)
    else await adminApi.createQuestion(payload)
    qModal.open = false
    await loadQuestions()
  } finally { qSaving.value = false }
}

async function deleteQuestion(q) {
  if (!confirm(`Xoá câu hỏi: "${q.question_text.slice(0, 50)}..."?`)) return
  await adminApi.deleteQuestion(q.id)
  await loadQuestions()
}
</script>
