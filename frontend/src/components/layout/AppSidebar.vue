<template>
  <aside
    class="flex flex-col shrink-0 overflow-hidden transition-all duration-300"
    :class="collapsed ? 'w-16' : 'w-62'"
    style="background-color: var(--color-surface-02); border-right: 1px solid var(--color-surface-04)"
  >
    <!-- Logo -->
    <div class="flex items-center gap-3 px-4 py-5 border-b shrink-0" style="border-color: var(--color-surface-04)">
      <div class="w-8 h-8 rounded-xl flex items-center justify-center text-white font-black text-sm shrink-0"
           style="background: linear-gradient(135deg, #6366f1, #8b5cf6)">ES</div>
      <Transition name="fade">
        <span v-if="!collapsed" class="font-bold text-sm tracking-wide" style="color: var(--color-text-base)">
          English Study
        </span>
      </Transition>
    </div>

    <!-- Nav items -->
    <nav class="flex-1 py-4 overflow-y-auto overflow-x-hidden">
      <div v-for="group in navGroups" :key="group.label" class="mb-4">
        <Transition name="fade">
          <p v-if="!collapsed" class="px-4 mb-1 text-xs font-semibold uppercase tracking-widest"
             style="color: var(--color-text-soft)">{{ group.label }}</p>
        </Transition>
        <RouterLink
          v-for="item in group.items" :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 mx-2 px-3 py-2.5 rounded-xl text-sm font-medium transition-all"
          :class="[
            $route.path.startsWith(item.to) && item.to !== '/'
              ? 'text-white' : 'hover:text-white',
          ]"
          :style="$route.path.startsWith(item.to) && item.to !== '/'
            ? 'background-color: var(--color-primary-600); color: white'
            : 'color: var(--color-text-muted)'"
        >
          <span class="text-lg shrink-0">{{ item.icon }}</span>
          <Transition name="fade">
            <span v-if="!collapsed">{{ item.label }}</span>
          </Transition>
        </RouterLink>
      </div>
    </nav>

    <!-- Upgrade CTA for free users -->
    <RouterLink
      v-if="!auth.isPremium && !collapsed"
      to="/pricing"
      class="upgrade-cta"
    >
      <span class="upgrade-icon">✨</span>
      <span>Nâng cấp Premium</span>
    </RouterLink>
    <RouterLink
      v-if="!auth.isPremium && collapsed"
      to="/pricing"
      class="upgrade-cta-mini"
      title="Nâng cấp Premium"
    >
      ✨
    </RouterLink>

    <!-- User info at bottom -->
    <div class="shrink-0 p-3 border-t" style="border-color: var(--color-surface-04)">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 relative"
             :style="auth.isPremium ? 'background: linear-gradient(135deg, #f59e0b, #fbbf24); color: #1a1400; box-shadow: 0 0 12px rgba(245, 158, 11, 0.3)' : 'background-color: var(--color-primary-700); color: white'">
          {{ avatarInitials }}
          <span v-if="auth.isPremium" class="absolute -top-1.5 -right-1 text-[11px] drop-shadow-md">👑</span>
        </div>
        <Transition name="fade">
          <div v-if="!collapsed" class="flex-1 min-w-0">
            <p class="text-sm font-medium truncate" 
               :style="auth.isPremium ? 'background: linear-gradient(135deg, #fbbf24, #f59e0b); -webkit-background-clip: text; -webkit-text-fill-color: transparent;' : 'color: var(--color-text-base)'">
              {{ auth.displayName }}
            </p>
            <p class="text-xs truncate" :style="auth.isPremium ? 'color: #fbbf24; font-weight: 600;' : 'color: var(--color-text-soft)'">
              {{ auth.user?.current_level }} · {{ accountLabel }}
            </p>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Collapse toggle -->
    <button
      @click="$emit('toggle')"
      class="w-full py-2 text-sm flex items-center justify-center transition hover:opacity-80"
      style="color: var(--color-text-soft); border-top: 1px solid var(--color-surface-04)"
    >
      {{ collapsed ? '→' : '←' }}
    </button>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth.js'

defineProps({ collapsed: Boolean })
defineEmits(['toggle'])

const auth = useAuthStore()

const avatarInitials = computed(() => {
  const name = auth.displayName || ''
  return name.slice(0, 2).toUpperCase() || 'ES'
})

const accountLabel = computed(() =>
  auth.isPremium ? 'Premium ✦' : 'Free'
)

const navGroups = [
  {
    label: 'Học tập',
    items: [
      { to: '/dashboard', icon: '🏠', label: 'Dashboard' },
      { to: '/courses', icon: '📚', label: 'Khoá học' },
      { to: '/grammar', icon: '📖', label: 'Ngữ pháp' },
      { to: '/vocabulary', icon: '🔤', label: 'Từ vựng' },
      { to: '/pronunciation', icon: '🎙️', label: 'Phát âm' },
      { to: '/skill-practice', icon: '🎯', label: 'Luyện Kỹ Năng' },
      { to: '/flashcards', icon: '🃏', label: 'Flashcards' },
      { to: '/assessments', icon: '📝', label: 'Assessment' },
    ],
  },
  {
    label: 'Cộng đồng',
    items: [
      { to: '/leaderboard', icon: '🏆', label: 'Xếp hạng' },
      { to: '/achievements', icon: '🏅', label: 'Thành tựu' },
      { to: '/certificates', icon: '📜', label: 'Chứng chỉ' },
    ],
  },
  {
    label: 'Tài khoản',
    items: [
      { to: '/profile', icon: '👤', label: 'Hồ sơ' },
    ],
  },
]
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.w-62 { width: 15.5rem; }

/* Upgrade CTA */
.upgrade-cta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0.5rem 0.5rem;
  padding: 0.65rem 1rem;
  border-radius: 0.75rem;
  background: linear-gradient(135deg, #d97706, #fbbf24);
  color: #1a1400;
  font-size: 0.82rem;
  font-weight: 700;
  text-decoration: none;
  transition: opacity 0.15s, transform 0.15s;
  text-align: center;
  justify-content: center;
}
.upgrade-cta:hover {
  opacity: 0.9;
  transform: scale(1.02);
}
.upgrade-icon {
  font-size: 1rem;
}
.upgrade-cta-mini {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0.5rem auto;
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 0.6rem;
  background: linear-gradient(135deg, #d97706, #fbbf24);
  text-decoration: none;
  font-size: 1rem;
  transition: transform 0.15s;
}
.upgrade-cta-mini:hover {
  transform: scale(1.1);
}
</style>
