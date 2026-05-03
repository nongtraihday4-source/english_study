<template>
  <div class="flex flex-col min-h-screen" style="background-color: var(--color-surface)">
    <PublicNavbar />
    <main class="flex-1">
      <RouterView />
    </main>
    <PublicFooter />
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import PublicNavbar from './PublicNavbar.vue'
import PublicFooter from './PublicFooter.vue'
</script>
