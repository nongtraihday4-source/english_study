<template>
  <div class="flex h-screen overflow-hidden" style="background-color: var(--color-surface)">
    <!-- Support Sidebar -->
    <aside
      :class="collapsed ? 'w-16' : 'w-60'"
      class="shrink-0 flex flex-col h-full transition-all duration-200 border-r"
      style="background-color: var(--color-surface-01); border-color: var(--color-surface-04)"
    >
      <!-- Logo / Brand -->
      <div class="flex items-center gap-3 px-4 h-16 shrink-0 border-b" style="border-color: var(--color-surface-04)">
        <span class="text-2xl">🎧</span>
        <span v-if="!collapsed" class="font-bold text-sm truncate" style="color: var(--color-text-base)">Support Portal</span>
        <button
          class="ml-auto text-xs p-1 rounded hover:opacity-70"
          style="color: var(--color-text-muted)"
          @click="collapsed = !collapsed"
        >
          {{ collapsed ? '→' : '←' }}
        </button>
      </div>

      <!-- Nav links -->
      <nav class="flex-1 py-3 overflow-y-auto space-y-0.5 px-2">
        <RouterLink
          v-for="item in NAV"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition hover:opacity-80"
          :class="isActive(item.to) ? 'nav-active' : 'nav-idle'"
        >
          <span class="text-lg shrink-0">{{ item.icon }}</span>
          <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
          <span
            v-if="!collapsed && item.badge"
            class="ml-auto text-xs px-1.5 py-0.5 rounded-full font-semibold"
            style="background-color: color-mix(in srgb, #3b82f6 20%, transparent); color: #60a5fa"
          >{{ item.badge }}</span>
        </RouterLink>
      </nav>

      <!-- Footer -->
      <div class="px-2 py-3 border-t space-y-0.5" style="border-color: var(--color-surface-04)">
        <!-- Admin can also view admin panel -->
        <RouterLink
          v-if="auth.isAdmin"
          to="/admin"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition nav-idle hover:opacity-80"
        >
          <span class="text-lg shrink-0">🛡️</span>
          <span v-if="!collapsed" class="truncate">Admin Panel</span>
        </RouterLink>
        <RouterLink
          to="/dashboard"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition nav-idle hover:opacity-80"
        >
          <span class="text-lg shrink-0">🏠</span>
          <span v-if="!collapsed" class="truncate">Trang chủ</span>
        </RouterLink>
      </div>
    </aside>

    <!-- Main area -->
    <div class="flex flex-col flex-1 min-w-0 overflow-hidden">
      <!-- Top bar -->
      <header
        class="flex items-center gap-3 px-6 h-16 shrink-0 border-b"
        style="background-color: var(--color-surface-01); border-color: var(--color-surface-04)"
      >
        <div class="flex-1">
          <h1 class="text-base font-bold" style="color: var(--color-text-base)">{{ currentTitle }}</h1>
        </div>
        <div class="flex items-center gap-2">
          <span
            class="text-xs px-2 py-1 rounded-full font-semibold"
            style="background-color: color-mix(in srgb, #3b82f6 20%, transparent); color: #60a5fa"
          >Hỗ trợ</span>
          <span class="text-sm" style="color: var(--color-text-muted)">{{ auth.displayName }}</span>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 overflow-y-auto p-5 lg:p-8">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const auth = useAuthStore()
const route = useRoute()
const collapsed = ref(false)

const NAV = [
  { to: '/support',          icon: '📊', label: 'Tổng quan' },
  { to: '/support/users',    icon: '🔍', label: 'Tra cứu người dùng' },
  { to: '/support/public-requests', icon: '📨', label: 'Yêu cầu công khai' },
  { to: '/support/tickets',  icon: '🎫', label: 'Tickets' },
  { to: '/support/payments', icon: '💳', label: 'Thanh toán' },
  { to: '/support/coupons',  icon: '🏷️',  label: 'Ưu đãi' },
  { to: '/support/refunds',  icon: '↩️',  label: 'Hoàn tiền' },
]

function isActive(path) {
  if (path === '/support') return route.path === '/support'
  return route.path.startsWith(path)
}

const currentTitle = computed(() => {
  const found = NAV.find((n) => isActive(n.to))
  return found?.label || 'Support Portal'
})
</script>

<style scoped>
.nav-active {
  background-color: color-mix(in srgb, #3b82f6 18%, transparent);
  color: #60a5fa;
}
.nav-idle { color: var(--color-text-muted); }
</style>
