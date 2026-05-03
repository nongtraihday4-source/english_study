<template>
  <div class="space-y-5">
    <div>
      <h2 class="text-xl font-bold" style="color:var(--color-text-base)">Ưu đãi / Coupon</h2>
      <p class="text-sm mt-0.5" style="color:var(--color-text-muted)">Tra cứu mã giảm giá (chỉ xem)</p>
    </div>
    <div class="flex gap-2">
      <input v-model="search" type="text" placeholder="Tìm theo mã coupon..." class="flex-1 rounded-xl px-3 py-2 text-sm border" style="background-color:var(--color-surface-02);border-color:var(--color-surface-04);color:var(--color-text-base)" @keyup.enter="load(1)" />
      <label class="flex items-center gap-2 text-xs cursor-pointer px-3 py-2 rounded-xl border" style="border-color:var(--color-surface-04);color:var(--color-text-muted)">
        <input v-model="activeOnly" type="checkbox" @change="load(1)" />
        Chỉ còn hiệu lực
      </label>
      <button class="text-sm px-4 py-2 rounded-xl hover:opacity-80" style="background-color:#3b82f6;color:#fff" @click="load(1)">Tìm</button>
    </div>
    <div class="rounded-2xl overflow-hidden" style="background-color:var(--color-surface-02)">
      <div v-if="loading" class="p-5 space-y-2"><div v-for="n in 6" :key="n" class="h-10 animate-pulse rounded-xl" style="background-color:var(--color-surface-03)" /></div>
      <table v-else-if="coupons.length" class="w-full text-sm">
        <thead><tr style="border-bottom:1px solid var(--color-surface-04)"><th v-for="h in ['Mã','Loại','Giá trị','Đã dùng','Giới hạn','Hiệu lực từ','Hết hạn','Trạng thái']" :key="h" class="text-left px-4 py-3 text-xs font-semibold" style="color:var(--color-text-muted)">{{ h }}</th></tr></thead>
        <tbody>
          <tr v-for="c in coupons" :key="c.id" style="border-bottom:1px solid var(--color-surface-04)">
            <td class="px-4 py-3 font-mono font-semibold text-xs" style="color:var(--color-text-base)">{{ c.code }}</td>
            <td class="px-4 py-3 text-xs capitalize" style="color:var(--color-text-muted)">{{ c.discount_type }}</td>
            <td class="px-4 py-3 text-xs font-semibold" style="color:var(--color-text-base)">{{ c.discount_type === 'percentage' ? c.discount_value + '%' : formatVND(c.discount_value) }}</td>
            <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ c.times_used ?? 0 }}</td>
            <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ c.usage_limit ?? '∞' }}</td>
            <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ c.valid_from ? formatDate(c.valid_from) : '—' }}</td>
            <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ c.valid_until ? formatDate(c.valid_until) : '—' }}</td>
            <td class="px-4 py-3"><span class="text-xs px-2 py-0.5 rounded-full" :style="c.is_available ? 'background-color:color-mix(in srgb,#22c55e 20%,transparent);color:#4ade80' : 'background-color:color-mix(in srgb,#ef4444 20%,transparent);color:#f87171'">{{ c.is_available ? 'Hiệu lực' : 'Hết hạn' }}</span></td>
          </tr>
        </tbody>
      </table>
      <div v-else class="p-8 text-center text-sm" style="color:var(--color-text-muted)">Không có coupon nào.</div>
      <div v-if="totalPages > 1" class="flex items-center justify-between px-4 py-3 border-t" style="border-color:var(--color-surface-04)">
        <span class="text-xs" style="color:var(--color-text-muted)">{{ total }} coupon</span>
        <div class="flex gap-2">
          <button :disabled="page === 1" class="text-xs px-3 py-1.5 rounded-lg disabled:opacity-40" style="background-color:var(--color-surface-03);color:var(--color-text-base)" @click="load(page-1)">‹</button>
          <span class="text-xs py-1.5 px-2" style="color:var(--color-text-muted)">{{ page }} / {{ totalPages }}</span>
          <button :disabled="page === totalPages" class="text-xs px-3 py-1.5 rounded-lg disabled:opacity-40" style="background-color:var(--color-surface-03);color:var(--color-text-base)" @click="load(page+1)">›</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { supportApi } from '@/api/support.js'

const coupons = ref([])
const loading = ref(false)
const search = ref('')
const activeOnly = ref(true)
const page = ref(1)
const total = ref(0)
const totalPages = ref(1)

function formatDate(ts) { return ts ? new Date(ts).toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' }) : '—' }
function formatVND(n) { return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(n || 0) }

async function load(p = 1) {
  page.value = p; loading.value = true
  try {
    const params = { page: page.value, page_size: 20 }
    if (search.value) params.search = search.value
    if (activeOnly.value) params.active_only = 'true'
    const { data } = await supportApi.getCoupons(params)
    const payload = data.data ?? data
    coupons.value = payload.results ?? payload
    total.value = payload.count ?? coupons.value.length
    totalPages.value = Math.ceil(total.value / 20) || 1
  } catch { coupons.value = [] }
  finally { loading.value = false }
}

onMounted(() => load())
</script>
