<template>
  <button
    @click="themeStore.toggleTheme()"
    :title="themeStore.isDark() ? 'Chuyển chế độ sáng' : 'Chuyển chế độ tối'"
    class="relative w-9 h-9 flex items-center justify-center rounded-xl transition-all hover:opacity-80 focus:outline-none"
    style="background-color: var(--color-surface-03); border: 1px solid var(--color-surface-04)"
  >
    <Transition name="theme-icon" mode="out-in">
      <span v-if="themeStore.isDark()" key="sun" class="text-base leading-none">☀️</span>
      <span v-else key="moon" class="text-base leading-none">🌙</span>
    </Transition>
  </button>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme.js'

const themeStore = useThemeStore()
</script>

<style scoped>
.theme-icon-enter-active,
.theme-icon-leave-active { transition: opacity 0.15s, transform 0.15s; }
.theme-icon-enter-from { opacity: 0; transform: scale(0.7) rotate(-30deg); }
.theme-icon-leave-to   { opacity: 0; transform: scale(0.7) rotate(30deg); }
</style>
