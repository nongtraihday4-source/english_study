<template>
  <div v-if="pagination.count > 0" class="flex items-center justify-between px-4 py-3 border-t" style="border-color:var(--color-border)">
    <span class="text-xs" style="color:var(--color-text-muted)">
      {{ pagination.count }} kết quả
    </span>
    <div class="flex items-center gap-1">
      <button
        :disabled="!pagination.previous"
        @click="$emit('change', pagination.page - 1)"
        class="px-3 py-1.5 text-xs rounded-lg disabled:opacity-40"
        style="background-color:var(--color-surface-03);color:var(--color-text-base)"
      >‹ Trước</button>
      <span class="px-3 py-1.5 text-xs" style="color:var(--color-text-muted)">
        Trang {{ pagination.page }}
      </span>
      <button
        :disabled="!pagination.next"
        @click="$emit('change', pagination.page + 1)"
        class="px-3 py-1.5 text-xs rounded-lg disabled:opacity-40"
        style="background-color:var(--color-surface-03);color:var(--color-text-base)"
      >Sau ›</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  pagination: {
    type: Object,
    default: () => ({ count: 0, next: null, previous: null, page: 1 }),
  },
})
defineEmits(['change'])
</script>
