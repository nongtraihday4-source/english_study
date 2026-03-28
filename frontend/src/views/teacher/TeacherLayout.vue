<template>
  <div class="flex h-screen overflow-hidden" style="background-color: var(--color-surface)">
    <!-- Teacher Sidebar -->
    <aside
      :class="collapsed ? 'w-16' : 'w-60'"
      class="shrink-0 flex flex-col h-full transition-all duration-200 border-r"
      style="background-color: var(--color-surface-01); border-color: var(--color-surface-04)"
    >
      <!-- Logo / Brand -->
      <div class="flex items-center gap-3 px-4 h-16 shrink-0 border-b" style="border-color: var(--color-surface-04)">
        <span class="text-2xl">🎓</span>
        <span v-if="!collapsed" class="font-bold text-sm truncate" style="color: var(--color-text-base)">Teacher Portal</span>
        <button class="ml-auto text-xs p-1 rounded hover:opacity-70" style="color: var(--color-text-muted)" @click="collapsed = !collapsed">
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
        </RouterLink>
      </nav>

      <!-- Footer: back to student view -->
      <div class="px-2 py-3 border-t" style="border-color: var(--color-surface-04)">
        <RouterLink
          to="/dashboard"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition nav-idle hover:opacity-80"
        >
          <span class="text-lg shrink-0">🏠</span>
          <span v-if="!collapsed" class="truncate">Trang học viên</span>
        </RouterLink>
      </div>
    </aside>

    <!-- Main -->
    <div class="flex flex-col flex-1 min-w-0 overflow-hidden">
      <!-- Top bar -->
      <header class="flex items-center gap-3 px-6 h-16 shrink-0 border-b" style="background-color: var(--color-surface-01); border-color: var(--color-surface-04)">
        <div class="flex-1">
          <h1 class="text-base font-bold" style="color: var(--color-text-base)">{{ currentTitle }}</h1>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs px-2 py-1 rounded-full font-semibold" style="background-color: color-mix(in srgb, var(--color-primary-600) 20%, transparent); color: var(--color-primary-400)">
            {{ auth.user?.role === 'admin' ? 'Admin' : 'Giáo viên' }}
          </span>
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
  { to: '/teacher',         icon: '📊', label: 'Tổng quan' },
  { to: '/teacher/grading', icon: '✏️',  label: 'Chấm bài' },
  { to: '/teacher/classes', icon: '👥',  label: 'Lớp học' },
]

function isActive(path) {
  if (path === '/teacher') return route.path === '/teacher'
  return route.path.startsWith(path)
}

const currentTitle = computed(() => {
  const found = NAV.find(n => isActive(n.to))
  return found?.label || 'Teacher Portal'
})
</script>

<style scoped>
.nav-active {
  background-color: color-mix(in srgb, var(--color-primary-600) 18%, transparent);
  color: var(--color-primary-400);
}
.nav-idle { color: var(--color-text-muted); }
</style>
