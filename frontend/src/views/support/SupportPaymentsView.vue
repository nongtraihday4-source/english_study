<template>
  <div class="space-y-5">
    <div>
      <h2 class="text-xl font-bold" style="color:var(--color-text-base)">Thanh toán</h2>
      <p class="text-sm mt-0.5" style="color:var(--color-text-muted)">Tra cứu giao dịch và gói đăng ký (chỉ xem)</p>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 p-1 rounded-xl w-fit" style="background-color:var(--color-surface-02)">
      <button v-for="t in tabs" :key="t.key" class="text-sm px-4 py-2 rounded-lg transition font-medium"
        :style="tab === t.key ? 'background-color:#3b82f6;color:#fff' : 'color:var(--color-text-muted)'"
        @click="switchTab(t.key)">{{ t.label }}</button>
    </div>

    <!-- Transactions tab -->
    <div v-if="tab === 'transactions'" class="space-y-4">
      <div class="flex gap-2">
        <input v-model="txSearch" type="text" placeholder="Email, Mã GD..." class="flex-1 rounded-xl px-3 py-2 text-sm border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" @keyup.enter="loadTx(1)" />
        <select v-model="txStatus" class="rounded-xl px-3 py-2 text-sm border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" @change="loadTx(1)">
          <option value="">Mọi trạng thái</option>
          <option value="pending">Pending</option>
          <option value="success">Success</option>
          <option value="failed">Failed</option>
          <option value="refunded">Refunded</option>
        </select>
        <button class="text-sm px-4 py-2 rounded-xl hover:opacity-80" style="background-color:#3b82f6;color:#fff" @click="loadTx(1)">Tìm</button>
      </div>
      <div class="rounded-2xl overflow-hidden" style="background-color:var(--color-surface-02)">
        <div v-if="txLoading" class="p-5 space-y-2"><div v-for="n in 5" :key="n" class="h-10 animate-pulse rounded-xl" style="background-color:var(--color-surface-03)" /></div>
        <table v-else-if="transactions.length" class="w-full text-sm">
          <thead><tr style="border-bottom:1px solid var(--color-surface-04)"><th v-for="h in ['Mã GD','Người dùng','Gói','Số tiền','P.thức','Trạng thái','Ngày']" :key="h" class="text-left px-4 py-3 text-xs font-semibold" style="color:var(--color-text-muted)">{{ h }}</th></tr></thead>
          <tbody>
            <tr v-for="tx in transactions" :key="tx.id" style="border-bottom:1px solid var(--color-surface-04)">
              <td class="px-4 py-3 font-mono text-xs" style="color:var(--color-text-base)">{{ tx.transaction_id }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ tx.user_email }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ tx.plan_name }}</td>
              <td class="px-4 py-3 font-semibold text-xs" style="color:var(--color-text-base)">{{ formatVND(tx.amount_vnd) }}</td>
              <td class="px-4 py-3 text-xs uppercase" style="color:var(--color-text-muted)">{{ tx.payment_method }}</td>
              <td class="px-4 py-3"><span class="text-xs px-2 py-0.5 rounded-full" :style="txStyle(tx.status)">{{ tx.status }}</span></td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ formatDate(tx.created_at) }}</td>
            </tr>
          </tbody>
        </table>
        <div v-else class="p-8 text-center text-sm" style="color:var(--color-text-muted)">Không có giao dịch.</div>
        <div v-if="txTotalPages > 1" class="flex items-center justify-between px-4 py-3 border-t" style="border-color:var(--color-surface-04)">
          <span class="text-xs" style="color:var(--color-text-muted)">{{ txTotal }} giao dịch</span>
          <div class="flex gap-2">
            <button :disabled="txPage === 1" class="text-xs px-3 py-1.5 rounded-lg disabled:opacity-40" style="background-color:var(--color-surface-03);color:var(--color-text-base)" @click="loadTx(txPage-1)">‹</button>
            <span class="text-xs py-1.5 px-2" style="color:var(--color-text-muted)">{{ txPage }} / {{ txTotalPages }}</span>
            <button :disabled="txPage === txTotalPages" class="text-xs px-3 py-1.5 rounded-lg disabled:opacity-40" style="background-color:var(--color-surface-03);color:var(--color-text-base)" @click="loadTx(txPage+1)">›</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Subscriptions tab -->
    <div v-else class="space-y-4">
      <div class="flex gap-2">
        <input v-model="subSearch" type="text" placeholder="Email người dùng..." class="flex-1 rounded-xl px-3 py-2 text-sm border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" @keyup.enter="loadSub(1)" />
        <select v-model="subStatus" class="rounded-xl px-3 py-2 text-sm border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" @change="loadSub(1)">
          <option value="">Mọi trạng thái</option>
          <option value="active">Active</option>
          <option value="expired">Expired</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <button class="text-sm px-4 py-2 rounded-xl hover:opacity-80" style="background-color:#3b82f6;color:#fff" @click="loadSub(1)">Tìm</button>
      </div>
      <div class="rounded-2xl overflow-hidden" style="background-color:var(--color-surface-02)">
        <div v-if="subLoading" class="p-5 space-y-2"><div v-for="n in 5" :key="n" class="h-10 animate-pulse rounded-xl" style="background-color:var(--color-surface-03)" /></div>
        <table v-else-if="subscriptions.length" class="w-full text-sm">
          <thead><tr style="border-bottom:1px solid var(--color-surface-04)"><th v-for="h in ['Người dùng','Gói','Trạng thái','Bắt đầu','Hết hạn','Tự gia hạn']" :key="h" class="text-left px-4 py-3 text-xs font-semibold" style="color:var(--color-text-muted)">{{ h }}</th></tr></thead>
          <tbody>
            <tr v-for="s in subscriptions" :key="s.id" style="border-bottom:1px solid var(--color-surface-04)">
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-base)">{{ s.user_email }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ s.plan_name }}</td>
              <td class="px-4 py-3"><span class="text-xs px-2 py-0.5 rounded-full" :style="subStyle(s.status)">{{ s.status }}</span></td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ formatDate(s.start_date) }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ formatDate(s.end_date) }}</td>
              <td class="px-4 py-3 text-xs" :style="s.auto_renew ? 'color:#4ade80' : 'color:var(--color-text-muted)'">{{ s.auto_renew ? 'Có' : 'Không' }}</td>
            </tr>
          </tbody>
        </table>
        <div v-else class="p-8 text-center text-sm" style="color:var(--color-text-muted)">Không có gói đăng ký.</div>
        <div v-if="subTotalPages > 1" class="flex items-center justify-between px-4 py-3 border-t" style="border-color:var(--color-surface-04)">
          <span class="text-xs" style="color:var(--color-text-muted)">{{ subTotal }} gói</span>
          <div class="flex gap-2">
            <button :disabled="subPage === 1" class="text-xs px-3 py-1.5 rounded-lg disabled:opacity-40" style="background-color:var(--color-surface-03);color:var(--color-text-base)" @click="loadSub(subPage-1)">‹</button>
            <span class="text-xs py-1.5 px-2" style="color:var(--color-text-muted)">{{ subPage }} / {{ subTotalPages }}</span>
            <button :disabled="subPage === subTotalPages" class="text-xs px-3 py-1.5 rounded-lg disabled:opacity-40" style="background-color:var(--color-surface-03);color:var(--color-text-base)" @click="loadSub(subPage+1)">›</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { supportApi } from '@/api/support.js'

const tabs = [{ key: 'transactions', label: 'Giao dịch' }, { key: 'subscriptions', label: 'Gói đăng ký' }]
const tab = ref('transactions')

const transactions = ref([]); const txLoading = ref(false); const txSearch = ref(''); const txStatus = ref(''); const txPage = ref(1); const txTotal = ref(0); const txTotalPages = ref(1)
const subscriptions = ref([]); const subLoading = ref(false); const subSearch = ref(''); const subStatus = ref(''); const subPage = ref(1); const subTotal = ref(0); const subTotalPages = ref(1)

function txStyle(s) { return { success: 'background-color:color-mix(in srgb,#22c55e 20%,transparent);color:#4ade80', pending: 'background-color:color-mix(in srgb,#f59e0b 20%,transparent);color:#fbbf24', failed: 'background-color:color-mix(in srgb,#ef4444 20%,transparent);color:#f87171', refunded: 'background-color:color-mix(in srgb,#6b7280 20%,transparent);color:#9ca3af' }[s] ?? '' }
function subStyle(s) { return { active: 'background-color:color-mix(in srgb,#22c55e 20%,transparent);color:#4ade80', expired: 'background-color:color-mix(in srgb,#ef4444 20%,transparent);color:#f87171', cancelled: 'background-color:color-mix(in srgb,#6b7280 20%,transparent);color:#9ca3af' }[s] ?? '' }
function formatDate(ts) { return ts ? new Date(ts).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' }) : '—' }
function formatVND(n) { return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(n || 0) }

async function loadTx(p = 1) {
  txPage.value = p; txLoading.value = true
  try {
    const params = { page: txPage.value, page_size: 20 }
    if (txSearch.value) params.search = txSearch.value
    if (txStatus.value) params.status = txStatus.value
    const { data } = await supportApi.getTransactions(params)
    const payload = data.data ?? data
    transactions.value = payload.results ?? payload
    txTotal.value = payload.count ?? transactions.value.length
    txTotalPages.value = Math.ceil(txTotal.value / 20) || 1
  } catch { transactions.value = [] }
  finally { txLoading.value = false }
}

async function loadSub(p = 1) {
  subPage.value = p; subLoading.value = true
  try {
    const params = { page: subPage.value, page_size: 20 }
    if (subSearch.value) params.search = subSearch.value
    if (subStatus.value) params.status = subStatus.value
    const { data } = await supportApi.getSubscriptions(params)
    const payload = data.data ?? data
    subscriptions.value = payload.results ?? payload
    subTotal.value = payload.count ?? subscriptions.value.length
    subTotalPages.value = Math.ceil(subTotal.value / 20) || 1
  } catch { subscriptions.value = [] }
  finally { subLoading.value = false }
}

function switchTab(k) { tab.value = k; if (k === 'subscriptions' && !subscriptions.value.length) loadSub() }

onMounted(() => loadTx())
</script>
