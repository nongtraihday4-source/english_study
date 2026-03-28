<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h2 class="text-xl font-bold" style="color: var(--color-text-base)">Tổng quan hệ thống</h2>
      <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">Số liệu thống kê toàn hệ thống</p>
    </div>

    <!-- KPI Cards -->
    <div v-if="loading" class="grid grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="n in 6"
        :key="n"
        class="rounded-2xl p-5 animate-pulse h-24"
        style="background-color: var(--color-surface-02)"
      />
    </div>

    <div v-else class="grid grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="card in kpiCards"
        :key="card.label"
        class="rounded-2xl p-5 flex flex-col gap-2"
        style="background-color: var(--color-surface-02)"
      >
        <div class="flex items-center justify-between">
          <span class="text-2xl">{{ card.icon }}</span>
          <span
            v-if="card.badge"
            class="text-xs px-2 py-0.5 rounded-full font-medium"
            :style="card.badgeStyle"
          >{{ card.badge }}</span>
        </div>
        <div class="text-2xl font-bold" style="color: var(--color-text-base)">{{ card.value }}</div>
        <div class="text-xs" style="color: var(--color-text-muted)">{{ card.label }}</div>
      </div>
    </div>

    <!-- User Growth Chart + Activity Feed -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 7-day user growth bar chart -->
      <div class="rounded-2xl p-5" style="background-color: var(--color-surface-02)">
        <h3 class="text-sm font-semibold mb-4" style="color: var(--color-text-base)">
          📈 Người dùng mới (7 ngày)
        </h3>
        <div v-if="loading" class="h-32 animate-pulse rounded-xl" style="background-color: var(--color-surface-03)" />
        <div v-else class="flex items-end gap-2 h-32">
          <div
            v-for="day in stats.user_growth"
            :key="day.date"
            class="flex-1 flex flex-col items-center gap-1"
          >
            <span class="text-xs font-medium" style="color: var(--color-text-base)">{{ day.count }}</span>
            <div
              class="w-full rounded-t-md transition-all"
              :style="{
                height: `${maxGrowth > 0 ? Math.max(4, (day.count / maxGrowth) * 96) : 4}px`,
                backgroundColor: 'var(--color-primary-500)',
                opacity: 0.8
              }"
            />
            <span class="text-xs" style="color: var(--color-text-muted)">{{ day.date }}</span>
          </div>
        </div>
      </div>

      <!-- Recent activity feed -->
      <div class="rounded-2xl p-5" style="background-color: var(--color-surface-02)">
        <h3 class="text-sm font-semibold mb-4" style="color: var(--color-text-base)">
          🕐 Hoạt động gần đây
        </h3>
        <div v-if="loading" class="space-y-3">
          <div
            v-for="n in 5"
            :key="n"
            class="h-10 animate-pulse rounded-xl"
            style="background-color: var(--color-surface-03)"
          />
        </div>
        <div v-else class="space-y-2 max-h-48 overflow-y-auto pr-1">
          <div
            v-for="(event, i) in stats.recent_activity"
            :key="i"
            class="flex items-start gap-3 py-1.5"
          >
            <span class="text-base shrink-0 mt-0.5">{{ event.icon }}</span>
            <div class="flex-1 min-w-0">
              <p class="text-xs leading-snug truncate" style="color: var(--color-text-base)">
                {{ event.description }}
              </p>
              <p class="text-xs mt-0.5" style="color: var(--color-text-muted)">
                {{ formatTime(event.timestamp) }}
              </p>
            </div>
          </div>
          <p v-if="!stats.recent_activity?.length" class="text-xs text-center py-4" style="color: var(--color-text-muted)">
            Chưa có hoạt động nào.
          </p>
        </div>
      </div>
    </div>

    <!-- Error state -->
    <div
      v-if="error"
      class="rounded-2xl p-4 text-sm"
      style="background-color: color-mix(in srgb, #ef4444 12%, transparent); color: #f87171"
    >
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { adminApi } from '@/api/admin.js'

const loading = ref(true)
const error = ref(null)
const stats = reactive({ user_growth: [], recent_activity: [], stats: {} })

const kpiCards = computed(() => {
  const s = stats.stats || {}
  return [
    {
      icon: '👥',
      value: s.total_users?.toLocaleString('vi-VN') ?? '—',
      label: 'Tổng người dùng',
    },
    {
      icon: '🆕',
      value: s.new_today ?? '—',
      label: 'Đăng ký hôm nay',
      badge: 'Hôm nay',
      badgeStyle: 'background-color:color-mix(in srgb,#22c55e 20%,transparent);color:#4ade80',
    },
    {
      icon: '🟢',
      value: s.active_today ?? '—',
      label: 'Đang hoạt động hôm nay',
    },
    {
      icon: '💰',
      value: s.revenue_month != null ? `${Number(s.revenue_month).toLocaleString('vi-VN')}đ` : '—',
      label: 'Doanh thu tháng này',
      badge: 'Tháng',
      badgeStyle: 'background-color:color-mix(in srgb,#eab308 20%,transparent);color:#facc15',
    },
    {
      icon: '📝',
      value: s.pending_submissions ?? '—',
      label: 'Bài nộp chờ chấm',
      badge: s.pending_submissions > 0 ? 'Cần xử lý' : null,
      badgeStyle: 'background-color:color-mix(in srgb,#ef4444 20%,transparent);color:#f87171',
    },
    {
      icon: '📚',
      value: s.total_courses ?? '—',
      label: 'Khoá học đang hoạt động',
    },
  ]
})

const maxGrowth = computed(() =>
  Math.max(1, ...((stats.user_growth || []).map((d) => d.count)))
)

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return d.toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' })
}

async function fetchDashboard() {
  loading.value = true
  error.value = null
  try {
    const { data } = await adminApi.getDashboard()
    const payload = data.data ?? data
    stats.stats = payload.stats
    stats.user_growth = payload.user_growth
    stats.recent_activity = payload.recent_activity
  } catch (e) {
    error.value = 'Không thể tải dữ liệu. Vui lòng thử lại.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchDashboard)
</script>
