<template>
  <div class="flex h-screen overflow-hidden" style="background-color: var(--color-surface)">
    <!-- Sidebar -->
    <AppSidebar :collapsed="sidebarCollapsed" @toggle="sidebarCollapsed = !sidebarCollapsed" />

    <!-- Main area -->
    <div class="flex flex-col flex-1 min-w-0 overflow-hidden">
      <AppHeader
        :sidebar-collapsed="sidebarCollapsed"
        @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed"
      />

      <!-- Page content -->
      <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
        <RouterView v-slot="{ Component, route }">
          <Transition name="fade" mode="out-in">
            <component :is="Component" :key="route.path" />
          </Transition>
        </RouterView>
      </main>
    </div>

    <!-- Global pronunciation mode toggle -->
    <PronunciationMode />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import PronunciationMode from '../PronunciationMode.vue'

const sidebarCollapsed = ref(false)
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
