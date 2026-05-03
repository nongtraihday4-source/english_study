import { ref, watch } from 'vue'
import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref('light')

  function applyTheme(value) {
    document.documentElement.setAttribute('data-theme', value)
  }

  function initTheme() {
    const saved = localStorage.getItem('es-theme')
    theme.value = saved === 'dark' ? 'dark' : 'light'
    applyTheme(theme.value)
  }

  function setTheme(value) {
    theme.value = value
    localStorage.setItem('es-theme', value)
    applyTheme(value)
  }

  function toggleTheme() {
    setTheme(theme.value === 'dark' ? 'light' : 'dark')
  }

  const isDark = () => theme.value === 'dark'

  return { theme, initTheme, setTheme, toggleTheme, isDark }
})
