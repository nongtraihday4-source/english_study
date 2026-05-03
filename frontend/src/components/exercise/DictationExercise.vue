<template>
  <div class="dictation-exercise">
    <div class="flex items-center gap-2 mb-3">
      <span class="text-xs px-2 py-0.5 rounded-full font-medium"
            style="background:rgba(6,182,212,0.12);color:#22d3ee">🎧 Chính tả</span>
      <span v-if="done" class="text-xs font-medium" style="color:#86efac">✓ Hoàn thành</span>
    </div>

    <p class="text-sm font-medium mb-3" style="color:var(--color-text-base)">
      Nghe và gõ lại câu bạn vừa nghe.
    </p>

    <!-- Audio controls -->
    <div class="flex items-center gap-3 mb-4">
      <button @click="playAudio"
              :disabled="ttsLoading"
              class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
              style="background:rgba(6,182,212,0.12);color:#22d3ee;border:1px solid rgba(6,182,212,0.25)">
        <span v-if="ttsLoading" class="animate-spin">⏳</span>
        <span v-else-if="ttsPlaying">⏹ Đang phát...</span>
        <span v-else>▶ Nghe câu</span>
      </button>
      <span v-if="playCount > 0" class="text-xs" style="color:var(--color-text-muted)">
        Đã nghe {{ playCount }} lần
      </span>
    </div>

    <!-- Input -->
    <div class="mb-3">
      <input
        v-model="userInput"
        @keydown.enter="checkAnswer"
        :disabled="state === 'correct'"
        type="text"
        placeholder="Gõ câu bạn nghe được..."
        class="w-full px-4 py-2.5 rounded-xl text-sm outline-none transition"
        style="background:var(--color-surface-03);border:1px solid var(--color-surface-04);color:var(--color-text-base)"
      />
    </div>

    <!-- Word-level diff result -->
    <Transition name="fade">
      <div v-if="state !== 'idle'" class="mb-3 px-4 py-3 rounded-xl text-sm leading-relaxed"
           :style="state === 'correct'
             ? 'background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.25)'
             : 'background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.25)'">
        <span v-for="(token, ti) in diffResult" :key="ti"
              :style="token.match
                ? 'color:#86efac'
                : 'color:#fca5a5;text-decoration:underline;text-decoration-style:wavy'">
          {{ token.word }}{{ ti < diffResult.length - 1 ? ' ' : '' }}
        </span>
        <span v-if="state === 'correct'" class="ml-2 font-semibold" style="color:#86efac">✓ Đúng!</span>
      </div>
    </Transition>

    <!-- Hint after 2nd fail -->
    <Transition name="fade">
      <div v-if="showHint && exercise.hint" class="mb-3 px-3 py-2 rounded-lg text-xs"
           style="background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.25);color:#fbbf24">
        💡 Gợi ý: {{ exercise.hint }}
      </div>
    </Transition>

    <!-- Check / Next buttons -->
    <div class="flex gap-2">
      <button v-if="state !== 'correct'"
              @click="checkAnswer"
              :disabled="!userInput.trim() || !playCount"
              class="px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
              :style="(!userInput.trim() || !playCount)
                ? 'background:var(--color-surface-04);color:var(--color-text-muted);cursor:not-allowed'
                : 'background:rgba(99,102,241,0.15);color:#818cf8;border:1px solid rgba(99,102,241,0.3)'">
        Kiểm tra
      </button>
      <button v-if="state === 'wrong' && exercise.hint"
              @click="showHint = true"
              class="px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
              style="background:rgba(251,191,36,0.1);color:#fbbf24;border:1px solid rgba(251,191,36,0.25)">
        Gợi ý
      </button>
      <button v-if="state === 'wrong'"
              @click="retry"
              class="px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
              style="background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)">
        Thử lại
      </button>
      <button v-if="state === 'correct' && !done"
              @click="$emit('complete')"
              class="px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
              style="background-color:var(--color-primary-500);color:#fff">
        Tiếp tục →
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useTTS } from '@/composables/useTTS.js'

const props = defineProps({
  exercise: { type: Object, required: true },
  done: { type: Boolean, default: false },
})
const emit = defineEmits(['complete'])

const { speak, stop, speaking, loadingText } = useTTS()

const userInput = ref('')
const state = ref('idle')   // idle | wrong | correct
const diffResult = ref([])
const showHint = ref(false)
const playCount = ref(0)
const failCount = ref(0)

const ttsLoading = computed(() => loadingText.value === props.exercise.audio_text?.trim().toLowerCase())
const ttsPlaying = computed(() => speaking.value)

async function playAudio() {
  if (ttsLoading.value || ttsPlaying.value) { stop(); return }
  await speak(props.exercise.audio_text)
  playCount.value++
}

function normalizeWords(str) {
  return str.trim().toLowerCase().replace(/[.,!?;:'"]/g, '').split(/\s+/).filter(Boolean)
}

function checkAnswer() {
  if (!userInput.value.trim() || !playCount.value) return
  const target = normalizeWords(props.exercise.audio_text)
  const input  = normalizeWords(userInput.value)

  diffResult.value = target.map((word, i) => ({
    word,
    match: input[i] === word,
  }))

  const correct = diffResult.value.every(t => t.match)
  if (correct) {
    state.value = 'correct'
    emit('complete')
  } else {
    state.value = 'wrong'
    failCount.value++
    if (failCount.value >= 2) showHint.value = true
  }
}

function retry() {
  userInput.value = ''
  state.value = 'idle'
  diffResult.value = []
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity .25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
