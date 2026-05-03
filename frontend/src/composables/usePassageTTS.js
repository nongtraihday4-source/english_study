import { ref } from 'vue'
import apiClient from '@/api/client.js'

// Cache blob URLs for passage text across the session
const blobUrlCache = new Map()

let currentAudio = null

// Shared reactive state
const isPlaying = ref(false)
const isPaused = ref(false)
const isLoading = ref(false)

export function usePassageTTS() {
  async function play(text, voice, rate) {
    if (!text || !text.trim()) return

    const plainText = text.trim()
    const cacheKey = `${plainText}|${voice || ''}`

    // Stop any currently playing audio
    _stop()

    isLoading.value = true

    let blobUrl = blobUrlCache.get(cacheKey)

    if (!blobUrl) {
      try {
        const resp = await apiClient.get('/pronunciation/tts/', {
          params: { text: plainText, voice: voice || undefined },
          responseType: 'blob',
        })
        blobUrl = URL.createObjectURL(resp.data)
        blobUrlCache.set(cacheKey, blobUrl)
      } catch (e) {
        console.warn('[PassageTTS] fetch failed:', e?.response?.status, e?.message)
        isLoading.value = false
        return
      }
    }

    isLoading.value = false

    try {
      const audio = new Audio(blobUrl)
      if (rate && rate !== 1.0) audio.playbackRate = rate
      currentAudio = audio
      isPlaying.value = true
      isPaused.value = false

      audio.addEventListener('ended', () => {
        isPlaying.value = false
        isPaused.value = false
        currentAudio = null
      })
      audio.addEventListener('error', () => {
        isPlaying.value = false
        isPaused.value = false
        currentAudio = null
      })

      await audio.play()
    } catch (e) {
      console.warn('[PassageTTS] play() rejected:', e?.message)
      isPlaying.value = false
      isPaused.value = false
      currentAudio = null
    }
  }

  function pause() {
    if (currentAudio && isPlaying.value && !isPaused.value) {
      currentAudio.pause()
      isPlaying.value = false
      isPaused.value = true
    }
  }

  function resume() {
    if (currentAudio && isPaused.value) {
      currentAudio.play()
      isPlaying.value = true
      isPaused.value = false
    }
  }

  function setRate(rate) {
    if (currentAudio) {
      currentAudio.playbackRate = rate
    }
  }

  function _stop() {
    if (currentAudio) {
      currentAudio.pause()
      currentAudio = null
    }
    isPlaying.value = false
    isPaused.value = false
    isLoading.value = false
  }

  function stop() {
    _stop()
  }

  return { play, pause, resume, stop, setRate, isPlaying, isPaused, isLoading }
}
