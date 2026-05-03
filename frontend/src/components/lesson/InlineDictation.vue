<template>
  <div>
    <!-- Hint / translation toggle row -->
    <div class="flex items-center gap-3 mb-3">
      <button @click="playSentence"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition hover:opacity-80"
              style="background:rgba(6,182,212,0.12);color:#22d3ee;border:1px solid rgba(6,182,212,0.25)">
        <span v-if="ttsLoading" class="inline-block animate-spin text-xs">⏳</span>
        <span v-else>🔊 Nghe</span>
      </button>
      <button v-if="!hintVisible && fails >= 2"
              @click="hintVisible = true"
              class="text-xs px-2.5 py-1.5 rounded-xl transition hover:opacity-80"
              style="background:rgba(251,191,36,0.1);color:#fbbf24;border:1px solid rgba(251,191,36,0.25)">
        💡 Gợi ý
      </button>
      <span v-if="hintVisible"
            class="text-xs italic"
            style="color:#fbbf24">
        {{ props.sentence.hint }}
      </span>
    </div>

    <!-- Input area (hidden after correct) -->
    <div v-if="state !== 'correct'" class="flex gap-2">
      <input
        ref="inputRef"
        v-model="userInput"
        @keyup.enter="checkAnswer"
        :disabled="ttsLoading"
        :placeholder="state === 'wrong' ? 'Thử lại...' : 'Gõ câu bạn vừa nghe...'"
        class="flex-1 rounded-xl px-4 py-2.5 text-sm outline-none transition"
        :style="state === 'wrong'
          ? 'background:rgba(239,68,68,0.08);border:1.5px solid rgba(239,68,68,0.4);color:var(--color-text-base)'
          : 'background:var(--color-surface-03);border:1.5px solid var(--color-surface-04);color:var(--color-text-base)'"
      />
      <button @click="checkAnswer"
              class="px-4 py-2.5 rounded-xl text-sm font-medium transition hover:opacity-80"
              style="background:rgba(6,182,212,0.18);color:#22d3ee;border:1px solid rgba(6,182,212,0.35)">
        Kiểm tra
      </button>
    </div>

    <!-- Wrong feedback -->
    <Transition name="fade">
      <div v-if="state === 'wrong'" class="mt-2">
        <div class="flex flex-wrap gap-1">
          <span v-for="(w, wi) in diffTokens" :key="wi"
                class="px-1.5 py-0.5 rounded text-xs font-mono"
                :style="w.type === 'correct'
                  ? 'background:rgba(34,197,94,0.12);color:#86efac'
                  : w.type === 'wrong'
                    ? 'background:rgba(239,68,68,0.12);color:#fca5a5;text-decoration:line-through'
                    : 'background:rgba(251,191,36,0.12);color:#fbbf24'">
            {{ w.token }}
          </span>
        </div>
        <p class="text-xs mt-1" style="color:var(--color-text-muted)">
          Sai {{ fails }} lần — thử lại!
          <button v-if="fails >= 3" @click="revealAnswer"
                  class="ml-2 underline text-xs" style="color:#fbbf24">
            Xem đáp án
          </button>
        </p>
      </div>
    </Transition>

    <!-- Correct feedback -->
    <Transition name="fade">
      <div v-if="state === 'correct'"
           class="flex items-center gap-3 px-4 py-3 rounded-xl"
           style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.25)">
        <span class="text-lg">✅</span>
        <div>
          <p class="text-sm font-medium" style="color:#86efac">Chính xác!</p>
          <p class="text-xs" style="color:var(--color-text-muted)">{{ props.sentence.translation_vi }}</p>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useTTS } from '@/composables/useTTS.js'

const props = defineProps({
  sentence: { type: Object, required: true }, // { text, hint, translation_vi }
  done:     { type: Boolean, default: false },
})
const emit = defineEmits(['complete'])

const { speak, loadingText } = useTTS()
const ttsLoading = computed(() => loadingText.value !== '')

const userInput  = ref('')
const state      = ref('idle')   // idle | wrong | correct
const fails      = ref(0)
const hintVisible = ref(false)
const diffTokens  = ref([])
const inputRef    = ref(null)

function normalize(str) {
  return str.toLowerCase()
            .replace(/[.,!?;:'"()]/g, '')
            .replace(/\s+/g, ' ')
            .trim()
}

function checkAnswer() {
  const user    = normalize(userInput.value)
  const correct = normalize(props.sentence.text)
  if (!user) return
  if (user === correct) {
    state.value = 'correct'
    emit('complete')
    return
  }
  fails.value++
  state.value = 'wrong'
  diffTokens.value = buildDiff(user.split(' '), correct.split(' '))
  nextTick(() => inputRef.value?.focus())
}

function buildDiff(userWords, correctWords) {
  const len = Math.max(userWords.length, correctWords.length)
  const tokens = []
  for (let i = 0; i < len; i++) {
    const u = userWords[i]
    const c = correctWords[i]
    if (u === undefined) tokens.push({ token: c, type: 'missing' })
    else if (c === undefined) tokens.push({ token: u, type: 'wrong' })
    else if (u === c) tokens.push({ token: u, type: 'correct' })
    else tokens.push({ token: u, type: 'wrong' })
  }
  return tokens
}

function revealAnswer() {
  userInput.value = props.sentence.text
  state.value = 'correct'
  emit('complete')
}

function playSentence() {
  speak(props.sentence.text)
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity .2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
