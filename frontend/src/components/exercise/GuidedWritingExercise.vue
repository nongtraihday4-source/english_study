<template>
  <div class="guided-writing-exercise">
    <div class="flex items-center gap-2 mb-3">
      <span class="text-xs px-2 py-0.5 rounded-full font-medium"
            style="background:rgba(251,146,60,0.12);color:#fb923c">✍️ Viết có hướng dẫn</span>
      <span v-if="done" class="text-xs font-medium" style="color:#86efac">✓ Hoàn thành</span>
    </div>

    <!-- Prompt -->
    <div class="px-4 py-3 rounded-xl mb-4"
         style="background:var(--color-surface-03);border-left:3px solid #fb923c">
      <p class="text-sm font-medium mb-1" style="color:var(--color-text-base)">{{ exercise.prompt }}</p>
      <p v-if="exercise.structure_hint" class="text-xs" style="color:#fb923c">
        💡 {{ exercise.structure_hint }}
      </p>
    </div>

    <!-- Writing phase -->
    <div v-if="phase !== 'submitted'">
      <textarea
        v-model="userText"
        :disabled="phase === 'submitted'"
        :placeholder="`Viết ${exercise.min_words}–${exercise.max_words} từ...`"
        rows="4"
        class="w-full px-4 py-3 rounded-xl text-sm outline-none resize-none transition"
        style="background:var(--color-surface-03);border:1px solid var(--color-surface-04);color:var(--color-text-base)"
      ></textarea>

      <!-- Word count bar -->
      <div class="mt-2 mb-3">
        <div class="flex justify-between text-xs mb-1" style="color:var(--color-text-muted)">
          <span>{{ wordCount }} từ</span>
          <span>Mục tiêu: {{ exercise.min_words }}–{{ exercise.max_words }} từ</span>
        </div>
        <div class="h-1.5 rounded-full overflow-hidden" style="background:var(--color-surface-04)">
          <div class="h-full rounded-full transition-all duration-300"
               :style="`width:${barPercent}%;background:${barColor}`"></div>
        </div>
      </div>

      <button @click="submit"
              :disabled="!canSubmit"
              class="px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
              :style="canSubmit
                ? 'background-color:var(--color-primary-500);color:#fff'
                : 'background:var(--color-surface-04);color:var(--color-text-muted);cursor:not-allowed'">
        Nộp bài
      </button>
    </div>

    <!-- Submitted phase: show user text + model answer -->
    <div v-else class="space-y-3">
      <div class="px-4 py-3 rounded-xl"
           style="background:var(--color-surface-03);border:1px solid var(--color-surface-04)">
        <p class="text-xs font-semibold uppercase tracking-wide mb-1" style="color:var(--color-text-muted)">Bài của bạn</p>
        <p class="text-sm leading-relaxed" style="color:var(--color-text-base);white-space:pre-wrap">{{ userText }}</p>
        <p class="text-xs mt-1" style="color:var(--color-text-muted)">{{ wordCount }} từ</p>
      </div>

      <div v-if="showAnswer && exercise.sample_answer">
        <div class="px-4 py-3 rounded-xl"
             style="background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.2)">
          <p class="text-xs font-semibold uppercase tracking-wide mb-1" style="color:#86efac">Đáp án mẫu</p>
          <p class="text-sm leading-relaxed" style="color:var(--color-text-base);white-space:pre-wrap">{{ exercise.sample_answer }}</p>
        </div>
      </div>

      <div class="flex gap-2 flex-wrap">
        <button v-if="!showAnswer && exercise.sample_answer"
                @click="showAnswer = true"
                class="px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
                style="background:rgba(34,197,94,0.1);color:#86efac;border:1px solid rgba(34,197,94,0.25)">
          Xem đáp án mẫu
        </button>
        <button @click="resetExercise"
                class="px-4 py-2 rounded-xl text-sm font-medium transition hover:opacity-80"
                style="background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)">
          Viết lại
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  exercise: { type: Object, required: true },
  done: { type: Boolean, default: false },
})
const emit = defineEmits(['complete'])

const userText = ref('')
const phase = ref('writing')  // writing | submitted
const showAnswer = ref(false)

const wordCount = computed(() =>
  userText.value.trim() === '' ? 0 : userText.value.trim().split(/\s+/).length
)

const minWords = computed(() => props.exercise.min_words ?? 15)
const maxWords = computed(() => props.exercise.max_words ?? 60)

const barPercent = computed(() => {
  if (wordCount.value === 0) return 0
  return Math.min(100, Math.round((wordCount.value / maxWords.value) * 100))
})

const barColor = computed(() => {
  if (wordCount.value < minWords.value) return '#f59e0b'
  if (wordCount.value > maxWords.value) return '#ef4444'
  return '#22c55e'
})

const canSubmit = computed(() =>
  wordCount.value >= minWords.value && wordCount.value <= maxWords.value
)

function submit() {
  if (!canSubmit.value) return
  phase.value = 'submitted'
  emit('complete')
}

function resetExercise() {
  userText.value = ''
  phase.value = 'writing'
  showAnswer.value = false
}
</script>
