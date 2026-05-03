<template>
    <div class="p-6 max-w-2xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-bold" style="color: var(--color-text-base)">Flashcards</h1>
          <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">Ôn tập từ vựng theo phương pháp spaced repetition</p>
        </div>
        <span class="text-sm font-semibold px-3 py-1.5 rounded-lg"
              style="background-color: var(--color-surface-03); color: var(--color-text-soft)">
          {{ currentIdx + 1 }} / {{ cards.length }}
        </span>
      </div>

      <div v-if="loading" class="h-64 rounded-2xl animate-pulse"
           style="background-color: var(--color-surface-02)"></div>

      <div v-else-if="cards.length === 0" class="text-center py-16" style="color: var(--color-text-muted)">
        <p class="text-4xl mb-3">🃏</p>
        <p>Không có flashcard nào trong hôm nay. Hãy quay lại sau!</p>
      </div>

      <!-- Card flip -->
      <div v-else class="flip-container cursor-pointer" :class="{ flipped: isFlipped }"
           @click="isFlipped = !isFlipped" style="height: 260px">
        <div class="flip-card">
          <div class="flip-front rounded-2xl flex flex-col items-center justify-center p-8 text-center"
               style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <p class="text-3xl font-black mb-2" style="color: var(--color-text-base)">
              {{ cards[currentIdx]?.front_text }}
            </p>
            <p class="text-sm" style="color: var(--color-primary-400)">
              {{ cards[currentIdx]?.phonetic }}
            </p>
            <p class="text-xs mt-4" style="color: var(--color-text-muted)">Nhấn để lật thẻ</p>
          </div>
          <div class="flip-back rounded-2xl flex flex-col items-center justify-center p-8 text-center"
               style="background-color: var(--color-surface-03); border: 1px solid var(--color-primary-600)">
            <p class="text-xl font-bold mb-2" style="color: var(--color-text-base)">
              {{ cards[currentIdx]?.back_text }}
            </p>
            <p class="text-sm" style="color: var(--color-text-muted)">
              {{ cards[currentIdx]?.example_sentence }}
            </p>
          </div>
        </div>
      </div>

      <!-- Rating buttons -->
      <div v-if="isFlipped && cards.length" class="flex gap-3 mt-5">
        <button @click="rateCard('again')"
                class="flex-1 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
                style="background-color: rgba(239,68,68,0.15); color: #fca5a5">
          Học lại
        </button>
        <button @click="rateCard('hard')"
                class="flex-1 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
                style="background-color: rgba(234,179,8,0.15); color: #fde68a">
          Khó
        </button>
        <button @click="rateCard('good')"
                class="flex-1 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
                style="background-color: rgba(34,197,94,0.15); color: #86efac">
          Biết rồi
        </button>
        <button @click="rateCard('easy')"
                class="flex-1 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-80"
                style="background-color: rgba(99,102,241,0.15); color: var(--color-primary-400)">
          Dễ
        </button>
      </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client.js'

const cards = ref([])
const loading = ref(false)
const currentIdx = ref(0)
const isFlipped = ref(false)

async function rateCard(rating) {
  const card = cards.value[currentIdx.value]
  if (!card) return
  try {
    await apiClient.post(`/vocabulary/flashcards/${card.id}/review/`, { rating })
  } catch { /* silent */ }
  isFlipped.value = false
  if (currentIdx.value < cards.value.length - 1) {
    currentIdx.value++
  } else {
    cards.value = []
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await apiClient.get('/vocabulary/flashcards/due/')
    const d = res.data?.data ?? res.data
    cards.value = d?.results || (Array.isArray(d) ? d : [])
  } catch {
    cards.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.flip-container { perspective: 1000px; }
.flip-card { position: relative; width: 100%; height: 100%; transform-style: preserve-3d; transition: transform 0.5s; }
.flipped .flip-card { transform: rotateY(180deg); }
.flip-front, .flip-back { position: absolute; inset: 0; backface-visibility: hidden; }
.flip-back { transform: rotateY(180deg); }
</style>
