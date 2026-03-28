<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h2 class="text-xl font-bold" style="color:var(--color-text-base)">Yêu cầu hoàn tiền</h2>
        <p class="text-sm mt-0.5" style="color:var(--color-text-muted)">Tạo và theo dõi yêu cầu hoàn tiền (admin duyệt)</p>
      </div>
      <button class="text-sm font-semibold px-4 py-2 rounded-xl hover:opacity-80" style="background-color:#3b82f6;color:#fff" @click="showCreate = true">+ Yêu cầu hoàn tiền</button>
    </div>

    <!-- Filter -->
    <div class="flex gap-2">
      <select v-model="statusFilter" class="rounded-xl px-3 py-2 text-sm border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" @change="load(1)">
        <option value="">Mọi trạng thái</option>
        <option value="pending">Chờ duyệt</option>
        <option value="approved">Đã duyệt</option>
        <option value="rejected">Từ chối</option>
        <option value="completed">Hoàn tất</option>
      </select>
    </div>

    <!-- Table -->
    <div class="rounded-2xl overflow-hidden" style="background-color:var(--color-surface-02)">
      <div v-if="loading" class="p-5 space-y-2"><div v-for="n in 5" :key="n" class="h-10 animate-pulse rounded-xl" style="background-color:var(--color-surface-03)" /></div>
      <table v-else-if="refunds.length" class="w-full text-sm">
        <thead><tr style="border-bottom:1px solid var(--color-surface-04)"><th v-for="h in ['#','Người dùng','Mã GD','Số tiền','Lý do','Trạng thái','Ngày tạo','Ghi chú admin']" :key="h" class="text-left px-4 py-3 text-xs font-semibold" style="color:var(--color-text-muted)">{{ h }}</th></tr></thead>
        <tbody>
          <tr v-for="r in refunds" :key="r.id" style="border-bottom:1px solid var(--color-surface-04)">
            <td class="px-4 py-3 text-xs font-mono" style="color:var(--color-text-muted)">#{{ r.id }}</td>
            <td class="px-4 py-3 text-xs" style="color:var(--color-text-base)">{{ r.requested_by_email }}</td>
            <td class="px-4 py-3 text-xs font-mono" style="color:var(--color-text-muted)">{{ r.transaction_id }}</td>
            <td class="px-4 py-3 text-xs font-semibold" style="color:var(--color-text-base)">{{ formatVND(r.amount_vnd) }}</td>
            <td class="px-4 py-3 text-xs max-w-xs truncate" style="color:var(--color-text-muted)">{{ r.reason }}</td>
            <td class="px-4 py-3"><span class="text-xs px-2 py-0.5 rounded-full" :style="refundStyle(r.status)">{{ refundLabel(r.status) }}</span></td>
            <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ formatDate(r.created_at) }}</td>
            <td class="px-4 py-3 text-xs max-w-xs truncate" style="color:var(--color-text-muted)">{{ r.notes || '—' }}</td>
          </tr>
        </tbody>
      </table>
      <div v-else class="p-8 text-center text-sm" style="color:var(--color-text-muted)">Không có yêu cầu hoàn tiền nào.</div>
      <div v-if="totalPages > 1" class="flex items-center justify-between px-4 py-3 border-t" style="border-color:var(--color-surface-04)">
        <span class="text-xs" style="color:var(--color-text-muted)">{{ total }} yêu cầu</span>
        <div class="flex gap-2">
          <button :disabled="page === 1" class="text-xs px-3 py-1.5 rounded-lg disabled:opacity-40" style="background-color:var(--color-surface-03);color:var(--color-text-base)" @click="load(page-1)">‹</button>
          <span class="text-xs py-1.5 px-2" style="color:var(--color-text-muted)">{{ page }} / {{ totalPages }}</span>
          <button :disabled="page === totalPages" class="text-xs px-3 py-1.5 rounded-lg disabled:opacity-40" style="background-color:var(--color-surface-03);color:var(--color-text-base)" @click="load(page+1)">›</button>
        </div>
      </div>
    </div>

    <!-- Create modal -->
    <div v-if="showCreate" class="fixed inset-0 z-50 flex items-center justify-center p-4" style="background-color:rgba(0,0,0,.5)">
      <div class="w-full max-w-md rounded-2xl p-6 space-y-4" style="background-color:var(--color-surface-01)">
        <h3 class="font-bold text-base" style="color:var(--color-text-base)">Tạo yêu cầu hoàn tiền</h3>
        <div class="space-y-1">
          <label class="text-xs font-semibold" style="color:var(--color-text-muted)">Mã giao dịch (transaction_id)</label>
          <input v-model="form.transactionId" type="text" placeholder="VD: TXN-XXXXXXXX..." class="w-full rounded-xl px-3 py-2 text-sm border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" />
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold" style="color:var(--color-text-muted)">Số tiền hoàn (VNĐ)</label>
          <input v-model.number="form.amount" type="number" min="0" class="w-full rounded-xl px-3 py-2 text-sm border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" />
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold" style="color:var(--color-text-muted)">Lý do hoàn tiền</label>
          <textarea v-model="form.reason" rows="3" class="w-full rounded-xl px-3 py-2 text-sm border resize-none" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" />
        </div>
        <p v-if="createErr" class="text-xs" style="color:#f87171">{{ createErr }}</p>
        <div class="flex gap-2 justify-end">
          <button class="text-sm px-4 py-2 rounded-xl" style="background-color:var(--color-surface-03);color:var(--color-text-base)" @click="closeCreate">Huỷ</button>
          <button :disabled="creating" class="text-sm font-semibold px-4 py-2 rounded-xl hover:opacity-80 disabled:opacity-50" style="background-color:#3b82f6;color:#fff" @click="submitCreate">{{ creating ? 'Đang gửi...' : 'Gửi' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { supportApi } from '@/api/support.js'

const refunds = ref([])
const loading = ref(false)
const statusFilter = ref('')
const page = ref(1)
const total = ref(0)
const totalPages = ref(1)
const showCreate = ref(false)
const creating = ref(false)
const createErr = ref('')
const form = reactive({ transactionId: '', amount: '', reason: '' })

function refundStyle(s) { return { pending: 'background-color:color-mix(in srgb,#f59e0b 20%,transparent);color:#fbbf24', approved: 'background-color:color-mix(in srgb,#22c55e 20%,transparent);color:#4ade80', rejected: 'background-color:color-mix(in srgb,#ef4444 20%,transparent);color:#f87171', completed: 'background-color:color-mix(in srgb,#3b82f6 20%,transparent);color:#60a5fa' }[s] ?? '' }
function refundLabel(s) { return { pending: 'Chờ duyệt', approved: 'Đã duyệt', rejected: 'Từ chối', completed: 'Hoàn tất' }[s] ?? s }
function formatDate(ts) { return ts ? new Date(ts).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' }) : '—' }
function formatVND(n) { return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(n || 0) }

async function load(p = 1) {
  page.value = p; loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (statusFilter.value) params.status = statusFilter.value
    const { data } = await supportApi.getRefundRequests(params)
    const payload = data.data ?? data
    refunds.value = payload.results ?? payload
    total.value = payload.count ?? refunds.value.length
    totalPages.value = Math.ceil(total.value / 20) || 1
  } catch { refunds.value = [] }
  finally { loading.value = false }
}

function closeCreate() { showCreate.value = false; createErr.value = ''; Object.assign(form, { transactionId: '', amount: '', reason: '' }) }

async function submitCreate() {
  if (!form.transactionId || !form.amount || !form.reason) { createErr.value = 'Vui lòng điền đầy đủ.'; return }
  creating.value = true; createErr.value = ''
  try {
    await supportApi.createRefundRequest({ transaction: form.transactionId, reason: form.reason, amount_vnd: form.amount })
    closeCreate()
    load(1)
  } catch (e) {
    const err = e?.response?.data
    createErr.value = (typeof err === 'object' ? Object.values(err).flat().join(' ') : err) ?? 'Tạo thất bại.'
  } finally { creating.value = false }
}

onMounted(() => load())
</script>
