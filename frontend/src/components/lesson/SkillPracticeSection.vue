<template>
  <div>
    <!-- Section header -->
    <div class="flex items-center gap-2 mb-4">
      <span class="text-xl">🎯</span>
      <span class="text-base font-bold" style="color:var(--color-text-base)">Luyện tập kỹ năng</span>
      <span class="ml-auto text-xs font-medium px-2.5 py-0.5 rounded-full"
            :style="allDone
              ? 'background:rgba(34,197,94,0.15);color:#86efac'
              : 'background:rgba(251,146,60,0.12);color:#fb923c'">
        {{ doneCount }}/{{ totalCount }}
      </span>
    </div>

    <div class="space-y-5">

      <!-- 🎧 Dictation -->
      <div v-if="sections.dictation?.length"
           class="rounded-2xl overflow-hidden"
           style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
        <div class="flex items-center justify-between px-5 py-3"
             style="background-color:var(--color-surface-03);border-bottom:1px solid var(--color-surface-04)">
          <div class="flex items-center gap-2">
            <span class="text-base">🎧</span>
            <span class="font-semibold text-sm" style="color:var(--color-text-base)">Chính tả</span>
            <span class="text-xs" style="color:var(--color-text-muted)">Nghe và gõ lại câu</span>
          </div>
          <span class="text-xs font-medium px-2 py-0.5 rounded-full"
                :style="subsectionAllDone('dictation')
                  ? 'background:rgba(34,197,94,0.15);color:#86efac'
                  : 'background:rgba(6,182,212,0.12);color:#22d3ee'">
            {{ dictationDone }}/{{ sections.dictation.length }}
          </span>
        </div>
        <div class="px-5 py-4 space-y-6">
          <div v-for="(ex, i) in sections.dictation" :key="'d-' + i">
            <p v-if="sections.dictation.length > 1"
               class="text-xs font-medium mb-3"
               style="color:var(--color-text-muted)">
              Bài {{ i + 1 }}/{{ sections.dictation.length }}
            </p>
            <DictationExercise
              :exercise="ex"
              :done="doneMap['dictation_' + i]"
              @complete="markDone('dictation', i)"
            />
          </div>
        </div>
      </div>

      <!-- 🎤 Shadowing -->
      <div v-if="sections.shadowing?.length"
           class="rounded-2xl overflow-hidden"
           style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
        <div class="flex items-center justify-between px-5 py-3"
             style="background-color:var(--color-surface-03);border-bottom:1px solid var(--color-surface-04)">
          <div class="flex items-center gap-2">
            <span class="text-base">🎤</span>
            <span class="font-semibold text-sm" style="color:var(--color-text-base)">Shadowing</span>
            <span class="text-xs" style="color:var(--color-text-muted)">Nghe và đọc theo</span>
          </div>
          <span class="text-xs font-medium px-2 py-0.5 rounded-full"
                :style="subsectionAllDone('shadowing')
                  ? 'background:rgba(34,197,94,0.15);color:#86efac'
                  : 'background:rgba(99,102,241,0.12);color:#818cf8'">
            {{ shadowingDone }}/{{ sections.shadowing.length }}
          </span>
        </div>
        <div class="px-5 py-4 space-y-6">
          <div v-for="(ex, i) in sections.shadowing" :key="'s-' + i">
            <p v-if="sections.shadowing.length > 1"
               class="text-xs font-medium mb-3"
               style="color:var(--color-text-muted)">
              Bài {{ i + 1 }}/{{ sections.shadowing.length }}
            </p>
            <ShadowingExercise
              :exercise="ex"
              :done="doneMap['shadowing_' + i]"
              @complete="markDone('shadowing', i)"
            />
          </div>
        </div>
      </div>

      <!-- ✍️ Guided Writing -->
      <div v-if="sections.guided_writing?.length"
           class="rounded-2xl overflow-hidden"
           style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
        <div class="flex items-center justify-between px-5 py-3"
             style="background-color:var(--color-surface-03);border-bottom:1px solid var(--color-surface-04)">
          <div class="flex items-center gap-2">
            <span class="text-base">✍️</span>
            <span class="font-semibold text-sm" style="color:var(--color-text-base)">Viết có hướng dẫn</span>
            <span class="text-xs" style="color:var(--color-text-muted)">Áp dụng ngữ pháp vào viết</span>
          </div>
          <span class="text-xs font-medium px-2 py-0.5 rounded-full"
                :style="subsectionAllDone('guided_writing')
                  ? 'background:rgba(34,197,94,0.15);color:#86efac'
                  : 'background:rgba(251,146,60,0.12);color:#fb923c'">
            {{ guidedWritingDone }}/{{ sections.guided_writing.length }}
          </span>
        </div>
        <div class="px-5 py-4 space-y-6">
          <GuidedWritingExercise
            v-for="(ex, i) in sections.guided_writing" :key="'w-' + i"
            :exercise="ex"
            :done="doneMap['guided_writing_' + i]"
            @complete="markDone('guided_writing', i)"
          />
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { reactive, computed } from 'vue'
import DictationExercise from '@/components/exercise/DictationExercise.vue'
import ShadowingExercise from '@/components/exercise/ShadowingExercise.vue'
import GuidedWritingExercise from '@/components/exercise/GuidedWritingExercise.vue'

const props = defineProps({
  sections: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['progress'])

const doneMap = reactive({})

function markDone(type, index) {
  doneMap[`${type}_${index}`] = true
  emit('progress', { done: doneCount.value, total: totalCount.value })
}

const dictationDone = computed(() =>
  (props.sections.dictation || []).filter((_, i) => doneMap[`dictation_${i}`]).length
)
const shadowingDone = computed(() =>
  (props.sections.shadowing || []).filter((_, i) => doneMap[`shadowing_${i}`]).length
)
const guidedWritingDone = computed(() =>
  (props.sections.guided_writing || []).filter((_, i) => doneMap[`guided_writing_${i}`]).length
)

const doneCount = computed(() =>
  dictationDone.value + shadowingDone.value + guidedWritingDone.value
)
const totalCount = computed(() =>
  (props.sections.dictation?.length || 0)
  + (props.sections.shadowing?.length || 0)
  + (props.sections.guided_writing?.length || 0)
)
const allDone = computed(() => totalCount.value > 0 && doneCount.value >= totalCount.value)

function subsectionAllDone(type) {
  const arr = props.sections[type] || []
  return arr.length > 0 && arr.every((_, i) => doneMap[`${type}_${i}`])
}
</script>
