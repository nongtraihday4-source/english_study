<template>
  <Teleport to="body">
    <div
      class="word-audio-tooltip fixed z-[100] px-4 py-3 rounded-2xl shadow-xl flex items-center gap-3 animate-in"
      :style="positionStyle"
      style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); min-width: 120px"
    >
      <!-- Word text -->
      <span class="font-semibold text-sm" style="color: var(--color-text-base)">{{ word }}</span>

      <!-- Loading spinner -->
      <svg v-if="loading" class="w-5 h-5 animate-spin shrink-0" style="color: var(--color-primary-400)" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>

      <!-- Replay button -->
      <button
        v-else
        @click.stop="$emit('replay')"
        class="shrink-0 w-7 h-7 rounded-full flex items-center justify-center transition hover:opacity-80"
        :style="speaking
          ? 'background-color: var(--color-primary-600); color: #fff'
          : 'background-color: var(--color-surface-04); color: var(--color-text-muted)'"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.536 8.464a5 5 0 010 7.072M11 5L6 9H2v6h4l5 4V5z" />
        </svg>
      </button>

      <!-- Close button -->
      <button
        @click.stop="$emit('close')"
        class="shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-xs hover:opacity-70"
        style="color: var(--color-text-muted)"
      >&times;</button>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  word: { type: String, required: true },
  x: { type: Number, required: true },
  y: { type: Number, required: true },
  loading: { type: Boolean, default: false },
  speaking: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'replay'])

const positionStyle = computed(() => {
  const padding = 12
  // Position above the click point, centered horizontally
  let left = props.x - 60
  let top = props.y - 56

  // Keep within viewport
  if (left < padding) left = padding
  if (left + 160 > window.innerWidth) left = window.innerWidth - 160 - padding
  if (top < padding) top = props.y + 20  // below if no room above

  return { left: `${left}px`, top: `${top}px` }
})

// Auto-dismiss after 4 seconds
let timer
onMounted(() => {
  timer = setTimeout(() => emit('close'), 4000)
})
onUnmounted(() => clearTimeout(timer))
</script>

<style scoped>
.animate-in {
  animation: tooltip-pop 0.15s ease-out;
}
@keyframes tooltip-pop {
  from { opacity: 0; transform: scale(0.9) translateY(4px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
</style>
