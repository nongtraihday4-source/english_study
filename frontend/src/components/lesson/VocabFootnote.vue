<template>
  <div class="rounded-2xl overflow-hidden"
       style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
    <button
      class="w-full flex items-center justify-between px-5 py-3 transition hover:opacity-80"
      style="background-color:var(--color-surface-03);border-bottom:1px solid var(--color-surface-04)"
      @click="open = !open"
    >
      <span class="font-medium text-sm" style="color:var(--color-text-muted)">
        📝 Từ vựng trong bài ({{ items.length }} từ)
      </span>
      <span class="text-xs" style="color:var(--color-text-muted)">{{ open ? '▲' : '▼' }}</span>
    </button>
    <Transition name="collapse">
      <div v-show="open" class="px-5 py-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <div
            v-for="(item, i) in items" :key="i"
            class="rounded-xl p-3"
            style="background-color:var(--color-surface-03);border:1px solid var(--color-surface-04)"
          >
            <div class="flex items-center gap-1.5 flex-wrap mb-0.5">
              <span class="font-bold text-sm" style="color:var(--color-primary-500)">{{ item.word }}</span>
              <span v-if="item.pos" class="text-xs px-1 rounded"
                    style="background:var(--color-surface-04);color:var(--color-text-muted)">{{ item.pos }}</span>
              <span v-if="item.ipa" class="text-xs font-mono" style="color:var(--color-text-muted)">{{ item.ipa }}</span>
            </div>
            <p class="text-sm font-medium" style="color:var(--color-text-base)">{{ item.meaning_vi }}</p>
            <p v-if="item.definition_en" class="text-xs mt-0.5" style="color:var(--color-text-muted)">
              {{ item.definition_en }}
            </p>
            <div v-if="item.example_en"
                 class="mt-1.5 px-2 py-1.5 rounded-lg"
                 style="background:var(--color-surface-02);border-left:2px solid var(--color-primary-500)">
              <p class="text-xs italic" style="color:var(--color-text-base)">{{ item.example_en }}</p>
              <p v-if="item.example_vi" class="text-xs" style="color:var(--color-text-muted)">{{ item.example_vi }}</p>
            </div>
            <div v-if="item.collocations?.length" class="flex flex-wrap gap-1 mt-1.5">
              <span
                v-for="col in item.collocations.slice(0,3)" :key="col"
                class="text-xs px-1.5 py-0.5 rounded-full"
                style="background:rgba(99,102,241,0.1);color:#818cf8"
              >{{ col }}</span>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  items: { type: Array, default: () => [] },
})

const open = ref(false)
</script>

<style scoped>
.collapse-enter-active, .collapse-leave-active { transition: all .2s ease; overflow: hidden; }
.collapse-enter-from, .collapse-leave-to { max-height: 0; opacity: 0; }
.collapse-enter-to, .collapse-leave-from { max-height: 9999px; opacity: 1; }
</style>
