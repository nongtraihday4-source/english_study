import { ref } from 'vue'
import apiClient from '@/api/client.js'

// word+voice → blob URL (blob:...) ready to play — survives the session
const blobUrlCache = new Map()

let currentAudio = null

// Module-level shared state (all useTTS() calls share the same refs)
const speaking = ref(false)
const speakingText = ref('')
const loadingText = ref('')

export function useTTS() {
  async function speak(text, voice) {
    if (!text || !text.trim()) return

    const word = text.trim().toLowerCase()
    const cacheKey = `${word}|${voice || ''}`

    // Stop any currently playing audio
    if (currentAudio) {
      currentAudio.pause()
      currentAudio = null
      speaking.value = false
    }

    // ── Get blob URL (cached or fetch from API) ───────────────────
    let blobUrl = blobUrlCache.get(cacheKey)

    if (!blobUrl) {
      loadingText.value = word
      try {
        // GET /api/v1/pronunciation/tts/?text=...&voice=...
        // Returns audio/mpeg binary directly — goes through /api/ proxy (always works)
        const resp = await apiClient.get('/pronunciation/tts/', {
          params: { text: word, voice: voice || undefined },
          responseType: 'blob',
        })
        blobUrl = URL.createObjectURL(resp.data)
        blobUrlCache.set(cacheKey, blobUrl)
      } catch (e) {
        console.warn('[TTS] fetch failed:', e?.response?.status, e?.message)
        loadingText.value = ''
        return
      }
      loadingText.value = ''
    }

    // ── Play from blob URL ────────────────────────────────────────
    try {
      const audio = new Audio(blobUrl)
      currentAudio = audio
      speaking.value = true
      speakingText.value = word

      audio.addEventListener('ended', () => {
        speaking.value = false
        speakingText.value = ''
        currentAudio = null
      })
      audio.addEventListener('error', (e) => {
        console.warn('[TTS] audio element error:', e)
        speaking.value = false
        speakingText.value = ''
        currentAudio = null
      })

      await audio.play()
    } catch (e) {
      console.warn('[TTS] play() rejected:', e?.message)
      speaking.value = false
      speakingText.value = ''
      currentAudio = null
    }
  }

  function stop() {
    if (currentAudio) {
      currentAudio.pause()
      currentAudio = null
    }
    speaking.value = false
    speakingText.value = ''
    loadingText.value = ''
  }

  return { speak, stop, speaking, speakingText, loadingText }
}
