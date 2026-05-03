<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-xl font-bold" style="color: var(--color-text-base)">Tra cứu người dùng</h2>
      <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">Tìm theo email, số điện thoại hoặc tên</p>
    </div>

    <!-- Search bar -->
    <div class="flex gap-3">
      <input
        v-model="search"
        type="text"
        placeholder="Email, SĐT hoặc tên..."
        class="flex-1 rounded-xl px-4 py-2.5 text-sm bg-transparent border focus:outline-none"
        style="border-color: var(--color-surface-04); color: var(--color-text-base); background-color: var(--color-surface-02)"
        @keyup.enter="doSearch"
      />
      <select
        v-model="filters.account_type"
        class="rounded-xl px-3 py-2.5 text-sm border focus:outline-none"
        style="border-color: var(--color-surface-04); color: var(--color-text-base); background-color: var(--color-surface-02)"
        @change="doSearch"
      >
        <option value="">Tất cả gói</option>
        <option value="demo">Demo</option>
        <option value="premium">Premium</option>
      </select>
      <button
        class="px-5 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
        style="background-color: #3b82f6; color: #fff"
        @click="doSearch"
      >Tìm kiếm</button>
    </div>

    <!-- Results -->
    <div class="rounded-2xl overflow-hidden" style="background-color: var(--color-surface-02)">
      <div v-if="loading" class="p-6 space-y-2">
        <div v-for="n in 5" :key="n" class="h-12 animate-pulse rounded-xl" style="background-color: var(--color-surface-03)" />
      </div>
      <div v-else-if="!users.length && searched" class="p-8 text-center text-sm" style="color: var(--color-text-muted)">Không tìm thấy người dùng nào.</div>
      <div v-else-if="!searched" class="p-8 text-center text-sm" style="color: var(--color-text-muted)">Nhập từ khoá và nhấn Tìm kiếm để bắt đầu.</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr style="border-bottom: 1px solid var(--color-surface-04)">
            <th v-for="h in ['Email', 'Tên', 'SĐT', 'Gói', 'Subscription', 'Đăng nhập cuối', '']" :key="h"
                class="text-left px-4 py-3 text-xs font-semibold" style="color: var(--color-text-muted)">{{ h }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="u in users"
            :key="u.id"
            style="border-bottom: 1px solid var(--color-surface-04)"
            class="hover:opacity-80 transition"
          >
            <td class="px-4 py-3" style="color: var(--color-text-base)">{{ u.email }}</td>
            <td class="px-4 py-3" style="color: var(--color-text-muted)">{{ u.full_name }}</td>
            <td class="px-4 py-3" style="color: var(--color-text-muted)">{{ u.phone || '—' }}</td>
            <td class="px-4 py-3">
              <span class="text-xs px-2 py-0.5 rounded-full" :style="accountStyle(u.account_type)">{{ u.account_type }}</span>
            </td>
            <td class="px-4 py-3">
              <span v-if="u.subscription_status" class="text-xs px-2 py-0.5 rounded-full" :style="subStyle(u.subscription_status)">{{ u.subscription_status }}</span>
              <span v-else class="text-xs" style="color: var(--color-text-muted)">—</span>
            </td>
            <td class="px-4 py-3 text-xs" style="color: var(--color-text-muted)">{{ u.last_login ? formatDate(u.last_login) : '—' }}</td>
            <td class="px-4 py-3">
              <RouterLink :to="`/support/users/${u.id}`" class="text-xs font-medium hover:opacity-80" style="color: #60a5fa">Chi tiết →</RouterLink>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-between px-4 py-3 border-t" style="border-color: var(--color-surface-04)">
        <span class="text-xs" style="color: var(--color-text-muted)">{{ total }} kết quả</span>
        <div class="flex gap-2">
          <button :disabled="page === 1" class="text-xs px-3 py-1.5 rounded-lg disabled:opacity-40" style="background-color:var(--color-surface-03);color:var(--color-text-base)" @click="changePage(page - 1)">‹</button>
          <span class="text-xs py-1.5 px-2" style="color: var(--color-text-muted)">{{ page }} / {{ totalPages }}</span>
          <button :disabled="page === totalPages" class="text-xs px-3 py-1.5 rounded-lg disabled:opacity-40" style="background-color:var(--color-surface-03);color:var(--color-text-base)" @click="changePage(page + 1)">›</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { supportApi } from '@/api/support.js'

const search = ref('')
const filters = ref({ account_type: '' })
const users = ref([])
const loading = ref(false)
const searched = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = 20
const totalPages = ref(1)

function accountStyle(t) { return t === 'premium' ? 'background-color:color-mix(in srgb,#f59e0b 20%,transparent);color:#fbbf24' : 'background-color:color-mix(in srgb,#6b7280 20%,transparent);color:#9ca3af' }
function subStyle(s) { return s === 'active' ? 'background-color:color-mix(in srgb,#22c55e 20%,transparent);color:#4ade80' : 'background-color:color-mix(in srgb,#ef4444 20%,transparent);color:#f87171' }
function formatDate(ts) { return new Date(ts).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' }) }

async function doSearch(resetPage = true) {
  if (resetPage === true) page.value = 1
  loading.value = true
  searched.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (search.value.trim()) params.search = search.value.trim()
    if (filters.value.account_type) params.account_type = filters.value.account_type
    const { data } = await supportApi.searchUsers(params)
    const payload = data.data ?? data
    users.value = payload.results ?? payload
    total.value = payload.count ?? users.value.length
    totalPages.value = Math.ceil(total.value / pageSize) || 1
  } catch {
    users.value = []
  } finally {
    loading.value = false
  }
}

function changePage(p) {
  page.value = p
  doSearch(false)
}
</script>
