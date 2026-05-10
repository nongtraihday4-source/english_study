<template>
  <div v-if="lessonStore.srsQueue.length" class="rounded-2xl overflow-hidden mb-5"
       style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
    <div class="flex items-center justify-between px-5 py-3"
         style="background-color:var(--color-surface-03);border-bottom:1px solid var(--color-surface-04)">
      <span class="font-semibold text-sm" style="color:var(--color-text-base)">🔁 Ôn tập từ vựng (SRS)</span>
      <span class="text-xs" style="color:var(--color-text-muted)">{{ lessonStore.srsQueue.length }} từ đến hạn</span>
    </div>
    <div class="px-5 py-4 space-y-2">
      <div v-for="card in lessonStore.srsQueue" :key="card.id"
           class="flex items-center justify-between p-2 rounded-lg"
           style="background:var(--color-surface-03)">
        <span class="text-sm font-medium" style="color:var(--color-text-base)">{{ card.word }}</span>
        <button @click="markReviewed(card.id)" class="text-xs px-2 py-1 rounded-lg transition hover:opacity-80"
                style="background:rgba(34,197,94,0.15);color:#86efac">
          ✓ Đã thuộc
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useLessonStore } from '@/stores/lesson.js'

const lessonStore = useLessonStore()

function markReviewed(cardId) {
  lessonStore.srsQueue = lessonStore.srsQueue.filter(c => c.id !== cardId)
}
</script>
