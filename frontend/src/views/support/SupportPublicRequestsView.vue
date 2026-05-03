<template>
  <div class="space-y-5">
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
      <div>
        <h2 class="text-xl font-black" style="font-family: Nunito, sans-serif; color: var(--color-text-base)">
          Yêu cầu công khai chưa đăng nhập
        </h2>
        <p class="text-sm mt-1" style="color: var(--color-text-muted)">
          Hàng đợi yêu cầu từ form công khai. Chuyển thành ticket để xử lý chính thức.
        </p>
      </div>
    </div>

    <div class="rounded-2xl p-4" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
      <div class="grid md:grid-cols-4 gap-3">
        <input
          v-model="filters.search"
          type="text"
          placeholder="Tìm theo tên/email/số điện thoại"
          class="md:col-span-2 px-3 py-2 rounded-xl text-sm outline-none border"
          style="background-color: var(--color-surface-03); color: var(--color-text-base); border-color: var(--color-surface-04)"
          @keyup.enter="fetchRequests"
        />

        <select
          v-model="filters.status"
          class="px-3 py-2 rounded-xl text-sm outline-none border"
          style="background-color: var(--color-surface-03); color: var(--color-text-base); border-color: var(--color-surface-04)"
          @change="fetchRequests"
        >
          <option value="">Tất cả trạng thái</option>
          <option value="new">Mới</option>
          <option value="auto_converted">Đã tự chuyển ticket</option>
          <option value="triaged">Đã triaged</option>
          <option value="closed">Đã đóng</option>
          <option value="spam_rejected">Spam</option>
        </select>

        <button
          class="px-3 py-2 rounded-xl text-sm font-semibold text-white"
          style="background: linear-gradient(135deg, #3b82f6, #2563eb)"
          @click="fetchRequests"
        >
          Lọc dữ liệu
        </button>
      </div>
    </div>

    <div v-if="error" class="rounded-xl p-3 text-sm" style="background-color: color-mix(in srgb, #ef4444 12%, transparent); color: #f87171">
      {{ error }}
    </div>

    <div class="rounded-2xl overflow-hidden" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
      <div v-if="loading" class="p-5 space-y-2">
        <div v-for="n in 5" :key="n" class="h-14 rounded-xl animate-pulse" style="background-color: var(--color-surface-03)" />
      </div>

      <template v-else>
        <div v-if="items.length" class="divide-y" style="border-color: var(--color-surface-04)">
          <div v-for="req in items" :key="req.id" class="p-4 lg:p-5">
            <div class="flex flex-col lg:flex-row lg:items-start gap-3 lg:gap-5">
              <div class="flex-1 min-w-0">
                <div class="flex items-center flex-wrap gap-2">
                  <p class="text-sm font-semibold" style="color: var(--color-text-base)">#{{ req.id }} · {{ req.subject }}</p>
                  <span class="text-[11px] px-2 py-0.5 rounded-full" :style="statusStyle(req.status)">{{ statusLabel(req.status) }}</span>
                </div>
                <p class="text-xs mt-1" style="color: var(--color-text-soft)">
                  {{ req.full_name }} · {{ req.email || 'Không có email' }} · {{ req.phone || 'Không có số điện thoại' }}
                </p>
                <p class="text-xs mt-1" style="color: var(--color-text-soft)">
                  Nhóm: {{ issueLabel(req.issue_type) }} · {{ formatDate(req.created_at) }}
                </p>
                <p class="text-sm mt-2 whitespace-pre-wrap" style="color: var(--color-text-muted)">{{ req.description }}</p>

                <div v-if="req.linked_ticket_id" class="text-xs mt-2" style="color: #60a5fa">
                  Đã liên kết ticket: #{{ req.linked_ticket_id }}
                </div>
              </div>

              <div class="w-full lg:w-64 space-y-2">
                <input
                  v-model="draftUserId[req.id]"
                  type="number"
                  min="1"
                  placeholder="Nhập user_id để chuyển ticket"
                  class="w-full px-3 py-2 rounded-xl text-xs outline-none border"
                  style="background-color: var(--color-surface-03); color: var(--color-text-base); border-color: var(--color-surface-04)"
                />

                <button
                  class="w-full px-3 py-2 rounded-xl text-xs font-semibold text-white disabled:opacity-50"
                  style="background: linear-gradient(135deg, #f59e0b, #d97706)"
                  :disabled="req.linked_ticket_id || convertingId === req.id"
                  @click="convertRequest(req.id)"
                >
                  {{ convertingId === req.id ? 'Đang chuyển...' : req.linked_ticket_id ? 'Đã chuyển' : 'Chuyển thành ticket' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="p-8 text-center text-sm" style="color: var(--color-text-muted)">
          Không có yêu cầu phù hợp bộ lọc.
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { supportApi } from '@/api/support.js'

const loading = ref(true)
const error = ref('')
const convertingId = ref(null)
const items = ref([])
const draftUserId = reactive({})
const filters = reactive({ search: '', status: 'new' })

function statusLabel(status) {
  return {
    new: 'Mới',
    auto_converted: 'Đã tự chuyển',
    triaged: 'Đã triaged',
    closed: 'Đã đóng',
    spam_rejected: 'Spam',
  }[status] || status
}

function statusStyle(status) {
  const map = {
    new: 'background-color:color-mix(in srgb,#3b82f6 18%,transparent);color:#60a5fa',
    auto_converted: 'background-color:color-mix(in srgb,#16a34a 18%,transparent);color:#4ade80',
    triaged: 'background-color:color-mix(in srgb,#f59e0b 20%,transparent);color:#fbbf24',
    closed: 'background-color:color-mix(in srgb,#6b7280 20%,transparent);color:#9ca3af',
    spam_rejected: 'background-color:color-mix(in srgb,#ef4444 20%,transparent);color:#f87171',
  }
  return map[status] || map.new
}

function issueLabel(issue) {
  return {
    account_access: 'Tài khoản',
    payment: 'Thanh toán',
    technical: 'Kỹ thuật',
    learning: 'Học tập',
    other: 'Khác',
  }[issue] || issue
}

function formatDate(ts) {
  if (!ts) return '—'
  return new Date(ts).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' })
}

async function fetchRequests() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filters.search.trim()) params.search = filters.search.trim()
    if (filters.status) params.status = filters.status
    const { data } = await supportApi.getPublicRequests(params)
    const payload = data.data ?? data
    items.value = payload.results || payload || []
  } catch {
    error.value = 'Không thể tải danh sách yêu cầu công khai.'
  } finally {
    loading.value = false
  }
}

async function convertRequest(requestId) {
  convertingId.value = requestId
  error.value = ''
  try {
    const userId = draftUserId[requestId] ? Number(draftUserId[requestId]) : undefined
    const payload = userId ? { user_id: userId } : {}
    await supportApi.convertPublicRequest(requestId, payload)
    await fetchRequests()
  } catch (err) {
    const body = err.response?.data || {}
    error.value = body.detail || 'Không thể chuyển yêu cầu thành ticket.'
  } finally {
    convertingId.value = null
  }
}

onMounted(fetchRequests)
</script>
