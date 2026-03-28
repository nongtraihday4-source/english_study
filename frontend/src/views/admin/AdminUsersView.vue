<template>
  <div class="space-y-5">
    <!-- Header -->
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h2 class="text-xl font-bold" style="color: var(--color-text-base)">Quản lý người dùng</h2>
        <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">
          {{ total }} người dùng
        </p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 p-1 rounded-xl w-fit" style="background-color: var(--color-surface-02)">
      <button
        v-for="tab in TABS" :key="tab.key" @click="activeTab = tab.key"
        class="px-4 py-2 text-sm rounded-lg font-medium transition-all"
        :style="activeTab === tab.key
          ? 'background-color:var(--color-primary-500);color:#fff'
          : 'color:var(--color-text-muted)'"
      >{{ tab.label }}</button>
    </div>

    <!-- ══════════════════════════════════════════════════════════ -->
    <!-- TAB: Người dùng                                           -->
    <!-- ══════════════════════════════════════════════════════════ -->
    <template v-if="activeTab === 'users'">
      <!-- Filters -->
      <div class="flex flex-wrap gap-3">
        <input
          v-model="filters.search"
          type="text"
          placeholder="Tìm email, tên..."
          class="rounded-xl px-3 py-2 text-sm border outline-none"
          style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)"
          @input="debouncedFetch"
        />
        <select
          v-model="filters.role"
          class="rounded-xl px-3 py-2 text-sm border outline-none"
          style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)"
          @change="fetchUsers"
        >
          <option value="">Tất cả vai trò</option>
          <option value="admin">Admin</option>
          <option value="teacher">Giáo viên</option>
          <option value="student">Học viên</option>
        </select>
        <select
          v-model="filters.account_type"
          class="rounded-xl px-3 py-2 text-sm border outline-none"
          style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)"
          @change="fetchUsers"
        >
          <option value="">Tất cả loại TK</option>
          <option value="demo">Demo</option>
          <option value="premium">Premium</option>
        </select>
        <select
          v-model="filters.is_active"
          class="rounded-xl px-3 py-2 text-sm border outline-none"
          style="background-color: var(--color-surface-02); border-color: var(--color-surface-04); color: var(--color-text-base)"
          @change="fetchUsers"
        >
          <option value="">Tất cả trạng thái</option>
          <option value="true">Đang hoạt động</option>
          <option value="false">Đã khoá</option>
        </select>
      </div>

      <!-- Table -->
      <div class="rounded-2xl overflow-hidden border" style="border-color: var(--color-surface-04)">
        <div v-if="loading" class="p-8 text-center text-sm" style="color: var(--color-text-muted)">
          Đang tải...
        </div>
        <div v-else-if="!users.length" class="p-8 text-center text-sm" style="color: var(--color-text-muted)">
          Không có người dùng nào.
        </div>
        <table v-else class="w-full text-sm border-collapse">
          <thead>
            <tr style="background-color: var(--color-surface-02); border-bottom: 1px solid var(--color-surface-04)">
              <th class="text-left px-4 py-3 font-semibold" style="color: var(--color-text-muted)">Email</th>
              <th class="text-left px-4 py-3 font-semibold" style="color: var(--color-text-muted)">Tên</th>
              <th class="text-left px-4 py-3 font-semibold" style="color: var(--color-text-muted)">Vai trò</th>
              <th class="text-left px-4 py-3 font-semibold hidden sm:table-cell" style="color: var(--color-text-muted)">Loại TK</th>
              <th class="text-left px-4 py-3 font-semibold hidden md:table-cell" style="color: var(--color-text-muted)">Ngày đăng ký</th>
              <th class="text-left px-4 py-3 font-semibold" style="color: var(--color-text-muted)">Trạng thái</th>
              <th class="text-right px-4 py-3 font-semibold" style="color: var(--color-text-muted)">Thao tác</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in users"
              :key="user.id"
              class="border-t transition hover:opacity-90"
              style="border-color: var(--color-surface-04); background-color: var(--color-surface-01)"
            >
              <td class="px-4 py-3" style="color: var(--color-text-base)">{{ user.email }}</td>
              <td class="px-4 py-3" style="color: var(--color-text-base)">
                {{ [user.first_name, user.last_name].filter(Boolean).join(' ') || '—' }}
              </td>
              <!-- Editable role cell -->
              <td class="px-4 py-3">
                <select
                  v-if="editingRoleId === user.id"
                  v-model="editingRoleValue"
                  class="rounded-lg px-2 py-1 text-xs border outline-none"
                  style="background-color: var(--color-surface-03); border-color: var(--color-surface-04); color: var(--color-text-base)"
                  @change="saveRole(user)"
                  @blur="cancelEditRole"
                >
                  <option value="student">student</option>
                  <option value="teacher">teacher</option>
                  <option value="admin">admin</option>
                </select>
                <button
                  v-else
                  class="text-xs px-2 py-1 rounded-full font-medium cursor-pointer transition hover:opacity-80"
                  :style="roleBadgeStyle(user.role)"
                  @click="startEditRole(user)"
                >{{ user.role }}</button>
              </td>
              <td class="px-4 py-3 hidden sm:table-cell">
                <span
                  class="text-xs px-2 py-0.5 rounded-full font-medium"
                  :style="accountTypeBadgeStyle(user.account_type)"
                >{{ user.account_type }}</span>
              </td>
              <td class="px-4 py-3 hidden md:table-cell text-xs" style="color: var(--color-text-muted)">
                {{ formatDate(user.date_joined) }}
              </td>
              <td class="px-4 py-3">
                <span
                  class="text-xs px-2 py-0.5 rounded-full font-medium"
                  :style="user.is_active
                    ? 'background-color:color-mix(in srgb,#22c55e 18%,transparent);color:#4ade80'
                    : 'background-color:color-mix(in srgb,#ef4444 18%,transparent);color:#f87171'"
                >{{ user.is_active ? 'Hoạt động' : 'Đã khoá' }}</span>
              </td>
              <td class="px-4 py-3 text-right">
                <button
                  class="text-xs px-3 py-1.5 rounded-lg font-medium transition hover:opacity-80"
                  :style="user.is_active
                    ? 'background-color:color-mix(in srgb,#ef4444 16%,transparent);color:#f87171'
                    : 'background-color:color-mix(in srgb,#22c55e 16%,transparent);color:#4ade80'"
                  :disabled="banLoading === user.id"
                  @click="toggleBan(user)"
                >
                  {{ banLoading === user.id ? '...' : (user.is_active ? 'Khoá' : 'Mở khoá') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-center gap-2">
        <button
          class="px-3 py-1.5 text-sm rounded-lg font-medium transition hover:opacity-80 disabled:opacity-40"
          style="background-color: var(--color-surface-03); color: var(--color-text-base)"
          :disabled="page === 1"
          @click="changePage(page - 1)"
        >← Trước</button>
        <span class="text-sm" style="color: var(--color-text-muted)">{{ page }} / {{ totalPages }}</span>
        <button
          class="px-3 py-1.5 text-sm rounded-lg font-medium transition hover:opacity-80 disabled:opacity-40"
          style="background-color: var(--color-surface-03); color: var(--color-text-base)"
          :disabled="page === totalPages"
          @click="changePage(page + 1)"
        >Sau →</button>
      </div>
    </template>

    <!-- ══════════════════════════════════════════════════════════ -->
    <!-- TAB: Nhân viên & Quyền                                    -->
    <!-- ══════════════════════════════════════════════════════════ -->
    <template v-if="activeTab === 'staff'">
      <p class="text-sm" style="color: var(--color-text-muted)">
        Gán quyền truy cập module cho từng nhân viên (admin / teacher).
      </p>

      <div v-if="staffLoading" class="space-y-3">
        <div v-for="n in 3" :key="n" class="h-20 animate-pulse rounded-2xl" style="background-color:var(--color-surface-02)" />
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="member in staffUsers"
          :key="member.id"
          class="rounded-2xl p-5"
          style="background-color:var(--color-surface-02)"
        >
          <!-- Staff header row -->
          <div class="flex items-center gap-3 mb-4">
            <div class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold shrink-0"
              style="background-color:var(--color-surface-03);color:var(--color-text-base)">
              {{ (member.email?.[0] ?? '?').toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="font-medium text-sm truncate" style="color:var(--color-text-base)">{{ member.email }}</div>
              <div class="text-xs" style="color:var(--color-text-muted)">
                {{ [member.first_name, member.last_name].filter(Boolean).join(' ') || '—' }}
                <span class="ml-2 px-1.5 py-0.5 rounded font-medium" :style="roleBadgeStyle(member.role)">{{ member.role }}</span>
              </div>
            </div>
            <button
              v-if="!permissionsMap[member.id]"
              @click="loadPermissions(member)"
              class="text-xs px-3 py-1.5 rounded-lg"
              style="background-color:var(--color-surface-03);color:var(--color-text-muted)"
            >
              Tải quyền
            </button>
            <span v-else-if="permSaving[member.id]" class="text-xs" style="color:var(--color-text-muted)">Đang lưu...</span>
            <span v-else class="text-xs" style="color:#4ade80">✓ Đã lưu</span>
          </div>

          <!-- Permission grid -->
          <div v-if="permissionsMap[member.id]" class="grid grid-cols-2 sm:grid-cols-3 gap-2">
            <label
              v-for="perm in PERMISSIONS"
              :key="perm.key"
              class="flex items-center gap-2 px-3 py-2 rounded-xl cursor-pointer select-none text-xs"
              style="background-color:var(--color-surface-03)"
            >
              <input
                type="checkbox"
                :checked="permissionsMap[member.id][perm.key]"
                @change="togglePerm(member.id, perm.key, $event.target.checked)"
                class="rounded"
              />
              <span style="color:var(--color-text-muted)">{{ perm.label }}</span>
            </label>
          </div>
          <div v-else class="text-xs" style="color:var(--color-text-muted)">
            Nhấn "Tải quyền" để xem và chỉnh sửa.
          </div>
        </div>

        <div v-if="!staffUsers.length" class="text-center py-12 text-sm" style="color:var(--color-text-muted)">
          Chưa có nhân viên nào (admin / teacher).
        </div>
      </div>
    </template>

    <!-- Error -->
    <div
      v-if="error"
      class="rounded-xl p-4 text-sm"
      style="background-color:color-mix(in srgb,#ef4444 12%,transparent);color:#f87171"
    >{{ error }}</div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { adminApi } from '@/api/admin.js'

const TABS = [
  { key: 'users', label: 'Người dùng' },
  { key: 'staff', label: 'Nhân viên & Quyền' },
]
const activeTab = ref('users')

const PERMISSIONS = [
  { key: 'manage_users',         label: '👥 Người dùng' },
  { key: 'manage_content',       label: '📚 Nội dung' },
  { key: 'manage_payments',      label: '💳 Thanh toán' },
  { key: 'manage_assessments',   label: '📝 Bài thi' },
  { key: 'manage_notifications', label: '🔔 Thông báo' },
  { key: 'manage_gamification',  label: '🏆 Gamification' },
  { key: 'view_analytics',       label: '📊 Analytics' },
  { key: 'manage_settings',      label: '⚙️ Cài đặt' },
  { key: 'view_audit_log',       label: '📋 Nhật ký' },
]

// ── Users tab state ────────────────────────────────────────────────────────
const users = ref([])
const total = ref(0)
const loading = ref(false)
const error = ref(null)
const page = ref(1)
const PAGE_SIZE = 20
const totalPages = ref(1)
const banLoading = ref(null)
const editingRoleId = ref(null)
const editingRoleValue = ref('')

const filters = reactive({ search: '', role: '', account_type: '', is_active: '' })

// ── Staff tab state ────────────────────────────────────────────────────────
const staffUsers = ref([])
const staffLoading = ref(false)
const permissionsMap = reactive({})   // { userId: { manage_users: bool, ... } }
const permSaving = reactive({})       // { userId: bool }

watch(activeTab, (tab) => {
  if (tab === 'staff' && staffUsers.value.length === 0) loadStaffUsers()
})

// ── Users tab logic ────────────────────────────────────────────────────────
let debounceTimer = null
function debouncedFetch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { page.value = 1; fetchUsers() }, 350)
}

async function fetchUsers() {
  loading.value = true
  error.value = null
  try {
    const params = { page: page.value, page_size: PAGE_SIZE }
    if (filters.search) params.search = filters.search
    if (filters.role) params.role = filters.role
    if (filters.account_type) params.account_type = filters.account_type
    if (filters.is_active !== '') params.is_active = filters.is_active
    const { data } = await adminApi.getUsers(params)
    users.value = data.results ?? data
    total.value = data.count ?? users.value.length
    totalPages.value = Math.ceil(total.value / PAGE_SIZE)
  } catch {
    error.value = 'Không thể tải danh sách người dùng.'
  } finally {
    loading.value = false
  }
}

function changePage(p) { page.value = p; fetchUsers() }

function startEditRole(user) { editingRoleId.value = user.id; editingRoleValue.value = user.role }
function cancelEditRole() { setTimeout(() => { editingRoleId.value = null }, 150) }

async function saveRole(user) {
  const newRole = editingRoleValue.value
  editingRoleId.value = null
  if (newRole === user.role) return
  try {
    await adminApi.updateUser(user.id, { role: newRole })
    user.role = newRole
  } catch {
    error.value = 'Không thể cập nhật vai trò.'
  }
}

async function toggleBan(user) {
  banLoading.value = user.id
  try {
    const { data } = await adminApi.banUser(user.id)
    user.is_active = data.is_active
  } catch {
    error.value = 'Không thể thay đổi trạng thái tài khoản.'
  } finally {
    banLoading.value = null
  }
}

// ── Staff permissions logic ───────────────────────────────────────────────
async function loadStaffUsers() {
  staffLoading.value = true
  try {
    // Fetch admin + teacher users (two calls, merge)
    const [admins, teachers] = await Promise.all([
      adminApi.getUsers({ role: 'admin', page_size: 50 }),
      adminApi.getUsers({ role: 'teacher', page_size: 50 }),
    ])
    const aList = admins.data.results ?? admins.data
    const tList = teachers.data.results ?? teachers.data
    // Merge, deduplicate by id
    const seen = new Set()
    staffUsers.value = [...aList, ...tList].filter(u => {
      if (seen.has(u.id)) return false
      seen.add(u.id)
      return true
    })
  } finally {
    staffLoading.value = false
  }
}

async function loadPermissions(member) {
  try {
    const { data } = await adminApi.getStaffPermissions(member.id)
    permissionsMap[member.id] = { ...data }
  } catch {
    error.value = `Không thể tải quyền cho ${member.email}.`
  }
}

async function togglePerm(userId, permKey, checked) {
  permissionsMap[userId][permKey] = checked
  permSaving[userId] = true
  try {
    await adminApi.updateStaffPermissions(userId, permissionsMap[userId])
  } catch {
    // revert
    permissionsMap[userId][permKey] = !checked
    error.value = 'Lưu quyền thất bại.'
  } finally {
    permSaving[userId] = false
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────
function formatDate(ts) { return ts ? new Date(ts).toLocaleDateString('vi-VN') : '—' }

function roleBadgeStyle(role) {
  const map = {
    admin: 'background-color:color-mix(in srgb,#ef4444 18%,transparent);color:#f87171',
    teacher: 'background-color:color-mix(in srgb,#a855f7 18%,transparent);color:#c084fc',
    student: 'background-color:color-mix(in srgb,var(--color-primary-600) 18%,transparent);color:var(--color-primary-400)',
  }
  return map[role] || 'background-color:var(--color-surface-03);color:var(--color-text-muted)'
}

function accountTypeBadgeStyle(type) {
  return type === 'premium'
    ? 'background-color:color-mix(in srgb,#eab308 18%,transparent);color:#facc15'
    : 'background-color:var(--color-surface-03);color:var(--color-text-muted)'
}

onMounted(fetchUsers)
</script>
