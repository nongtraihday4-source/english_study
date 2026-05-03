<template>
  <!-- Floating toggle button -->
  <button
    @click="store.toggle()"
    class="fixed bottom-6 right-6 z-50 w-12 h-12 rounded-full shadow-lg flex items-center justify-center transition-all duration-200 hover:scale-110"
    :style="store.enabled
      ? 'background-color: var(--color-primary-600); color: #fff; box-shadow: 0 0 0 4px rgba(99,102,241,0.25)'
      : 'background-color: var(--color-surface-02); color: var(--color-text-muted); border: 1px solid var(--color-surface-04)'"
    :title="store.enabled ? 'Tắt chế độ phát âm' : 'Bật chế độ phát âm'"
  >
    <svg v-if="store.enabled" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
      <path stroke-linecap="round" stroke-linejoin="round" d="M15.536 8.464a5 5 0 010 7.072M17.95 6.05a8 8 0 010 11.9M11 5L6 9H2v6h4l5 4V5z" />
    </svg>
    <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
      <path stroke-linecap="round" stroke-linejoin="round" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707A1 1 0 0112 5v14a1 1 0 01-1.707.707L5.586 15z" />
      <path stroke-linecap="round" stroke-linejoin="round" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
    </svg>
  </button>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { usePronunciationStore } from '@/stores/pronunciation.js'
import { useTTS } from '@/composables/useTTS.js'

const store = usePronunciationStore()
const tts = useTTS()

const ENGLISH_WORD_RE = /^[a-zA-Z'-]+$/

function getWordAtPoint(x, y) {
  let range
  if (document.caretPositionFromPoint) {
    const pos = document.caretPositionFromPoint(x, y)
    if (!pos || !pos.offsetNode) return null
    range = document.createRange()
    range.setStart(pos.offsetNode, pos.offset)
    range.setEnd(pos.offsetNode, pos.offset)
  } else if (document.caretRangeFromPoint) {
    range = document.caretRangeFromPoint(x, y)
  }
  if (!range) return null

  const node = range.startContainer
  if (node.nodeType !== Node.TEXT_NODE) return null

  const text = node.textContent
  const offset = range.startOffset

  let start = offset
  let end = offset
  while (start > 0 && /[a-zA-Z'-]/.test(text[start - 1])) start--
  while (end < text.length && /[a-zA-Z'-]/.test(text[end])) end++

  const word = text.slice(start, end).replace(/^['-]+|['-]+$/g, '')
  return word && word.length >= 2 && ENGLISH_WORD_RE.test(word) ? word : null
}

function handleClick(e) {
  if (!store.enabled) return

  // Explicit TTS trigger: element or ancestor has data-tts-word
  const ttsEl = e.target.closest('[data-tts-word]')
  if (ttsEl) {
    const ttsWord = ttsEl.dataset.ttsWord
    if (ttsWord) tts.speak(ttsWord, store.voice)
    return
  }

  const tag = e.target.tagName
  if (['BUTTON', 'A', 'INPUT', 'TEXTAREA', 'SELECT'].includes(tag)) return
  if (e.target.closest('button, a, input, textarea, select, [role="button"]')) return

  const word = getWordAtPoint(e.clientX, e.clientY)
  if (!word) return

  tts.speak(word, store.voice)
}

onMounted(() => document.addEventListener('click', handleClick, true))
onUnmounted(() => document.removeEventListener('click', handleClick, true))
</script>
