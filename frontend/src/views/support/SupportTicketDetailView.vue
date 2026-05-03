<template>
  <div class="space-y-5">
    <!-- Back -->
    <RouterLink to="/support/tickets" class="text-sm hover:opacity-70" style="color:#60a5fa">← Danh sách tickets</RouterLink>

    <div v-if="loading" class="space-y-3">
      <div v-for="n in 3" :key="n" class="h-24 animate-pulse rounded-2xl" style="background-color:var(--color-surface-02)" />
    </div>

    <template v-else-if="ticket">
      <!-- Header -->
      <div class="rounded-2xl p-5" style="background-color:var(--color-surface-02)">
        <div class="flex flex-wrap items-start gap-3 justify-between">
          <div class="flex-1 min-w-0">
            <h2 class="font-bold text-lg truncate" style="color:var(--color-text-base)">#{{ ticket.id }} — {{ ticket.subject }}</h2>
            <p class="text-xs mt-1" style="color:var(--color-text-muted)">{{ ticket.user_email }} · {{ formatDate(ticket.created_at) }}</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <span class="text-xs px-2.5 py-1 rounded-full" :style="statusStyle(ticket.status)">{{ statusLabel(ticket.status) }}</span>
            <span class="text-xs px-2.5 py-1 rounded-full font-semibold" :style="priorityStyle(ticket.priority)">{{ priorityIcon(ticket.priority) }} {{ ticket.priority }}</span>
            <span v-if="ticket.is_overdue" class="text-xs px-2.5 py-1 rounded-full" style="background-color:color-mix(in srgb,#ef4444 20%,transparent);color:#f87171">⚠ Quá hạn SLA</span>
          </div>
        </div>

        <!-- Actions bar -->
        <div class="mt-4 pt-4 border-t flex flex-wrap gap-3 items-center" style="border-color:var(--color-surface-04)">
          <div class="flex items-center gap-2">
            <label class="text-xs font-semibold" style="color:var(--color-text-muted)">Trạng thái:</label>
            <select v-model="editStatus" class="text-xs rounded-lg px-2 py-1.5 border" style="background-color:var(--color-surface-03);border-color:var(--color-surface-04);color:var(--color-text-base)" @change="updateStatus">
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="waiting_customer">Chờ KH</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          <div class="flex items-center gap-2">
            <label class="text-xs font-semibold" style="color:var(--color-text-muted)">Ưu tiên:</label>
            <select v-model="editPriority" class="text-xs rounded-lg px-2 py-1.5 border" style="background-color:var(--color-surface-03);border-color:var(--color-surface-04);color:var(--color-text-base)" @change="updatePriority">
              <option value="low">Thấp</option>
              <option value="medium">Trung bình</option>
              <option value="high">Cao</option>
              <option value="urgent">Khẩn</option>
            </select>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs" style="color:var(--color-text-muted)">Giao cho: <span style="color:var(--color-text-base)">{{ ticket.assigned_to_name ?? 'Chưa giao' }}</span></span>
            <button class="text-xs px-3 py-1.5 rounded-lg hover:opacity-80" style="background-color:color-mix(in srgb,#3b82f6 20%,transparent);color:#60a5fa" @click="assignToMe">Giao cho tôi</button>
          </div>
          <p v-if="actionMsg" class="text-xs ml-auto" :style="actionOk ? 'color:#4ade80' : 'color:#f87171'">{{ actionMsg }}</p>
        </div>
      </div>

      <!-- Ticket info -->
      <div class="rounded-2xl p-5 grid sm:grid-cols-2 gap-x-6 gap-y-2 text-sm" style="background-color:var(--color-surface-02)">
        <div>
          <span style="color:var(--color-text-soft)">Khách hàng:</span>
          <span class="ml-1 font-medium" style="color:var(--color-text-base)">
            {{ ticket.user_email }} <span style="color:var(--color-text-soft)">(#{{ ticket.user_id }})</span>
          </span>
        </div>
        <div>
          <span style="color:var(--color-text-soft)">Danh mục:</span>
          <span class="ml-1" style="color:var(--color-text-base)">{{ categoryLabel(ticket.category) }}</span>
        </div>
        <div>
          <span style="color:var(--color-text-soft)">Hạn SLA:</span>
          <span class="ml-1" :style="ticket.is_overdue ? 'color:#f87171' : 'color:var(--color-text-base)'">{{ formatDate(ticket.sla_deadline) }}</span>
          <span class="text-xs ml-1" style="color:var(--color-text-soft)">(giờ hành chính, T2-T7)</span>
        </div>
        <div v-if="ticket.resolved_at">
          <span style="color:var(--color-text-soft)">Đã giải quyết:</span>
          <span class="ml-1" style="color:#4ade80">{{ formatDate(ticket.resolved_at) }}</span>
        </div>
      </div>

      <!-- Initial description -->
      <div v-if="ticket.description" class="rounded-2xl p-5" style="background-color:var(--color-surface-02)">
        <h4 class="text-sm font-semibold mb-2" style="color:var(--color-text-muted)">Mô tả ban đầu</h4>
        <p class="text-sm whitespace-pre-wrap leading-relaxed" style="color:var(--color-text-base)">{{ ticket.description }}</p>
      </div>

      <!-- Message thread -->
      <div class="rounded-2xl overflow-hidden" style="background-color:var(--color-surface-02)">
        <div class="px-5 pt-5 pb-2">
          <h4 class="font-semibold text-sm" style="color:var(--color-text-base)">Hội thoại</h4>
        </div>
        <div class="px-5 pb-3 space-y-3">
          <div
            v-for="msg in ticket.messages"
            :key="msg.id"
            class="rounded-xl p-4"
            :style="msg.is_internal ? 'background-color:color-mix(in srgb,#f59e0b 10%,transparent);border:1px solid color-mix(in srgb,#f59e0b 25%,transparent)' : 'background-color:var(--color-surface-03)'"
          >
            <div class="flex items-center gap-2 mb-1.5">
              <span class="text-xs font-semibold" style="color:var(--color-text-base)">{{ msg.author_name }}</span>
              <span v-if="msg.is_internal" class="text-xs px-1.5 py-0.5 rounded" style="background-color:color-mix(in srgb,#f59e0b 30%,transparent);color:#fbbf24">Internal</span>
              <span class="text-xs ml-auto" style="color:var(--color-text-muted)">{{ formatDate(msg.created_at) }}</span>
            </div>
            <p class="text-sm whitespace-pre-wrap" style="color:var(--color-text-base)">{{ msg.content }}</p>
          </div>
          <div v-if="!ticket.messages?.length" class="text-sm py-4 text-center" style="color:var(--color-text-muted)">Chưa có tin nhắn nào.</div>
        </div>

        <!-- Reply box -->
        <div class="px-5 pb-5 border-t pt-4" style="border-color:var(--color-surface-04)">
          <textarea
            v-model="replyContent"
            rows="3"
            placeholder="Nhập nội dung phản hồi..."
            class="w-full rounded-xl px-3 py-2.5 text-sm border resize-none"
            style="background-color:var(--color-surface-03);border-color:var(--color-surface-04);color:var(--color-text-base)"
          />
          <div class="mt-2 flex items-center gap-3 justify-between">
            <label class="flex items-center gap-2 text-xs cursor-pointer" style="color:var(--color-text-muted)">
              <input v-model="isInternal" type="checkbox" class="rounded" />
              Ghi chú nội bộ (không thông báo KH)
            </label>
            <button :disabled="replying || !replyContent.trim()" class="text-sm font-semibold px-4 py-2 rounded-xl hover:opacity-80 disabled:opacity-50" style="background-color:#3b82f6;color:#fff" @click="sendReply">
              {{ replying ? 'Đang gửi...' : 'Gửi' }}
            </button>
          </div>
          <div v-if="!isInternal && ticket.user_email" class="text-xs mt-1.5" style="color:var(--color-primary-300)">
            📧 Phản hồi này sẽ gửi email tới <strong>{{ ticket.user_email }}</strong>
          </div>
          <p v-if="lastEmailSent" class="text-xs mt-1" style="color:#4ade80">✓ Email đã gửi tới {{ ticket.user_email }}</p>
          <p v-if="replyErr" class="text-xs mt-1" style="color:#f87171">{{ replyErr }}</p>
        </div>
      </div>
    </template>
    <div v-else class="text-sm p-6" style="color:var(--color-text-muted)">Không tìm thấy ticket.</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { supportApi } from '@/api/support.js'

const route = useRoute()
const ticket = ref(null)
const loading = ref(true)
const editStatus = ref('')
const editPriority = ref('')
const replyContent = ref('')
const isInternal = ref(false)
const replying = ref(false)
const replyErr = ref('')
const actionMsg = ref('')
const actionOk = ref(true)
const lastEmailSent = ref(false)

function statusStyle(s) { const m = { open: '#60a5fa,#3b82f6', in_progress: '#fbbf24,#f59e0b', waiting_customer: '#c084fc,#a855f7', resolved: '#4ade80,#22c55e', closed: '#6b7280,#4b5563' }; const [fg, bg] = (m[s] ?? '').split(','); return `background-color:color-mix(in srgb,${bg} 20%,transparent);color:${fg}` }
function statusLabel(s) { return { open: 'Open', in_progress: 'In Progress', waiting_customer: 'Chờ KH', resolved: 'Resolved', closed: 'Closed' }[s] ?? s }
function priorityStyle(p) { return { low: 'color:#4ade80', medium: 'color:#fbbf24', high: 'color:#fb923c', urgent: 'color:#f87171' }[p] ?? '' }
function priorityIcon(p) { return { low: '▽', medium: '◈', high: '▲', urgent: '🔴' }[p] ?? '' }
function formatDate(ts) { return ts ? new Date(ts).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' }) : '—' }
function categoryLabel(c) { return { account: 'Tài khoản', payment: 'Thanh toán', technical: 'Kỹ thuật', content: 'Nội dung', other: 'Khác' }[c] ?? c }

function showAction(msg, ok = true) { actionMsg.value = msg; actionOk.value = ok; setTimeout(() => { actionMsg.value = '' }, 3000) }

async function loadTicket() {
  try {
    const { data } = await supportApi.getTicketDetail(route.params.id)
    ticket.value = data.data ?? data
    editStatus.value = ticket.value.status
    editPriority.value = ticket.value.priority
  } catch { ticket.value = null }
  finally { loading.value = false }
}

async function updateStatus() {
  try {
    const { data } = await supportApi.updateTicket(route.params.id, { status: editStatus.value })
    ticket.value = { ...ticket.value, ...(data.data ?? data) }
    showAction('Đã cập nhật trạng thái.')
  } catch { showAction('Lỗi cập nhật.', false) }
}
async function updatePriority() {
  try {
    const { data } = await supportApi.updateTicket(route.params.id, { priority: editPriority.value })
    ticket.value = { ...ticket.value, ...(data.data ?? data) }
    showAction('Đã cập nhật ưu tiên.')
  } catch { showAction('Lỗi cập nhật.', false) }
}
async function assignToMe() {
  try {
    const { data } = await supportApi.assignTicket(route.params.id, {})
    ticket.value = { ...ticket.value, ...(data.data ?? data) }
    showAction('Đã giao cho bạn.')
  } catch (e) { showAction(e?.response?.data?.detail ?? 'Lỗi giao ticket.', false) }
}

async function sendReply() {
  if (!replyContent.value.trim()) return
  replying.value = true; replyErr.value = ''; lastEmailSent.value = false
  try {
    const { data } = await supportApi.addTicketMessage(route.params.id, { content: replyContent.value, is_internal: isInternal.value })
    const msg = data.data ?? data
    if (!ticket.value.messages) ticket.value.messages = []
    ticket.value.messages.push(msg)
    lastEmailSent.value = Boolean(msg.email_sent)
    replyContent.value = ''
    isInternal.value = false
    // refresh ticket header for status update
    const { data: td } = await supportApi.getTicketDetail(route.params.id)
    const updated = td.data ?? td
    editStatus.value = updated.status
    ticket.value = { ...updated, messages: ticket.value.messages }
  } catch (e) { replyErr.value = e?.response?.data?.detail ?? 'Gửi thất bại.' }
  finally { replying.value = false }
}

onMounted(loadTicket)
</script>
