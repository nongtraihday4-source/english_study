<template>
  <div class="skill-tree px-2 py-4 space-y-8">
    <div
      v-for="chapter in chapters"
      :key="chapter.id"
      class="skill-chapter"
    >
      <!-- Chapter label -->
      <div class="flex items-center gap-3 mb-4">
        <div
          class="h-0.5 flex-1 rounded"
          style="background: var(--color-surface-04)"
        />
        <span
          class="text-xs font-bold uppercase tracking-widest px-3 py-1 rounded-full"
          style="background: var(--color-surface-03); color: var(--color-text-muted)"
        >
          {{ chapter.title }}
        </span>
        <div
          class="h-0.5 flex-1 rounded"
          style="background: var(--color-surface-04)"
        />
      </div>

      <!-- Lesson nodes -->
      <div class="flex flex-col items-center gap-2">
        <template v-for="(lesson, idx) in chapter.lessons" :key="lesson.id">
          <!-- Connector line -->
          <div
            v-if="idx > 0"
            class="w-0.5 h-4 rounded"
            :style="connectorStyle(chapter.lessons[idx - 1])"
          />

          <!-- Lesson node -->
          <component
            :is="canNavigate(lesson) ? 'RouterLink' : 'div'"
            v-bind="canNavigate(lesson) ? {
              to: {
                name: `learn-${lesson.exercise_type || lesson.lesson_type}`,
                params: { id: lesson.exercise_id },
                query: { lesson_id: lesson.id }
              }
            } : {}"
            class="skill-node flex items-center gap-3 w-full max-w-sm px-4 py-3 rounded-2xl transition"
            :class="nodeClass(lesson)"
            :style="nodeStyle(lesson)"
            :title="nodeTitle(lesson)"
          >
            <!-- Status icon -->
            <span class="flex-shrink-0 text-xl">{{ nodeIcon(lesson) }}</span>

            <!-- Title -->
            <div class="flex-1 min-w-0">
              <p
                class="text-sm font-semibold truncate"
                :style="lesson.progress_status === 'completed'
                  ? 'color: #86efac'
                  : isLocked(lesson)
                    ? 'color: var(--color-text-muted)'
                    : 'color: var(--color-text-base)'"
              >
                {{ lesson.title }}
              </p>
              <p
                v-if="lesson.estimated_minutes"
                class="text-xs mt-0.5"
                style="color: var(--color-text-muted)"
              >
                ~{{ lesson.estimated_minutes }} phút
              </p>
            </div>

            <!-- Right badge -->
            <span class="flex-shrink-0 text-base">
              <span v-if="lesson.progress_status === 'completed'">✅</span>
              <span v-else-if="isLocked(lesson)">🔒</span>
              <span v-else style="color: #818cf8">▶</span>
            </span>
          </component>
        </template>

        <!-- Empty chapter fallback -->
        <p
          v-if="!chapter.lessons || !chapter.lessons.length"
          class="text-xs py-2"
          style="color: var(--color-text-muted)"
        >
          Chưa có bài học
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  chapters: {
    type: Array,
    default: () => [],
  },
})

function isLocked(lesson) {
  return lesson.is_unlocked === false || lesson.progress_status === 'locked'
}

function canNavigate(lesson) {
  return !isLocked(lesson) && !!lesson.exercise_id
}

function nodeIcon(lesson) {
  if (lesson.progress_status === 'completed') return '✅'
  if (isLocked(lesson)) return '🔒'
  const icons = { listening: '🎧', speaking: '🎤', reading: '📄', writing: '✍️' }
  return icons[lesson.exercise_type || lesson.lesson_type] || '📚'
}

function nodeClass(lesson) {
  if (lesson.progress_status === 'completed') return 'node-completed'
  if (isLocked(lesson)) return 'node-locked cursor-not-allowed select-none'
  return 'node-available hover:-translate-y-0.5 hover:shadow-md'
}

function nodeStyle(lesson) {
  if (lesson.progress_status === 'completed') {
    return 'background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3); text-decoration: none'
  }
  if (isLocked(lesson)) {
    return 'background: var(--color-surface-02); border: 1px solid var(--color-surface-04); opacity: 0.5; text-decoration: none'
  }
  return 'background: var(--color-surface-02); border: 1px solid rgba(99,102,241,0.4); text-decoration: none'
}

function nodeTitle(lesson) {
  if (lesson.is_unlocked === false) return 'Hoàn thành bài trước để mở khóa'
  if (lesson.progress_status === 'locked') return 'Hoàn thành bài trước để mở khóa'
  if (!lesson.exercise_id) return 'Chưa có bài tập'
  return ''
}

function connectorStyle(prevLesson) {
  if (prevLesson.progress_status === 'completed') {
    return 'background: rgba(34,197,94,0.5)'
  }
  return 'background: var(--color-surface-04)'
}
</script>

<style scoped>
.skill-node {
  text-decoration: none !important;
}
</style>
