import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

const STORAGE_KEY = 'pronunciation_settings'

export const usePronunciationStore = defineStore('pronunciation', () => {
  // Load persisted settings
  const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')

  const enabled = ref(saved.enabled ?? false)
  const voice = ref(saved.voice || 'en-GB-SoniaNeural')

  // Persist on change
  watch([enabled, voice], () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      enabled: enabled.value,
      voice: voice.value,
    }))
  }, { deep: true })

  function toggle() {
    enabled.value = !enabled.value
  }

  return { enabled, voice, toggle }
})
