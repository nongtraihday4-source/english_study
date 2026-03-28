<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-xl font-bold" style="color: var(--color-text-base)">Nhật ký hoạt động</h2>
      <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">Theo dõi tất cả thao tác quản trị</p>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-3 items-center">
      <input v-model="search" @input="loadLog" placeholder="Email admin / mô tả..." class="input-sm" />
      <select v-model="action" @change="loadLog" class="input-sm">
        <option value="">Tất cả hành động</option>
        <option v-for="a in ACTIONS" :key="a.value" :value="a.value">{{ a.label }}</option>
      </select>
      <input v-model="modelName" @input="loadLog" placeholder="Model (vd: User)" class="input-sm" />
      <button
        @click="exportCsv"
        :disabled="exporting"
        class="ml-auto flex items-center gap-1.5 text-sm px-4 py-1.5 rounded-xl font-medium transition hover:opacity-80 disabled:opacity-50"
        style="background-color:var(--color-surface-03);color:var(--color-text-muted)"
      >
        <span v-if="exporting">Đang xuất...</span>
        <span v-else>⬇ Xuất CSV</span>
      </button>
    </div>

    <div v-if="loading" class="space-y-2">
      <div v-for="n in 8" :key="n" class="h-12 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
    </div>

    <div v-else class="rounded-2xl overflow-x-auto" style="background-color:var(--color-surface-02)">
      <table class="w-full text-sm min-w-[680px]">
        <thead>
          <tr class="text-left border-b" style="border-color:var(--color-border);color:var(--color-text-muted)">
            <th class="px-4 py-3">Thời gian</th>
            <th class="px-4 py-3">Admin</th>
            <th class="px-4 py-3">Hành động</th>
            <th class="px-4 py-3">Model</th>
            <th class="px-4 py-3">ID</th>
            <th class="px-4 py-3">Mô tả</th>
            <th class="px-4 py-3">IP</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id" class="border-b last:border-0" style="border-color:var(--color-border)">
            <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ fmtDate(log.created_at) }}</td>
            <td class="px-4 py-3 text-xs" style="color:var(--color-text-base)">{{ log.admin_email ?? '—' }}</td>
            <td class="px-4 py-3">
              <span class="text-xs px-2 py-0.5 rounded-full font-medium" :style="actionStyle(log.action)">{{ log.action }}</span>
            </td>
            <td class="px-4 py-3 text-xs font-mono" style="color:var(--color-text-muted)">{{ log.model_name }}</td>
            <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ log.object_id ?? '—' }}</td>
            <td class="px-4 py-3 text-xs max-w-xs truncate" style="color:var(--color-text-base)">{{ log.description }}</td>
            <td class="px-4 py-3 text-xs font-mono" style="color:var(--color-text-muted)">{{ log.ip_address }}</td>
          </tr>
        </tbody>
      </table>
      <p v-if="logs.length === 0" class="text-center py-10 text-sm" style="color:var(--color-text-muted)">Chưa có nhật ký.</p>
      <PaginationBar :pagination="pagination" @change="loadLogPage" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { adminApi } from '@/api/admin.js'
import PaginationBar from '@/components/PaginationBar.vue'

const ACTIONS = [
  { value: 'create', label: 'Tạo mới' },
  { value: 'update', label: 'Cập nhật' },
  { value: 'delete', label: 'Xoá' },
  { value: 'ban', label: 'Khoá' },
  { value: 'unban', label: 'Mở khoá' },
  { value: 'bulk_action', label: 'Hàng loạt' },
  { value: 'login', label: 'Đăng nhập' },
  { value: 'export', label: 'Xuất dữ liệu' },
]

const logs = ref([])
const loading = ref(false)
const search = ref('')
const action = ref('')
const modelName = ref('')
const pagination = reactive({ count: 0, next: null, previous: null, page: 1 })
const exporting = ref(false)

onMounted(() => loadLog())

async function loadLog(page = 1) {
  loading.value = true
  try {
    const r = await adminApi.getAuditLog({
      search: search.value || undefined,
      action: action.value || undefined,
      model_name: modelName.value || undefined,
      page,
    })
    logs.value = r.data.results ?? r.data
    Object.assign(pagination, { count: r.data.count, next: r.data.next, previous: r.data.previous, page })
  } finally { loading.value = false }
}
function loadLogPage(p) { loadLog(p) }

async function exportCsv() {
  exporting.value = true
  try {
    const r = await adminApi.exportAuditLog({
      search: search.value || undefined,
      action: action.value || undefined,
      model_name: modelName.value || undefined,
    })
    const url = URL.createObjectURL(r.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `audit-log-${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } finally {
    exporting.value = false
  }
}

function fmtDate(d) { return d ? new Date(d).toLocaleString('vi-VN') : '—' }
function actionStyle(a) {
  const m = {
    create: 'background:#dcfce7;color:#166534',
    update: 'background:#dbeafe;color:#1e40af',
    delete: 'background:#fee2e2;color:#991b1b',
    ban: 'background:#fee2e2;color:#991b1b',
    unban: 'background:#dcfce7;color:#166534',
    bulk_action: 'background:#ede9fe;color:#5b21b6',
    login: 'background:#f3f4f6;color:#374151',
    export: 'background:#fef9c3;color:#854d0e',
  }
  return m[a] ?? 'background:#f3f4f6;color:#374151'
}
</script>
