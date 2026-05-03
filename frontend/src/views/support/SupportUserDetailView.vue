<template>
  <div class="space-y-6">
    <!-- Back -->
    <div class="flex items-center gap-3">
      <RouterLink to="/support/users" class="text-sm hover:opacity-70" style="color: #60a5fa">← Tra cứu</RouterLink>
      <span style="color: var(--color-text-muted)">/</span>
      <span class="text-sm font-semibold" style="color: var(--color-text-base)">Chi tiết người dùng</span>
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="n in 4" :key="n" class="h-24 animate-pulse rounded-2xl" style="background-color:var(--color-surface-02)" />
    </div>
    <template v-else-if="user">
      <!-- User info card -->
      <div class="rounded-2xl p-5" style="background-color: var(--color-surface-02)">
        <div class="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h3 class="font-bold text-lg" style="color: var(--color-text-base)">{{ user.full_name }}</h3>
            <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">{{ user.email }}</p>
            <p v-if="user.phone" class="text-sm" style="color: var(--color-text-muted)">{{ user.phone }}</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <span class="text-xs px-2.5 py-1 rounded-full" :style="accountStyle(user.account_type)">{{ user.account_type }}</span>
            <span class="text-xs px-2.5 py-1 rounded-full" :style="roleStyle(user.role)">{{ user.role }}</span>
          </div>
        </div>
        <div class="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
          <div>
            <p class="text-xs mb-0.5" style="color: var(--color-text-muted)">Tham gia</p>
            <p style="color: var(--color-text-base)">{{ formatDate(user.date_joined) }}</p>
          </div>
          <div>
            <p class="text-xs mb-0.5" style="color: var(--color-text-muted)">Đăng nhập cuối</p>
            <p style="color: var(--color-text-base)">{{ user.last_login ? formatDate(user.last_login) : '—' }}</p>
          </div>
          <div>
            <p class="text-xs mb-0.5" style="color: var(--color-text-muted)">Tickets</p>
            <p style="color: var(--color-text-base)">{{ user.ticket_count ?? 0 }}</p>
          </div>
          <div>
            <p class="text-xs mb-0.5" style="color: var(--color-text-muted)">Kích hoạt</p>
            <p :style="user.is_active ? 'color:#4ade80' : 'color:#f87171'">{{ user.is_active ? 'Hoạt động' : 'Bị khoá' }}</p>
          </div>
        </div>
        <div class="mt-4 pt-4 border-t" style="border-color: var(--color-surface-04)">
          <button
            :disabled="resetSending"
            class="text-sm font-medium px-4 py-2 rounded-xl transition hover:opacity-80 disabled:opacity-50"
            style="background-color: color-mix(in srgb, #f59e0b 20%, transparent); color: #fbbf24"
            @click="sendPasswordReset"
          >
            {{ resetSending ? 'Đang gửi...' : '✉ Gửi email đặt lại mật khẩu' }}
          </button>
          <p v-if="resetMsg" class="text-xs mt-2" :style="resetOk ? 'color:#4ade80' : 'color:#f87171'">{{ resetMsg }}</p>
        </div>
      </div>

      <!-- Subscription -->
      <div v-if="user.active_subscription" class="rounded-2xl p-5" style="background-color: var(--color-surface-02)">
        <h4 class="font-semibold text-sm mb-3" style="color: var(--color-text-base)">Gói hiện tại</h4>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
          <div><p class="text-xs mb-0.5" style="color:var(--color-text-muted)">Gói</p><p style="color:var(--color-text-base)">{{ user.active_subscription.plan_name }}</p></div>
          <div><p class="text-xs mb-0.5" style="color:var(--color-text-muted)">Trạng thái</p><p style="color:#4ade80">{{ user.active_subscription.status }}</p></div>
          <div><p class="text-xs mb-0.5" style="color:var(--color-text-muted)">Bắt đầu</p><p style="color:var(--color-text-base)">{{ formatDate(user.active_subscription.start_date) }}</p></div>
          <div><p class="text-xs mb-0.5" style="color:var(--color-text-muted)">Hết hạn</p><p style="color:var(--color-text-base)">{{ formatDate(user.active_subscription.end_date) }}</p></div>
        </div>
      </div>
      <div v-else class="rounded-2xl p-4 text-sm" style="background-color:var(--color-surface-02);color:var(--color-text-muted)">Chưa có gói đăng ký đang hoạt động.</div>

      <!-- Recent transactions -->
      <div class="rounded-2xl overflow-hidden" style="background-color: var(--color-surface-02)">
        <h4 class="font-semibold text-sm px-5 pt-5 pb-3" style="color: var(--color-text-base)">Lịch sử giao dịch gần đây</h4>
        <div v-if="!user.recent_transactions?.length" class="px-5 pb-5 text-sm" style="color:var(--color-text-muted)">Không có giao dịch.</div>
        <table v-else class="w-full text-sm">
          <thead>
            <tr style="border-top: 1px solid var(--color-surface-04)">
              <th v-for="h in ['Mã GD', 'Gói', 'Số tiền', 'Phương thức', 'Trạng thái', 'Ngày']" :key="h" class="text-left px-4 py-2.5 text-xs font-semibold" style="color:var(--color-text-muted)">{{ h }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tx in user.recent_transactions" :key="tx.id" class="border-t" style="border-color:var(--color-surface-04)">
              <td class="px-4 py-2.5 font-mono text-xs" style="color:var(--color-text-base)">{{ tx.transaction_id }}</td>
              <td class="px-4 py-2.5" style="color:var(--color-text-muted)">{{ tx.plan_name }}</td>
              <td class="px-4 py-2.5 font-semibold" style="color:var(--color-text-base)">{{ formatVND(tx.amount_vnd) }}</td>
              <td class="px-4 py-2.5 text-xs uppercase" style="color:var(--color-text-muted)">{{ tx.payment_method }}</td>
              <td class="px-4 py-2.5"><span class="text-xs px-2 py-0.5 rounded-full" :style="txStyle(tx.status)">{{ tx.status }}</span></td>
              <td class="px-4 py-2.5 text-xs" style="color:var(--color-text-muted)">{{ formatDate(tx.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
    <div v-else class="text-sm p-6" style="color:var(--color-text-muted)">Không tìm thấy người dùng.</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { supportApi } from '@/api/support.js'

const route = useRoute()
const user = ref(null)
const loading = ref(true)
const resetSending = ref(false)
const resetMsg = ref('')
const resetOk = ref(false)

function accountStyle(t) { return t === 'premium' ? 'background-color:color-mix(in srgb,#f59e0b 20%,transparent);color:#fbbf24' : 'background-color:color-mix(in srgb,#6b7280 20%,transparent);color:#9ca3af' }
function roleStyle(r) { return r === 'admin' ? 'background-color:color-mix(in srgb,#ef4444 20%,transparent);color:#f87171' : 'background-color:color-mix(in srgb,#6b7280 20%,transparent);color:#9ca3af' }
function txStyle(s) { return s === 'success' ? 'background-color:color-mix(in srgb,#22c55e 20%,transparent);color:#4ade80' : s === 'pending' ? 'background-color:color-mix(in srgb,#f59e0b 20%,transparent);color:#fbbf24' : 'background-color:color-mix(in srgb,#ef4444 20%,transparent);color:#f87171' }
function formatDate(ts) { return ts ? new Date(ts).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' }) : '—' }
function formatVND(n) { return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(n || 0) }

async function loadUser() {
  try {
    const { data } = await supportApi.getUserDetail(route.params.id)
    user.value = data.data ?? data
  } catch { user.value = null }
  finally { loading.value = false }
}

async function sendPasswordReset() {
  resetSending.value = true
  resetMsg.value = ''
  try {
    const { data } = await supportApi.resetUserPassword(route.params.id)
    const d = data.data ?? data
    resetOk.value = true
    resetMsg.value = d.detail ?? 'Đã gửi email thành công.'
  } catch (e) {
    resetOk.value = false
    resetMsg.value = e?.response?.data?.detail ?? 'Gửi thất bại.'
  } finally { resetSending.value = false }
}

onMounted(loadUser)
</script>
