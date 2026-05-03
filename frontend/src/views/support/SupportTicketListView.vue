<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h2 class="text-xl font-bold" style="color: var(--color-text-base)">Danh sách Tickets</h2>
        <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">Quản lý & xử lý ticket hỗ trợ</p>
      </div>
      <button class="text-sm font-semibold px-4 py-2 rounded-xl hover:opacity-80 transition" style="background-color:#3b82f6;color:#fff" @click="showCreate = true">+ Tạo Ticket</button>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-2">
      <input v-model="filters.search" type="text" placeholder="Tìm subject, email..." class="flex-1 min-w-40 rounded-xl px-3 py-2 text-sm border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" @keyup.enter="load(1)" />
      <select v-model="filters.status" class="rounded-xl px-3 py-2 text-sm border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" @change="load(1)">
        <option value="">Mọi trạng thái</option>
        <option value="open">Open</option>
        <option value="in_progress">In Progress</option>
        <option value="waiting_customer">Chờ KH</option>
        <option value="resolved">Resolved</option>
        <option value="closed">Closed</option>
      </select>
      <select v-model="filters.priority" class="rounded-xl px-3 py-2 text-sm border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" @change="load(1)">
        <option value="">Mọi ưu tiên</option>
        <option value="low">Thấp</option>
        <option value="medium">Trung bình</option>
        <option value="high">Cao</option>
        <option value="urgent">Khẩn</option>
      </select>
      <select v-model="filters.assigned_to" class="rounded-xl px-3 py-2 text-sm border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" @change="load(1)">
        <option value="">Tất cả</option>
        <option value="me">Giao cho tôi</option>
        <option value="unassigned">Chưa giao</option>
      </select>
    </div>

    <!-- Table -->
    <div class="rounded-2xl overflow-hidden" style="background-color:var(--color-surface-02)">
      <div v-if="loading" class="p-6 space-y-2">
        <div v-for="n in 6" :key="n" class="h-12 animate-pulse rounded-xl" style="background-color:var(--color-surface-03)" />
      </div>
      <table v-else-if="tickets.length" class="w-full text-sm">
        <thead>
          <tr style="border-bottom:1px solid var(--color-surface-04)">
            <th v-for="h in ['#', 'Tiêu đề', 'Người dùng', 'Danh mục', 'Ưu tiên', 'Trạng thái', 'Được giao', 'SLA', '']" :key="h" class="text-left px-4 py-3 text-xs font-semibold" style="color:var(--color-text-muted)">{{ h }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in tickets" :key="t.id" style="border-bottom:1px solid var(--color-surface-04)" class="hover:opacity-90 transition">
            <td class="px-4 py-3 text-xs font-mono" style="color:var(--color-text-muted)">#{{ t.id }}</td>
            <td class="px-4 py-3 max-w-xs truncate font-medium" style="color:var(--color-text-base)">{{ t.subject }}</td>
            <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ t.user_email }}</td>
            <td class="px-4 py-3 text-xs capitalize" style="color:var(--color-text-muted)">{{ t.category }}</td>
            <td class="px-4 py-3"><span class="text-xs font-semibold" :style="priorityStyle(t.priority)">{{ priorityIcon(t.priority) }} {{ t.priority }}</span></td>
            <td class="px-4 py-3"><span class="text-xs px-2 py-0.5 rounded-full" :style="statusStyle(t.status)">{{ statusLabel(t.status) }}</span></td>
            <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ t.assigned_to_name ?? '—' }}</td>
            <td class="px-4 py-3 text-xs" :style="t.is_overdue ? 'color:#f87171;font-weight:600' : 'color:var(--color-text-muted)'">{{ t.sla_deadline ? slaLabel(t.sla_deadline, t.is_overdue) : '—' }}</td>
            <td class="px-4 py-3"><RouterLink :to="`/support/tickets/${t.id}`" class="text-xs font-medium hover:opacity-80" style="color:#60a5fa">Xem →</RouterLink></td>
          </tr>
        </tbody>
      </table>
      <div v-else class="p-8 text-center text-sm" style="color:var(--color-text-muted)">Không có ticket nào.</div>
      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-between px-4 py-3 border-t" style="border-color:var(--color-surface-04)">
        <span class="text-xs" style="color:var(--color-text-muted)">{{ total }} tickets</span>
        <div class="flex gap-2">
          <button :disabled="page === 1" class="text-xs px-3 py-1.5 rounded-lg disabled:opacity-40" style="background-color:var(--color-surface-03);color:var(--color-text-base)" @click="load(page - 1)">‹</button>
          <span class="text-xs py-1.5 px-2" style="color:var(--color-text-muted)">{{ page }} / {{ totalPages }}</span>
          <button :disabled="page === totalPages" class="text-xs px-3 py-1.5 rounded-lg disabled:opacity-40" style="background-color:var(--color-surface-03);color:var(--color-text-base)" @click="load(page + 1)">›</button>
        </div>
      </div>
    </div>

    <!-- Create ticket modal -->
    <div v-if="showCreate" class="fixed inset-0 z-50 flex items-center justify-center p-4" style="background-color:rgba(0,0,0,.5)">
      <div class="w-full max-w-lg rounded-2xl p-6 space-y-4" style="background-color:var(--color-surface-01)">
        <h3 class="font-bold text-base" style="color:var(--color-text-base)">Tạo Ticket mới</h3>

        <!-- User search -->
        <div class="space-y-1">
          <label class="text-xs font-semibold" style="color:var(--color-text-muted)">Người dùng</label>
          <div class="flex gap-2">
            <input v-model="form.userSearch" type="text" placeholder="Email hoặc SĐT..." class="flex-1 rounded-xl px-3 py-2 text-sm border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" @keyup.enter="searchUser" />
            <button class="text-sm px-3 py-2 rounded-xl" style="background-color:var(--color-surface-03);color:var(--color-text-base)" @click="searchUser">Tìm</button>
          </div>
          <div v-if="foundUsers.length" class="rounded-xl border overflow-hidden" style="border-color:var(--color-surface-04)">
            <div v-for="u in foundUsers" :key="u.id" class="px-3 py-2 text-sm cursor-pointer hover:opacity-80" :style="form.userId === u.id ? 'background-color:color-mix(in srgb,#3b82f6 25%,transparent);color:#60a5fa' : 'background-color:var(--color-surface-02);color:var(--color-text-base)'" @click="selectUser(u)">
              {{ u.email }} — {{ u.full_name }}
            </div>
          </div>
          <p v-if="form.userId" class="text-xs" style="color:#4ade80">✓ Đã chọn: {{ form.userEmail }}</p>
        </div>

        <div class="space-y-1">
          <label class="text-xs font-semibold" style="color:var(--color-text-muted)">Tiêu đề</label>
          <input v-model="form.subject" type="text" maxlength="200" class="w-full rounded-xl px-3 py-2 text-sm border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div class="space-y-1">
            <label class="text-xs font-semibold" style="color:var(--color-text-muted)">Danh mục</label>
            <select v-model="form.category" class="w-full rounded-xl px-3 py-2 text-sm border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)">
              <option value="account">account</option>
              <option value="payment">payment</option>
              <option value="technical">technical</option>
              <option value="content">content</option>
              <option value="other">other</option>
            </select>
          </div>
          <div class="space-y-1">
            <label class="text-xs font-semibold" style="color:var(--color-text-muted)">Ưu tiên</label>
            <select v-model="form.priority" class="w-full rounded-xl px-3 py-2 text-sm border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)">
              <option value="low">Thấp</option>
              <option value="medium">Trung bình</option>
              <option value="high">Cao</option>
              <option value="urgent">Khẩn</option>
            </select>
          </div>
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold" style="color:var(--color-text-muted)">Mô tả</label>
          <textarea v-model="form.description" rows="4" class="w-full rounded-xl px-3 py-2 text-sm border resize-none" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" />
        </div>
        <p v-if="createErr" class="text-xs" style="color:#f87171">{{ createErr }}</p>
        <div class="flex gap-2 justify-end">
          <button class="text-sm px-4 py-2 rounded-xl" style="background-color:var(--color-surface-03);color:var(--color-text-base)" @click="closeCreate">Huỷ</button>
          <button :disabled="creating" class="text-sm font-semibold px-4 py-2 rounded-xl hover:opacity-80 disabled:opacity-50" style="background-color:#3b82f6;color:#fff" @click="submitCreate">{{ creating ? 'Đang tạo...' : 'Tạo' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { supportApi } from '@/api/support.js'

const router = useRouter()
const tickets = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const totalPages = ref(1)
const pageSize = 20
const filters = reactive({ search: '', status: '', priority: '', assigned_to: '' })
const showCreate = ref(false)
const creating = ref(false)
const createErr = ref('')
const foundUsers = ref([])
const form = reactive({ userId: null, userEmail: '', userSearch: '', subject: '', description: '', category: 'account', priority: 'medium' })

function statusStyle(s) { const m = { open: '#60a5fa,#3b82f6', in_progress: '#fbbf24,#f59e0b', waiting_customer: '#c084fc,#a855f7', resolved: '#4ade80,#22c55e', closed: '#6b7280,#4b5563' }; const [fg, bg] = (m[s] ?? '').split(','); return `background-color:color-mix(in srgb,${bg} 20%,transparent);color:${fg}` }
function statusLabel(s) { return { open: 'Open', in_progress: 'In Progress', waiting_customer: 'Chờ KH', resolved: 'Resolved', closed: 'Closed' }[s] ?? s }
function priorityStyle(p) { return { low: 'color:#4ade80', medium: 'color:#fbbf24', high: 'color:#fb923c', urgent: 'color:#f87171' }[p] ?? '' }
function priorityIcon(p) { return { low: '▽', medium: '◈', high: '▲', urgent: '🔴' }[p] ?? '' }
function slaLabel(ts, overdue) {
  const diff = new Date(ts) - Date.now()
  if (overdue || diff < 0) return 'Quá hạn'
  const h = Math.floor(diff / 3600000)
  return h < 1 ? '< 1h' : `${h}h`
}

async function load(p = 1) {
  page.value = p
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (filters.search) params.search = filters.search
    if (filters.status) params.status = filters.status
    if (filters.priority) params.priority = filters.priority
    if (filters.assigned_to) params.assigned_to = filters.assigned_to
    const { data } = await supportApi.getTickets(params)
    const payload = data.data ?? data
    tickets.value = payload.results ?? payload
    total.value = payload.count ?? tickets.value.length
    totalPages.value = Math.ceil(total.value / pageSize) || 1
  } catch { tickets.value = [] }
  finally { loading.value = false }
}

async function searchUser() {
  if (!form.userSearch.trim()) return
  try {
    const { data } = await supportApi.searchUsers({ search: form.userSearch.trim(), page_size: 5 })
    const p = data.data ?? data
    foundUsers.value = p.results ?? p
  } catch { foundUsers.value = [] }
}

function selectUser(u) { form.userId = u.id; form.userEmail = u.email; foundUsers.value = [] }
function closeCreate() { showCreate.value = false; createErr.value = ''; foundUsers.value = [] }

async function submitCreate() {
  if (!form.userId || !form.subject || !form.description) { createErr.value = 'Vui lòng điền đầy đủ thông tin.'; return }
  creating.value = true; createErr.value = ''
  try {
    const { data } = await supportApi.createTicket({ user: form.userId, subject: form.subject, description: form.description, category: form.category, priority: form.priority })
    const d = data.data ?? data
    closeCreate()
    router.push(`/support/tickets/${d.id}`)
  } catch (e) { createErr.value = e?.response?.data?.detail ?? 'Tạo ticket thất bại.' }
  finally { creating.value = false }
}

onMounted(() => load())
</script>
