<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h2 class="text-xl font-bold" style="color: var(--color-text-base)">Tổng quan hỗ trợ</h2>
      <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">Thống kê và công việc hôm nay</p>
    </div>

    <!-- KPI Cards -->
    <div v-if="loading" class="grid grid-cols-2 lg:grid-cols-5 gap-4">
      <div v-for="n in 5" :key="n" class="rounded-2xl p-5 animate-pulse h-24" style="background-color: var(--color-surface-02)" />
    </div>
    <div v-else class="grid grid-cols-2 lg:grid-cols-5 gap-4">
      <div
        v-for="card in kpiCards"
        :key="card.label"
        class="rounded-2xl p-5 flex flex-col gap-2"
        style="background-color: var(--color-surface-02)"
      >
        <span class="text-2xl">{{ card.icon }}</span>
        <div class="text-2xl font-bold" :style="{ color: card.color || 'var(--color-text-base)' }">{{ card.value }}</div>
        <div class="text-xs" style="color: var(--color-text-muted)">{{ card.label }}</div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- My assigned tickets -->
      <div class="rounded-2xl p-5" style="background-color: var(--color-surface-02)">
        <h3 class="text-sm font-semibold mb-4" style="color: var(--color-text-base)">🎫 Ticket được giao cho tôi</h3>
        <div v-if="loading" class="space-y-2">
          <div v-for="n in 3" :key="n" class="h-12 rounded-xl animate-pulse" style="background-color: var(--color-surface-03)" />
        </div>
        <div v-else class="space-y-2">
          <RouterLink
            v-for="t in stats.my_recent_tickets"
            :key="t.id"
            :to="`/support/tickets/${t.id}`"
            class="flex items-center gap-3 p-3 rounded-xl hover:opacity-80 transition"
            style="background-color: var(--color-surface-03)"
          >
            <span class="shrink-0 text-base">{{ priorityIcon(t.priority) }}</span>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-medium truncate" style="color: var(--color-text-base)">{{ t.subject }}</p>
              <p class="text-xs" style="color: var(--color-text-muted)">{{ t.user_email }}</p>
            </div>
            <span class="text-xs px-2 py-0.5 rounded-full shrink-0" :style="statusStyle(t.status)">{{ statusLabel(t.status) }}</span>
          </RouterLink>
          <p v-if="!stats.my_recent_tickets?.length" class="text-xs text-center py-4" style="color: var(--color-text-muted)">Chưa có ticket nào được giao.</p>
        </div>
        <RouterLink to="/support/tickets?assigned_to=me" class="block mt-3 text-xs text-center hover:opacity-80" style="color: #60a5fa">Xem tất cả →</RouterLink>
      </div>

      <!-- Overdue tickets -->
      <div class="rounded-2xl p-5" style="background-color: var(--color-surface-02)">
        <h3 class="text-sm font-semibold mb-4" style="color: var(--color-text-base)">⏰ Ticket quá hạn SLA</h3>
        <div v-if="loading" class="space-y-2">
          <div v-for="n in 3" :key="n" class="h-12 rounded-xl animate-pulse" style="background-color: var(--color-surface-03)" />
        </div>
        <div v-else class="space-y-2">
          <RouterLink
            v-for="t in stats.overdue_tickets_list"
            :key="t.id"
            :to="`/support/tickets/${t.id}`"
            class="flex items-center gap-3 p-3 rounded-xl hover:opacity-80 transition"
            style="background-color: var(--color-surface-03)"
          >
            <span class="shrink-0 text-base">🔴</span>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-medium truncate" style="color: var(--color-text-base)">{{ t.subject }}</p>
              <p class="text-xs" style="color: var(--color-text-muted)">SLA: {{ formatDate(t.sla_deadline) }}</p>
            </div>
            <span class="text-xs px-2 py-0.5 rounded-full shrink-0" style="background-color: color-mix(in srgb,#ef4444 20%,transparent);color:#f87171">Quá hạn</span>
          </RouterLink>
          <p v-if="!stats.overdue_tickets_list?.length" class="text-xs text-center py-4" style="color: var(--color-text-muted)">Không có ticket quá hạn. 🎉</p>
        </div>
        <RouterLink to="/support/tickets" class="block mt-3 text-xs text-center hover:opacity-80" style="color: #60a5fa">Xem tất cả ticket →</RouterLink>
      </div>
    </div>

    <div v-if="error" class="rounded-2xl p-4 text-sm" style="background-color: color-mix(in srgb,#ef4444 12%,transparent);color:#f87171">{{ error }}</div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { supportApi } from '@/api/support.js'

const loading = ref(true)
const error = ref(null)
const stats = reactive({ stats: {}, my_recent_tickets: [], overdue_tickets_list: [] })

const kpiCards = computed(() => {
  const s = stats.stats || {}
  return [
    { icon: '🎫', value: s.open_tickets ?? '—', label: 'Ticket đang mở', color: s.open_tickets > 0 ? '#60a5fa' : undefined },
    { icon: '👤', value: s.my_tickets ?? '—', label: 'Ticket của tôi' },
    { icon: '↩️', value: s.pending_refunds ?? '—', label: 'Hoàn tiền chờ duyệt', color: s.pending_refunds > 0 ? '#facc15' : undefined },
    { icon: '✅', value: s.resolved_today ?? '—', label: 'Đã giải quyết hôm nay', color: '#4ade80' },
    { icon: '⏰', value: s.overdue_tickets ?? '—', label: 'Quá hạn SLA', color: s.overdue_tickets > 0 ? '#f87171' : undefined },
  ]
})

function priorityIcon(p) { return { urgent: '🔴', high: '🟠', medium: '🟡', low: '🟢' }[p] || '⚪' }
function statusLabel(s) { return { open: 'Mở', in_progress: 'Đang xử lý', waiting_customer: 'Chờ KH', resolved: 'Đã giải quyết', closed: 'Đóng' }[s] || s }
function statusStyle(s) {
  const map = {
    open: 'background-color:color-mix(in srgb,#3b82f6 20%,transparent);color:#60a5fa',
    in_progress: 'background-color:color-mix(in srgb,#f59e0b 20%,transparent);color:#fbbf24',
    waiting_customer: 'background-color:color-mix(in srgb,#8b5cf6 20%,transparent);color:#a78bfa',
    resolved: 'background-color:color-mix(in srgb,#22c55e 20%,transparent);color:#4ade80',
    closed: 'background-color:color-mix(in srgb,#6b7280 20%,transparent);color:#9ca3af',
  }
  return map[s] || ''
}
function formatDate(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' })
}

async function fetchDashboard() {
  loading.value = true
  error.value = null
  try {
    const { data } = await supportApi.getDashboard()
    const payload = data.data ?? data
    Object.assign(stats, payload)
  } catch {
    error.value = 'Không thể tải dữ liệu. Vui lòng thử lại.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchDashboard)
</script>
