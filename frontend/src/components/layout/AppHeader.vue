<template>
  <header
    class="flex items-center justify-between px-4 sm:px-6 py-3 shrink-0"
    style="background-color: var(--color-surface-02); border-bottom: 1px solid var(--color-surface-04)"
  >
    <!-- Left: hamburger + breadcrumb -->
    <div class="flex items-center gap-3">
      <button
        @click="$emit('toggle-sidebar')"
        class="p-1.5 rounded-lg transition"
        style="color: var(--color-text-muted)"
        :style="{ '--tw-bg-opacity': '1' }"
      >☰</button>
      <span class="text-sm font-semibold" style="color: var(--color-text-base)">
        {{ currentTitle }}
      </span>
    </div>

    <!-- Right: notifications + user menu -->
    <div class="flex items-center gap-2">
      <!-- Notification bell -->
      <button
        @click="showNotifs = !showNotifs"
        class="relative p-2 rounded-xl transition hover:opacity-80"
        style="color: var(--color-text-muted)"
      >
        🔔
        <span
          v-if="notifs.unreadCount() > 0"
          class="absolute top-1 right-1 w-4 h-4 rounded-full text-xs flex items-center justify-center font-bold text-white"
          style="background-color: var(--color-accent-500)"
        >{{ notifs.unreadCount() }}</span>
      </button>

      <!-- Level badge -->
      <div v-if="auth.isPremium"
        class="px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1"
        style="background: linear-gradient(135deg, #f59e0b22, #fbbf2422); border: 1px solid #f59e0b88; color: #fbbf24; box-shadow: 0 0 8px rgba(245, 158, 11, 0.2)"
      > 
        👑 {{ auth.user?.current_level || '—' }} 
      </div>
      <div v-else
        class="px-2.5 py-1 rounded-full text-xs font-bold border"
        style="border-color: var(--color-primary-600); color: var(--color-primary-400)"
      >{{ auth.user?.current_level || '—' }}</div>

      <!-- Theme toggle -->
      <ThemeToggle />

      <!-- Logout -->
      <button
        @click="handleLogout"
        class="text-xs px-3 py-1.5 rounded-xl transition font-medium"
        style="color: var(--color-text-muted)"
      >Đăng xuất</button>
    </div>

    <!-- Notification dropdown -->
    <Transition name="slide-down">
      <div
        v-if="showNotifs"
        class="absolute top-14 right-4 w-80 rounded-2xl shadow-2xl overflow-hidden z-50"
        style="background-color: var(--color-surface-03); border: 1px solid var(--color-surface-04)"
      >
        <div class="px-4 py-3 border-b flex items-center justify-between"
             style="border-color: var(--color-surface-04)">
          <span class="text-sm font-semibold" style="color: var(--color-text-base)">Thông báo</span>
          <button @click="showNotifs = false" style="color: var(--color-text-soft)">✕</button>
        </div>
        <div class="max-h-72 overflow-y-auto">
          <div v-if="notifs.items.length === 0" class="p-6 text-center text-sm"
               style="color: var(--color-text-soft)">Không có thông báo mới</div>
          <button
            v-for="n in notifs.items.slice(0, 8)"
            :key="n.id"
            @click="notifs.markRead(n.id)"
            class="w-full px-4 py-3 text-left text-sm transition hover:opacity-80"
            :style="n.is_read ? 'opacity:0.5' : ''"
            style="border-bottom: 1px solid var(--color-surface-04)"
          >
            <p class="font-medium mb-0.5" style="color: var(--color-text-base)">{{ n.title }}</p>
            <p class="text-xs" style="color: var(--color-text-muted)">{{ n.body }}</p>
          </button>
        </div>
      </div>
    </Transition>
  </header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useNotificationsStore } from '@/stores/notifications.js'
import ThemeToggle from '@/components/common/ThemeToggle.vue'

defineProps({ sidebarCollapsed: Boolean })
defineEmits(['toggle-sidebar'])

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const notifs = useNotificationsStore()
const showNotifs = ref(false)

const currentTitle = computed(() => route.meta.title || 'Dashboard')

onMounted(() => notifs.fetch())

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.2s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
