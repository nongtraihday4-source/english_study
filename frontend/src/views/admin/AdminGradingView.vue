<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-xl font-bold" style="color: var(--color-text-base)">AI Grading</h2>
      <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">Giám sát hàng chờ chấm điểm AI và bài nộp</p>
    </div>

    <!-- Stats Row -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
      <div v-for="card in statCards" :key="card.label" class="rounded-2xl p-4 flex flex-col gap-1" style="background-color:var(--color-surface-02)">
        <div class="text-2xl font-bold" style="color:var(--color-text-base)">{{ statsLoading ? '—' : card.value }}</div>
        <div class="text-xs" style="color:var(--color-text-muted)">{{ card.label }}</div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 p-1 rounded-xl w-fit" style="background-color:var(--color-surface-02)">
      <button v-for="tab in TABS" :key="tab.key" @click="activeTab = tab.key"
        class="px-4 py-2 text-sm rounded-lg font-medium transition-all"
        :style="activeTab === tab.key ? 'background-color:var(--color-primary-500);color:#fff' : 'color:var(--color-text-muted)'">
        {{ tab.label }}
      </button>
    </div>

    <!-- ── Jobs ─────────────────────────────────────────────────────── -->
    <section v-if="activeTab === 'jobs'">
      <div class="flex flex-wrap gap-3 mb-4">
        <select v-model="jobStatus" @change="loadJobs" class="input-sm">
          <option value="">Tất cả trạng thái</option>
          <option value="queued">Đang chờ</option>
          <option value="processing">Đang xử lý</option>
          <option value="completed">Hoàn thành</option>
          <option value="failed">Thất bại</option>
          <option value="retrying">Đang retry</option>
        </select>
        <select v-model="jobType" @change="loadJobs" class="input-sm">
          <option value="">Tất cả loại</option>
          <option value="speaking">Speaking</option>
          <option value="writing">Writing</option>
        </select>
      </div>
      <div v-if="jobsLoading" class="space-y-2">
        <div v-for="n in 5" :key="n" class="h-12 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
      </div>
      <div v-else class="rounded-2xl overflow-x-auto" style="background-color:var(--color-surface-02)">
        <table class="w-full text-sm min-w-[640px]">
          <thead>
            <tr class="text-left border-b" style="border-color:var(--color-border);color:var(--color-text-muted)">
              <th class="px-4 py-3">ID</th>
              <th class="px-4 py-3">Loại</th>
              <th class="px-4 py-3">Trạng thái</th>
              <th class="px-4 py-3">Retry</th>
              <th class="px-4 py-3">Model AI</th>
              <th class="px-4 py-3">Token</th>
              <th class="px-4 py-3">Thời gian</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="job in jobs" :key="job.id" class="border-b last:border-0" style="border-color:var(--color-border)">
              <td class="px-4 py-3 text-xs font-mono" style="color:var(--color-text-muted)">{{ job.id }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-base)">{{ job.job_type }}</td>
              <td class="px-4 py-3">
                <span class="text-xs px-2 py-0.5 rounded-full font-medium" :style="jobStatusStyle(job.status)">{{ job.status }}</span>
              </td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ job.retry_count }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ job.ai_model_used ?? '—' }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ job.tokens_used ?? '—' }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ fmtDate(job.queued_at) }}</td>
              <td class="px-4 py-3">
                <button v-if="['failed','retrying'].includes(job.status)" @click="retryJob(job)"
                  class="text-xs px-3 py-1 rounded-lg" style="background-color:var(--color-surface-03);color:var(--color-primary-500)">
                  Retry
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <PaginationBar :pagination="jobsPagination" @change="loadJobsPage" />
      </div>
    </section>

    <!-- ── Speaking Submissions ──────────────────────────────────────── -->
    <section v-if="activeTab === 'speaking'">
      <div class="flex flex-wrap gap-3 mb-4">
        <input v-model="speakSearch" @input="loadSpeaking" placeholder="Email người dùng..." class="input-sm" />
        <select v-model="speakStatus" @change="loadSpeaking" class="input-sm">
          <option value="">Tất cả trạng thái</option>
          <option value="pending">Chờ chấm</option>
          <option value="graded">Đã chấm</option>
          <option value="failed">Lỗi</option>
        </select>
      </div>
      <div v-if="speakLoading" class="space-y-2">
        <div v-for="n in 5" :key="n" class="h-12 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
      </div>
      <div v-else class="rounded-2xl overflow-x-auto" style="background-color:var(--color-surface-02)">
        <table class="w-full text-sm min-w-[560px]">
          <thead>
            <tr class="text-left border-b" style="border-color:var(--color-border);color:var(--color-text-muted)">
              <th class="px-4 py-3">Người dùng</th>
              <th class="px-4 py-3">Trạng thái</th>
              <th class="px-4 py-3">Điểm</th>
              <th class="px-4 py-3">Thời gian</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in speakingSubs" :key="s.id" class="border-b last:border-0" style="border-color:var(--color-border)">
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-base)">{{ s.user_email }}</td>
              <td class="px-4 py-3">
                <span class="text-xs px-2 py-0.5 rounded-full font-medium" :style="subStatusStyle(s.status)">{{ s.status }}</span>
              </td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ s.overall_score ?? '—' }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ fmtDate(s.created_at) }}</td>
            </tr>
          </tbody>
        </table>
        <PaginationBar :pagination="speakPagination" @change="loadSpeakingPage" />
      </div>
    </section>

    <!-- ── Writing Submissions ───────────────────────────────────────── -->
    <section v-if="activeTab === 'writing'">
      <div class="flex flex-wrap gap-3 mb-4">
        <input v-model="writeSearch" @input="loadWriting" placeholder="Email người dùng..." class="input-sm" />
        <select v-model="writeStatus" @change="loadWriting" class="input-sm">
          <option value="">Tất cả trạng thái</option>
          <option value="pending">Chờ chấm</option>
          <option value="graded">Đã chấm</option>
          <option value="failed">Lỗi</option>
        </select>
      </div>
      <div v-if="writeLoading" class="space-y-2">
        <div v-for="n in 5" :key="n" class="h-12 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
      </div>
      <div v-else class="rounded-2xl overflow-x-auto" style="background-color:var(--color-surface-02)">
        <table class="w-full text-sm min-w-[560px]">
          <thead>
            <tr class="text-left border-b" style="border-color:var(--color-border);color:var(--color-text-muted)">
              <th class="px-4 py-3">Người dùng</th>
              <th class="px-4 py-3">Trạng thái</th>
              <th class="px-4 py-3">Điểm</th>
              <th class="px-4 py-3">Thời gian</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="w in writingSubs" :key="w.id" class="border-b last:border-0" style="border-color:var(--color-border)">
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-base)">{{ w.user_email }}</td>
              <td class="px-4 py-3">
                <span class="text-xs px-2 py-0.5 rounded-full font-medium" :style="subStatusStyle(w.status)">{{ w.status }}</span>
              </td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ w.overall_score ?? '—' }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ fmtDate(w.created_at) }}</td>
            </tr>
          </tbody>
        </table>
        <PaginationBar :pagination="writePagination" @change="loadWritingPage" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { adminApi } from '@/api/admin.js'
import PaginationBar from '@/components/PaginationBar.vue'

const TABS = [
  { key: 'jobs', label: 'Grading Jobs' },
  { key: 'speaking', label: 'Speaking' },
  { key: 'writing', label: 'Writing' },
]
const activeTab = ref('jobs')

const stats = ref({})
const statsLoading = ref(true)
const statCards = computed(() => [
  { label: 'Đang chờ', value: stats.value.queued ?? '—' },
  { label: 'Đang xử lý', value: stats.value.processing ?? '—' },
  { label: 'Hoàn thành', value: stats.value.completed ?? '—' },
  { label: 'Thất bại', value: stats.value.failed ?? '—' },
  { label: 'Tổng token', value: stats.value.tokens_total?.toLocaleString() ?? '—' },
])

const jobs = ref([])
const jobsLoading = ref(false)
const jobStatus = ref('')
const jobType = ref('')
const jobsPagination = reactive({ count: 0, next: null, previous: null, page: 1 })

const speakingSubs = ref([])
const speakLoading = ref(false)
const speakSearch = ref('')
const speakStatus = ref('')
const speakPagination = reactive({ count: 0, next: null, previous: null, page: 1 })

const writingSubs = ref([])
const writeLoading = ref(false)
const writeSearch = ref('')
const writeStatus = ref('')
const writePagination = reactive({ count: 0, next: null, previous: null, page: 1 })

watch(activeTab, (tab) => {
  if (tab === 'speaking' && speakingSubs.value.length === 0) loadSpeaking()
  if (tab === 'writing' && writingSubs.value.length === 0) loadWriting()
})

onMounted(() => {
  loadStats()
  loadJobs()
})

async function loadStats() {
  statsLoading.value = true
  try { const r = await adminApi.getGradingStats(); stats.value = r.data }
  finally { statsLoading.value = false }
}

async function loadJobs(page = 1) {
  jobsLoading.value = true
  try {
    const r = await adminApi.getGradingJobs({ status: jobStatus.value || undefined, job_type: jobType.value || undefined, page })
    jobs.value = r.data.results ?? r.data
    Object.assign(jobsPagination, { count: r.data.count, next: r.data.next, previous: r.data.previous, page })
  } finally { jobsLoading.value = false }
}
function loadJobsPage(p) { loadJobs(p) }

async function retryJob(job) {
  await adminApi.retryGradingJob(job.id)
  await Promise.all([loadStats(), loadJobs(jobsPagination.page)])
}

async function loadSpeaking(page = 1) {
  speakLoading.value = true
  try {
    const r = await adminApi.getSpeakingSubmissions({ search: speakSearch.value || undefined, status: speakStatus.value || undefined, page })
    speakingSubs.value = r.data.results ?? r.data
    Object.assign(speakPagination, { count: r.data.count, next: r.data.next, previous: r.data.previous, page })
  } finally { speakLoading.value = false }
}
function loadSpeakingPage(p) { loadSpeaking(p) }

async function loadWriting(page = 1) {
  writeLoading.value = true
  try {
    const r = await adminApi.getWritingSubmissions({ search: writeSearch.value || undefined, status: writeStatus.value || undefined, page })
    writingSubs.value = r.data.results ?? r.data
    Object.assign(writePagination, { count: r.data.count, next: r.data.next, previous: r.data.previous, page })
  } finally { writeLoading.value = false }
}
function loadWritingPage(p) { loadWriting(p) }

function fmtDate(d) { return d ? new Date(d).toLocaleString('vi-VN') : '—' }
function jobStatusStyle(s) {
  const m = { queued: 'background:#fef9c3;color:#854d0e', processing: 'background:#dbeafe;color:#1e40af', completed: 'background:#dcfce7;color:#166534', failed: 'background:#fee2e2;color:#991b1b', retrying: 'background:#ede9fe;color:#5b21b6' }
  return m[s] ?? ''
}
function subStatusStyle(s) {
  const m = { pending: 'background:#fef9c3;color:#854d0e', graded: 'background:#dcfce7;color:#166534', failed: 'background:#fee2e2;color:#991b1b' }
  return m[s] ?? ''
}
</script>
