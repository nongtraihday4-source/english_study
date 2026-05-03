<template>
  <header
    class="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
    :class="scrolled
      ? 'shadow-md'
      : 'shadow-none'"
    style="background-color: var(--color-surface-02); border-bottom: 1px solid var(--color-surface-04)"
  >
    <nav class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">

        <!-- Logo -->
        <RouterLink to="/" class="flex items-center gap-2 flex-shrink-0 group">
          <div
            class="w-8 h-8 rounded-lg flex items-center justify-center text-white font-black text-sm"
            style="background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-600))"
          >ES</div>
          <span class="font-black text-lg tracking-tight" style="font-family: var(--font-heading); color: var(--color-secondary)">
            English<span style="color: var(--color-primary-500)">Study</span>
          </span>
        </RouterLink>

        <!-- Desktop nav links -->
        <div class="hidden md:flex items-center gap-1">
          <RouterLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="px-3 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-80"
            :style="isActive(link.to)
              ? 'color: var(--color-primary-500); background-color: var(--color-primary-50)'
              : 'color: var(--color-text-muted)'"
          >{{ link.label }}</RouterLink>
        </div>

        <!-- Right: ThemeToggle + CTA -->
        <div class="hidden md:flex items-center gap-2">
          <ThemeToggle />
          <template v-if="auth.isLoggedIn">
            <RouterLink
              to="/dashboard"
              class="px-4 py-2 rounded-xl text-sm font-semibold transition"
              style="background-color: var(--color-primary-500); color: #fff"
            >Dashboard →</RouterLink>
          </template>
          <template v-else>
            <RouterLink
              to="/login"
              class="px-4 py-2 rounded-xl text-sm font-semibold transition hover:opacity-80"
              style="color: var(--color-secondary); border: 1.5px solid var(--color-surface-04)"
            >Đăng nhập</RouterLink>
            <RouterLink
              to="/register"
              class="px-4 py-2 rounded-xl text-sm font-semibold transition hover:opacity-80"
              style="background-color: var(--color-primary-500); color: #fff"
            >Đăng ký miễn phí</RouterLink>
          </template>
        </div>

        <!-- Mobile hamburger -->
        <div class="flex md:hidden items-center gap-2">
          <ThemeToggle />
          <button
            @click="menuOpen = !menuOpen"
            class="w-9 h-9 flex items-center justify-center rounded-xl transition"
            style="color: var(--color-text-muted); border: 1px solid var(--color-surface-04)"
          >
            <span class="text-lg">{{ menuOpen ? '✕' : '☰' }}</span>
          </button>
        </div>
      </div>

      <!-- Mobile menu -->
      <Transition name="mobile-menu">
        <div
          v-if="menuOpen"
          class="md:hidden pb-4 space-y-1"
          style="border-top: 1px solid var(--color-surface-04)"
        >
          <RouterLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            @click="menuOpen = false"
            class="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition"
            :style="isActive(link.to)
              ? 'color: var(--color-primary-500); background-color: var(--color-primary-50)'
              : 'color: var(--color-text-muted)'"
          >{{ link.label }}</RouterLink>

          <div class="pt-2 flex flex-col gap-2 px-3">
            <template v-if="auth.isLoggedIn">
              <RouterLink
                to="/dashboard"
                @click="menuOpen = false"
                class="w-full text-center px-4 py-2.5 rounded-xl text-sm font-semibold"
                style="background-color: var(--color-primary-500); color: #fff"
              >Dashboard →</RouterLink>
            </template>
            <template v-else>
              <RouterLink
                to="/login"
                @click="menuOpen = false"
                class="w-full text-center px-4 py-2.5 rounded-xl text-sm font-semibold border"
                style="color: var(--color-secondary); border-color: var(--color-surface-04)"
              >Đăng nhập</RouterLink>
              <RouterLink
                to="/register"
                @click="menuOpen = false"
                class="w-full text-center px-4 py-2.5 rounded-xl text-sm font-semibold"
                style="background-color: var(--color-primary-500); color: #fff"
              >Đăng ký miễn phí</RouterLink>
            </template>
          </div>
        </div>
      </Transition>
    </nav>
  </header>

  <!-- Spacer so content doesn't hide behind fixed navbar -->
  <div class="h-16"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import ThemeToggle from '@/components/common/ThemeToggle.vue'

const auth = useAuthStore()
const route = useRoute()
const menuOpen = ref(false)
const scrolled = ref(false)

const navLinks = [
  { to: '/',        label: 'Trang chủ'  },
  { to: '/about',   label: 'Giới thiệu' },
  { to: '/pricing', label: 'Bảng giá'   },
  { to: '/blog',    label: 'Blog'        },
]

function isActive(path) {
  return path === '/' ? route.path === '/' : route.path.startsWith(path)
}

function onScroll() {
  scrolled.value = window.scrollY > 12
}

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<style scoped>
.mobile-menu-enter-active,
.mobile-menu-leave-active { transition: all 0.2s ease; }
.mobile-menu-enter-from,
.mobile-menu-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
