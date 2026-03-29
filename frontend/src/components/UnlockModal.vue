<template>
  <Teleport to="body">
    <Transition name="unlock-fade">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
        @click="close"
      >
        <div class="text-center space-y-4 p-8" @click.stop>
          <div class="text-7xl animate-bounce">🔓</div>
          <h2 class="text-2xl font-bold" style="color: var(--color-primary-400)">
            Bài học mới đã mở khóa!
          </h2>
          <p class="text-lg" style="color: var(--color-text-base)">{{ lessonTitle }}</p>
          <p v-if="xpGained" class="font-semibold" style="color: var(--color-accent-gold, #f59e0b)">
            +{{ xpGained }} XP ⚡
          </p>
          <button
            @click="close"
            class="mt-4 px-6 py-2 rounded-lg font-semibold"
            style="background: var(--color-primary-400); color: white"
          >
            Tiếp tục
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { watch, onUnmounted } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  lessonTitle: { type: String, default: '' },
  xpGained: { type: Number, default: 0 },
})

const emit = defineEmits(['close'])

let dismissTimer = null

function close() {
  clearTimeout(dismissTimer)
  emit('close')
}

// Auto-dismiss after 3 seconds
watch(() => props.show, (val) => {
  clearTimeout(dismissTimer)
  if (val) {
    dismissTimer = setTimeout(() => emit('close'), 3000)
  }
})

onUnmounted(() => clearTimeout(dismissTimer))
</script>

<style scoped>
.unlock-fade-enter-active,
.unlock-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.unlock-fade-enter-from,
.unlock-fade-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
