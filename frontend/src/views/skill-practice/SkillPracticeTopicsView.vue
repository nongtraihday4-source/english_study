<template>
  <div class="max-w-5xl mx-auto px-4 py-8">

    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <RouterLink to="/skill-practice" class="text-sm hover:opacity-70 transition" style="color:var(--color-text-muted)">
        ← Luyện Kỹ Năng
      </RouterLink>
      <span style="color:var(--color-surface-04)">/</span>
      <span class="text-sm font-semibold" style="color:var(--color-text-base)">{{ levelInfo?.label || props.level }}</span>
    </div>

    <!-- Level badge + title -->
    <div class="flex items-center gap-3 mb-6">
      <span class="text-3xl">{{ levelInfo?.emoji || '📚' }}</span>
      <div>
        <h1 class="text-xl font-bold" style="color:var(--color-text-base)">
          Chủ đề Level {{ props.level }}
        </h1>
        <p class="text-sm" style="color:var(--color-text-muted)">{{ levelInfo?.desc }}</p>
      </div>
    </div>

    <!-- Category filter pills -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button
        v-for="cat in categories"
        :key="cat"
        @click="activeCategory = cat"
        class="px-3 py-1.5 rounded-xl text-xs font-medium transition hover:opacity-80"
        :style="activeCategory === cat
          ? 'background:var(--color-primary-600);color:#fff'
          : 'background:var(--color-surface-03);color:var(--color-text-muted);border:1px solid var(--color-surface-04)'"
      >
        {{ cat === 'all' ? 'Tất cả' : cat }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="i in 9" :key="i" class="h-32 rounded-2xl animate-pulse" style="background:var(--color-surface-03)" />
    </div>

    <!-- Empty state -->
    <div v-else-if="filteredTopics.length === 0" class="text-center py-16">
      <p class="text-4xl mb-3">📭</p>
      <p class="text-sm" style="color:var(--color-text-muted)">Chưa có chủ đề nào cho cấp độ này.</p>
    </div>

    <!-- Topic grid -->
    <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
      <RouterLink
        v-for="topic in filteredTopics"
        :key="topic.topic_slug"
        :to="`/skill-practice/passages/${topic.topic_slug}?level=${props.level}`"
        class="group rounded-2xl p-5 transition hover:scale-[1.01]"
        style="background:var(--color-surface-02);border:1px solid var(--color-surface-04)"
      >
        <!-- Topic name -->
        <p class="text-sm font-semibold mb-1 line-clamp-2 group-hover:text-[#818cf8] transition" style="color:var(--color-text-base)">
          {{ topic.topic }}
        </p>

        <!-- Passage count + difficulty -->
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs font-medium" style="color:var(--color-text-muted)">
            {{ topic.passage_count }} bài
          </span>
          <div class="flex gap-1">
            <span v-if="topic.easy_count" class="text-[10px] px-1.5 py-0.5 rounded-full" style="background:rgba(34,197,94,0.1);color:#86efac">
              {{ topic.easy_count }} dễ
            </span>
            <span v-if="topic.medium_count" class="text-[10px] px-1.5 py-0.5 rounded-full" style="background:rgba(251,191,36,0.1);color:#fbbf24">
              {{ topic.medium_count }} tb
            </span>
            <span v-if="topic.hard_count" class="text-[10px] px-1.5 py-0.5 rounded-full" style="background:rgba(239,68,68,0.1);color:#fca5a5">
              {{ topic.hard_count }} khó
            </span>
          </div>
        </div>

        <!-- Progress indicators -->
        <div class="flex gap-3">
          <div class="flex items-center gap-1.5">
            <span class="text-xs">🎧</span>
            <div class="flex-1 h-1.5 w-16 rounded-full overflow-hidden" style="background:var(--color-surface-04)">
              <div
                class="h-full rounded-full transition-all"
                style="background:#22d3ee"
                :style="{ width: `${Math.min(100, Math.round(topic.dictation_completed / topic.passage_count * 100))}%` }"
              />
            </div>
            <span class="text-[10px]" style="color:var(--color-text-muted)">
              {{ topic.dictation_completed }}/{{ topic.passage_count }}
            </span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-xs">🎤</span>
            <div class="flex-1 h-1.5 w-16 rounded-full overflow-hidden" style="background:var(--color-surface-04)">
              <div
                class="h-full rounded-full transition-all"
                style="background:#818cf8"
                :style="{ width: `${Math.min(100, Math.round(topic.shadowing_completed / topic.passage_count * 100))}%` }"
              />
            </div>
            <span class="text-[10px]" style="color:var(--color-text-muted)">
              {{ topic.shadowing_completed }}/{{ topic.passage_count }}
            </span>
          </div>
        </div>
      </RouterLink>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { skillPracticeApi } from '@/api/skillPractice.js'

const route = useRoute()
const props = defineProps({ level: { type: String, default: 'B1' } })

const topics = ref([])
const loading = ref(true)
const activeCategory = ref('all')

const levelMeta = {
  A1: { label: 'Sơ cấp', emoji: '🌱', desc: 'Từ vựng và cấu trúc cơ bản nhất.' },
  A2: { label: 'Sơ - Trung cấp', emoji: '🌿', desc: 'Giao tiếp hàng ngày và tình huống đơn giản.' },
  B1: { label: 'Trung cấp', emoji: '⭐', desc: 'Diễn đạt ý kiến và mô tả kinh nghiệm.' },
  B2: { label: 'Trên trung cấp', emoji: '🌟', desc: 'Thảo luận các chủ đề trừu tượng và chuyên ngành.' },
  C1: { label: 'Cao cấp', emoji: '🔥', desc: 'Tiếng Anh học thuật và chuyên nghiệp.' },
  C2: { label: 'Thành thạo', emoji: '💎', desc: 'Thành thạo hoàn toàn như người bản ngữ.' },
}

const levelInfo = computed(() => levelMeta[props.level])

// Extract category prefix: "Daily Life - Housing" → "Daily Life"
const categories = computed(() => {
  const cats = new Set(['all'])
  topics.value.forEach(t => {
    const cat = t.topic.split(' - ')[0]
    if (cat) cats.add(cat)
  })
  return [...cats]
})

const filteredTopics = computed(() => {
  if (activeCategory.value === 'all') return topics.value
  return topics.value.filter(t => t.topic.startsWith(activeCategory.value))
})

async function loadTopics() {
  loading.value = true
  try {
    const res = await skillPracticeApi.getTopics({ level: props.level })
    topics.value = res.data
  } catch {
    topics.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadTopics)
watch(() => props.level, loadTopics)
</script>
