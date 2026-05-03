<template>
  <RouterView />
</template>

<script setup>
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme.js'

const themeStore = useThemeStore()
onMounted(() => themeStore.initTheme())
</script>
