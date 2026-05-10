# 🎨 CURRICULUM APP — Frontend Architecture (Vue3)

> Tài liệu chi tiết về cấu trúc frontend và các Vue3 components

---

## 📑 MỤC LỤC

1. [Cấu trúc thư mục](#1-cấu-trúc-thư-mục)
2. [Views](#2-views)
3. [Components](#3-components)
4. [API Integration](#4-api-integration)
5. [State Management](#5-state-management)
6. [Routing](#6-routing)
7. [Styling](#7-styling)

---

## 1. CẤU TRÚC THƯ MỤC

```
frontend/src/
│
├── api/
│   ├── client.js                 # Axios instance
│   ├── curriculum.js             # Curriculum API
│   ├── exercises.js              # Exercises API
│   ├── grammar.js                # Grammar API
│   ├── progress.js               # Progress API
│   └── ...
│
├── views/
│   ├── CoursesView.vue           # ← List all courses (main view)
│   ├── CourseDetailView.vue      # ← Course detail + chapters
│   └── LessonDetailView.vue      # ← Lesson detail + content
│
├── components/
│   ├── lesson/                   # ← Lesson content sections
│   │   ├── ReadingSection.vue
│   │   ├── GrammarSection.vue
│   │   ├── ListeningSection.vue
│   │   ├── SpeakingSection.vue
│   │   ├── WritingSection.vue
│   │   ├── SkillPracticeSection.vue
│   │   ├── InlineDictation.vue
│   │   └── VocabFootnote.vue
│   │
│   ├── common/                   # ← Shared components
│   │   ├── SkillTreeView.vue    # Visual course progress tree
│   │   └── UnlockModal.vue      # Show prerequisites modal
│   │
│   ├── ui/                       # ← Generic UI components
│   │   ├── Button.vue
│   │   ├── Card.vue
│   │   ├── Modal.vue
│   │   └── ...
│   │
│   ├── dashboard/
│   ├── exercise/
│   └── ...
│
├── router/
│   └── index.js                  # Route definitions
│
├── stores/
│   ├── curriculum.js             # (Optional Pinia store)
│   └── ...
│
├── composables/
│   ├── useLessonContent.js       # Content composition logic
│   ├── useUnlock.js              # Unlock rules logic
│   └── ...
│
├── App.vue                       # Root component
├── main.js                       # Entry point
└── ...
```

---

## 2. VIEWS

### 2.1 CoursesView.vue

**Mục đích:** Hiển thị danh sách tất cả khóa học, có bộ lọc CEFR level.

```vue
<template>
  <div class="courses-container">
    <!-- Header -->
    <section class="header">
      <h1 class="text-2xl font-bold">🎓 Khoá học</h1>
      <p class="text-muted">Chọn khoá học phù hợp với trình độ của bạn</p>
    </section>

    <!-- Level Filters -->
    <section class="filters-section">
      <button
        v-for="level in cefrLevels"
        :key="level.code"
        @click="toggleLevel(level.code)"
        class="filter-btn"
        :class="{ active: activeLevel === level.code }"
      >
        <span class="level-badge">{{ level.code }}</span>
        <span class="level-name">{{ level.name_vi }}</span>
      </button>
    </section>

    <!-- Loading State -->
    <div v-if="loading" class="loading-grid">
      <div v-for="i in 6" :key="i" class="course-skeleton"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <p class="error-icon">⚠️</p>
      <p class="error-text">{{ error }}</p>
      <button @click="loadCourses" class="btn-retry">Thử lại</button>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredCourses.length === 0" class="empty-state">
      <p class="empty-icon">📚</p>
      <p class="empty-text">Không có khoá học nào phù hợp.</p>
    </div>

    <!-- Courses Grid -->
    <div v-else class="courses-grid">
      <RouterLink
        v-for="course in filteredCourses"
        :key="course.id"
        :to="`/courses/${course.id}`"
        class="course-card"
      >
        <!-- Card header with level badge -->
        <div class="card-header">
          <span class="level-badge" :style="levelBadgeStyle(course.level?.code)">
            {{ course.level?.code }}
          </span>
          <span class="lesson-count">{{ course.total_lessons }} bài</span>
        </div>

        <!-- Course title -->
        <h3 class="course-title">{{ course.title }}</h3>

        <!-- Course description (truncated) -->
        <p class="course-description">{{ truncate(course.description, 60) }}</p>

        <!-- Course metadata -->
        <div class="card-footer">
          <span v-if="course.is_premium" class="badge-premium">👑 Premium</span>
          <span v-else class="badge-free">Miễn phí</span>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { curriculumApi } from '@/api/curriculum'

// Reactive state
const courses = ref([])
const cefrLevels = ref([])
const activeLevel = ref('')
const loading = ref(false)
const error = ref(null)

// Computed properties
const filteredCourses = computed(() =>
  activeLevel.value
    ? courses.value.filter(c => c.level?.code === activeLevel.value)
    : courses.value
)

// Methods
const levelBadgeStyle = (code) => {
  const colorMap = {
    'A1': { bg: '#EFF6FF', color: '#0369A1' },    // Blue
    'A2': { bg: '#F0FDF4', color: '#15803D' },    // Green
    'B1': { bg: '#FFFBEB', color: '#B45309' },    // Amber
    'B2': { bg: '#FEF3C7', color: '#D97706' },    // Orange
    'C1': { bg: '#FEE2E2', color: '#DC2626' },    // Red
  }
  const style = colorMap[code] || { bg: '#F3F4F6', color: '#374151' }
  return {
    backgroundColor: style.bg,
    color: style.color,
  }
}

const truncate = (text, length) =>
  text && text.length > length ? text.substring(0, length) + '...' : text

const toggleLevel = (code) => {
  activeLevel.value = activeLevel.value === code ? '' : code
}

const loadCourses = async () => {
  loading.value = true
  error.value = null
  try {
    const [levelsRes, coursesRes] = await Promise.all([
      curriculumApi.getCefrLevels(),
      curriculumApi.getCourses({ ordering: 'level__order,created_at' })
    ])
    cefrLevels.value = levelsRes.data
    courses.value = coursesRes.data
  } catch (err) {
    error.value = err.response?.data?.detail || err.message
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadCourses()
})
</script>

<style scoped>
.courses-container {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  color: var(--color-text-base);
  margin-bottom: 0.5rem;
}

.header p {
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.filters-section {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.filter-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  background-color: var(--color-surface-03);
  border: 2px solid transparent;
  color: var(--color-text-soft);
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.filter-btn:hover {
  border-color: var(--color-primary-600);
}

.filter-btn.active {
  background-color: var(--color-primary-600);
  color: white;
  border-color: var(--color-primary-600);
}

.filter-btn .level-badge {
  font-weight: 700;
  font-size: 0.875rem;
}

.filter-btn .level-name {
  font-size: 0.75rem;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.course-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.25rem;
  border-radius: 1rem;
  background-color: var(--color-surface-02);
  border: 1px solid var(--color-surface-04);
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  border-color: var(--color-primary-600);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.level-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 700;
}

.lesson-count {
  color: var(--color-text-muted);
  font-size: 0.75rem;
  font-weight: 600;
}

.course-title {
  color: var(--color-text-base);
  font-size: 1rem;
  font-weight: 700;
  margin: 0;
}

.course-description {
  color: var(--color-text-muted);
  font-size: 0.875rem;
  margin: 0;
  flex-grow: 1;
  line-height: 1.4;
}

.card-footer {
  display: flex;
  gap: 0.5rem;
}

.badge-premium,
.badge-free {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.badge-premium {
  background-color: rgba(217, 119, 6, 0.1);
  color: #D97706;
}

.badge-free {
  background-color: rgba(34, 197, 94, 0.1);
  color: #22C55E;
}

/* Loading skeleton */
.loading-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.course-skeleton {
  height: 200px;
  border-radius: 1rem;
  background: linear-gradient(90deg, var(--color-surface-02) 25%, var(--color-surface-03) 50%, var(--color-surface-02) 75%);
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Error & Empty states */
.error-state,
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.error-icon,
.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-text,
.empty-text {
  color: var(--color-text-muted);
  margin-bottom: 1.5rem;
}

.btn-retry {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  background-color: var(--color-primary-600);
  color: white;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: opacity 0.2s;
}

.btn-retry:hover {
  opacity: 0.9;
}
</style>
```

---

### 2.2 CourseDetailView.vue

**Mục đích:** Hiển thị chi tiết khóa học (title, description, chapters + lessons), enrollment button.

```vue
<template>
  <div class="course-detail-container">
    <!-- Breadcrumb -->
    <div class="breadcrumb">
      <RouterLink to="/courses" class="breadcrumb-link">← Tất cả khoá học</RouterLink>
    </div>

    <!-- Loading skeleton -->
    <template v-if="loading">
      <div class="skeleton-header"></div>
      <div class="skeleton-chapters"></div>
    </template>

    <!-- Error state -->
    <div v-else-if="error" class="error-box">
      <p>⚠️ {{ error }}</p>
    </div>

    <!-- Course content -->
    <template v-else-if="course">
      <!-- Course Header Card -->
      <section class="course-header">
        <div class="header-content">
          <span class="level-badge" :style="levelBadgeStyle(course.level?.code)">
            {{ course.level?.code }}
          </span>
          <h1 class="course-title">{{ course.title }}</h1>
          <p class="course-description">{{ course.description }}</p>
        </div>

        <button
          v-if="!isEnrolled"
          @click="enrollCourse"
          :disabled="enrolling"
          class="btn-enroll"
        >
          {{ enrolling ? '⏳ Đang đăng ký...' : '📚 Đăng ký học' }}
        </button>
        <div v-else class="enrolled-badge">
          ✓ Bạn đã đăng ký
        </div>
      </section>

      <!-- Course Stats -->
      <section class="course-stats">
        <div class="stat-item">
          <span class="stat-value">{{ course.chapters?.length }}</span>
          <span class="stat-label">Chương</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ course.total_lessons }}</span>
          <span class="stat-label">Bài học</span>
        </div>
      </section>

      <!-- Chapters & Lessons -->
      <section class="chapters-section">
        <div v-for="(chapter, chIdx) in course.chapters" :key="chapter.id" class="chapter-block">
          <div class="chapter-header">
            <h2 class="chapter-title">
              <span class="chapter-number">Ch{{ chapter.order }}</span>
              {{ chapter.title }}
            </h2>
            <span class="lesson-count">{{ chapter.lessons?.length || 0 }} bài</span>
          </div>

          <p v-if="chapter.description" class="chapter-description">
            {{ chapter.description }}
          </p>

          <!-- Lessons list -->
          <div class="lessons-list">
            <RouterLink
              v-for="lesson in chapter.lessons"
              :key="lesson.id"
              :to="`/lessons/${lesson.id}`"
              class="lesson-item"
              :class="{
                locked: !lesson.is_unlocked,
                completed: lesson.progress_status === 'completed',
                in_progress: lesson.progress_status === 'in_progress',
              }"
            >
              <!-- Lesson icon & type -->
              <span class="lesson-icon">{{ lessonIcon(lesson.lesson_type) }}</span>

              <!-- Lesson info -->
              <div class="lesson-info">
                <span class="lesson-title">{{ lesson.title }}</span>
                <span class="lesson-time">~{{ lesson.estimated_minutes }} phút</span>
              </div>

              <!-- Lesson status -->
              <div class="lesson-status">
                <span v-if="!lesson.is_unlocked" class="status-locked">🔒</span>
                <span v-else-if="lesson.progress_status === 'completed'" class="status-completed">✓</span>
                <span v-else-if="lesson.progress_status === 'in_progress'" class="status-in-progress">⏳</span>
              </div>
            </RouterLink>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { curriculumApi } from '@/api/curriculum'

const route = useRoute()
const course = ref(null)
const loading = ref(true)
const error = ref(null)
const isEnrolled = ref(false)
const enrolling = ref(false)

const lessonIcon = (type) => {
  const icons = {
    listening: '🎧',
    speaking: '🎤',
    reading: '📖',
    writing: '✏️',
    grammar: '📝',
    vocabulary: '📚',
    pronunciation: '🗣️',
    assessment: '📋',
  }
  return icons[type] || '📄'
}

const levelBadgeStyle = (code) => {
  const colorMap = {
    A1: { bg: '#EFF6FF', color: '#0369A1' },
    A2: { bg: '#F0FDF4', color: '#15803D' },
    B1: { bg: '#FFFBEB', color: '#B45309' },
    B2: { bg: '#FEF3C7', color: '#D97706' },
    C1: { bg: '#FEE2E2', color: '#DC2626' },
  }
  const style = colorMap[code] || { bg: '#F3F4F6', color: '#374151' }
  return { backgroundColor: style.bg, color: style.color }
}

const enrollCourse = async () => {
  enrolling.value = true
  try {
    await curriculumApi.enroll(route.params.id)
    isEnrolled.value = true
  } catch (err) {
    error.value = 'Lỗi đăng ký: ' + err.message
  } finally {
    enrolling.value = false
  }
}

onMounted(async () => {
  try {
    const res = await curriculumApi.getCourse(route.params.id)
    course.value = res.data
    // Check if enrolled
    // isEnrolled.value = check from progress app
  } catch (err) {
    error.value = 'Không thể tải khóa học'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* [Similar styling as CoursesView but adapted for detail layout] */
.course-detail-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  padding: 2rem;
  background-color: var(--color-surface-02);
  border-radius: 1rem;
  border: 1px solid var(--color-surface-04);
  margin-bottom: 2rem;
}

/* ... rest of styling ... */
</style>
```

---

### 2.3 LessonDetailView.vue

**Mục đích:** Hiển thị bài học chi tiết với tất cả nội dung (reading, grammar, listening, v.v.).

```vue
<template>
  <div class="lesson-detail-container">
    <!-- Back button -->
    <button @click="$router.back()" class="btn-back">← Quay lại</button>

    <!-- Loading -->
    <div v-if="loading" class="loading-skeletons"></div>

    <!-- Error -->
    <div v-else-if="error" class="error-box">
      <p>⚠️ {{ error }}</p>
    </div>

    <!-- Lesson content -->
    <template v-else-if="lesson && content">
      <!-- Lesson header -->
      <section class="lesson-header">
        <div class="header-left">
          <span class="lesson-icon">{{ lessonIcon(lesson.lesson_type) }}</span>
          <span class="lesson-type-badge">{{ typeLabel(lesson.lesson_type) }}</span>
          <span class="lesson-time">~{{ lesson.estimated_minutes }} phút</span>
        </div>
        <div class="header-right">
          <span class="status-badge" :class="progress.status">
            {{ statusLabel(progress.status) }}
          </span>
        </div>
      </section>

      <h1 class="lesson-title">{{ lesson.title }}</h1>

      <!-- Locked gate -->
      <div v-if="progress.status === 'locked'" class="locked-gate">
        <p class="locked-icon">🔒</p>
        <p class="locked-text">Bài học chưa được mở</p>
        <p class="locked-hint">Hoàn thành các bài học trước để mở khoá bài này</p>
      </div>

      <!-- Unlocked content -->
      <template v-else-if="content">
        <!-- XP info -->
        <div class="xp-info">
          <span class="xp-base">⚡ {{ content.completion_xp }} XP</span>
          <span v-if="content.bonus_xp" class="xp-bonus">🌟 +{{ content.bonus_xp }} nếu 100%</span>
        </div>

        <!-- Reading section -->
        <ReadingSection
          v-if="content.reading_passage"
          :passage="content.reading_passage"
          :image-url="content.reading_image_url"
          :questions="content.reading_questions || []"
          :vocab-items="content.vocab_items || []"
          @progress="onSectionProgress('reading', $event)"
        />

        <!-- Grammar sections -->
        <template v-for="(section, idx) in (content.grammar_sections || [])" :key="'grammar-' + idx">
          <GrammarSection
            :section="section"
            @progress="onSectionProgress('grammar', $event)"
          />
        </template>

        <!-- Listening section -->
        <ListeningSection
          v-if="content.listening_content?.audio_text"
          :content="content.listening_content"
          @progress="onSectionProgress('listening', $event)"
        />

        <!-- Speaking section -->
        <SpeakingSection
          v-if="content.speaking_content?.sentences"
          :content="content.speaking_content"
          @progress="onSectionProgress('speaking', $event)"
        />

        <!-- Writing section -->
        <WritingSection
          v-if="content.writing_content?.exercises"
          :content="content.writing_content"
          @progress="onSectionProgress('writing', $event)"
        />

        <!-- Complete button -->
        <button @click="completeLesson" :disabled="completing" class="btn-complete">
          {{ completing ? '⏳ Đang lưu...' : '✓ Hoàn thành bài học' }}
        </button>
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { curriculumApi } from '@/api/curriculum'
import ReadingSection from '@/components/lesson/ReadingSection.vue'
import GrammarSection from '@/components/lesson/GrammarSection.vue'
import ListeningSection from '@/components/lesson/ListeningSection.vue'
import SpeakingSection from '@/components/lesson/SpeakingSection.vue'
import WritingSection from '@/components/lesson/WritingSection.vue'

const route = useRoute()
const router = useRouter()
const lesson = ref(null)
const content = ref(null)
const progress = reactive({ status: 'locked' })
const loading = ref(true)
const error = ref(null)
const completing = ref(false)
const sectionScores = ref({})

const lessonIcon = (type) => {
  const icons = {
    listening: '🎧',
    speaking: '🎤',
    reading: '📖',
    writing: '✏️',
    grammar: '📝',
    vocabulary: '📚',
    pronunciation: '🗣️',
    assessment: '📋',
  }
  return icons[type] || '📄'
}

const typeLabel = (type) => {
  const labels = {
    listening: 'Nghe',
    speaking: 'Nói',
    reading: 'Đọc',
    writing: 'Viết',
    grammar: 'Ngữ pháp',
    vocabulary: 'Từ vựng',
    pronunciation: 'Phát âm',
    assessment: 'Kiểm tra',
  }
  return labels[type] || type
}

const statusLabel = (status) => {
  const labels = {
    locked: '🔒 Chưa mở',
    in_progress: '⏳ Đang học',
    completed: '✅ Hoàn thành',
  }
  return labels[status] || status
}

const onSectionProgress = (section, { score }) => {
  sectionScores.value[section] = score
}

const completeLesson = async () => {
  completing.value = true
  try {
    // Calculate average score
    const scores = Object.values(sectionScores.value)
    const avgScore = scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b) / scores.length) : 0

    const res = await curriculumApi.markLessonComplete(route.params.id, {
      score: avgScore,
    })

    Object.assign(progress, res.data)

    // Show success message
    showNotification('✓ Hoàn thành bài học!')

    // Redirect or show completion modal
    setTimeout(() => router.push('/lessons'), 1500)
  } catch (err) {
    error.value = 'Lỗi lưu: ' + err.message
  } finally {
    completing.value = false
  }
}

onMounted(async () => {
  try {
    const [lessonRes, contentRes, progressRes] = await Promise.all([
      curriculumApi.getLesson(route.params.id),
      curriculumApi.getLessonContent(route.params.id),
      curriculumApi.getLessonProgress(route.params.id),
    ])

    lesson.value = lessonRes.data
    content.value = contentRes.data
    Object.assign(progress, progressRes.data)
  } catch (err) {
    error.value = 'Không thể tải bài học'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* [Lesson detail specific styling] */
.lesson-detail-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

.btn-back {
  margin-bottom: 1rem;
  padding: 0.5rem 1rem;
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 0.875rem;
  transition: color 0.2s;
}

.btn-back:hover {
  color: var(--color-text-base);
}

.lesson-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 1rem;
  background-color: var(--color-surface-02);
  border-radius: 0.5rem;
}

.lesson-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--color-text-base);
  margin-bottom: 1.5rem;
}

.xp-info {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.xp-base {
  padding: 0.5rem 1rem;
  background-color: rgba(251, 146, 60, 0.1);
  color: #fb923c;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.xp-bonus {
  padding: 0.5rem 1rem;
  background-color: rgba(250, 204, 21, 0.1);
  color: #fbbf24;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.locked-gate {
  text-align: center;
  padding: 4rem 2rem;
  background-color: var(--color-surface-02);
  border-radius: 1rem;
  border: 1px dashed var(--color-surface-04);
}

.locked-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.locked-text {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text-base);
  margin-bottom: 0.5rem;
}

.locked-hint {
  color: var(--color-text-muted);
  margin-bottom: 1.5rem;
}

.btn-complete {
  display: block;
  margin: 2rem auto;
  padding: 0.875rem 2rem;
  background-color: var(--color-primary-600);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-complete:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-complete:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
```

---

## 3. COMPONENTS

### 3.1 ReadingSection.vue

```vue
<template>
  <section class="reading-section">
    <!-- Reading passage with vocabulary highlights -->
    <article class="reading-content">
      <img v-if="imageUrl" :src="imageUrl" class="reading-image" alt="Reading illustration">
      <div class="passage" v-html="highlightVocab(passage)"></div>
    </article>

    <!-- Vocabulary footnotes -->
    <aside v-if="vocabItems?.length" class="vocab-footnotes">
      <div v-for="vocab in vocabItems" :key="vocab.word" class="vocab-item">
        <VocabFootnote :vocab="vocab" :word="vocab.word" />
      </div>
    </aside>

    <!-- Comprehension questions -->
    <div v-if="questions?.length" class="reading-questions">
      <h3>📋 Câu hỏi đọc hiểu</h3>
      <div v-for="(q, idx) in questions" :key="idx" class="question-item">
        <p class="question-text">{{ idx + 1 }}. {{ q.question }}</p>
        <div class="options">
          <label v-for="(opt, oi) in q.options" :key="oi" class="option">
            <input
              type="radio"
              :name="`reading-q${idx}`"
              :value="oi"
              v-model.number="answers[idx]"
            >
            <span>{{ opt }}</span>
          </label>
        </div>
      </div>

      <button @click="submitAnswers" class="btn-submit">Kiểm tra câu trả lời</button>

      <!-- Show results -->
      <div v-if="showResults" class="results">
        <p class="score">Điểm: {{ Math.round(score) }}%</p>
        <div v-for="(q, idx) in questions" :key="'result-' + idx" class="result-item">
          <p class="question">{{ q.question }}</p>
          <p :class="{ correct: answers[idx] === q.correct, incorrect: answers[idx] !== q.correct }">
            Câu trả lời của bạn: {{ q.options[answers[idx]] }}
            <span v-if="answers[idx] !== q.correct"> (Sai)</span>
          </p>
          <p class="correct-answer">Câu trả lời đúng: {{ q.options[q.correct] }}</p>
          <p class="explanation">{{ q.explanation }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import VocabFootnote from './VocabFootnote.vue'

const props = defineProps({
  passage: String,
  imageUrl: String,
  questions: Array,
  vocabItems: Array,
})

const emit = defineEmits(['progress'])

const answers = ref({})
const showResults = ref(false)
const score = ref(0)

const highlightVocab = (text) => {
  let highlighted = text
  props.vocabItems?.forEach(vocab => {
    if (vocab.highlight_in_passage) {
      const regex = new RegExp(`\\b${vocab.word}\\b`, 'gi')
      highlighted = highlighted.replace(
        regex,
        `<mark class="vocab-highlight" data-word="${vocab.word}">${vocab.word}</mark>`
      )
    }
  })
  return highlighted
}

const submitAnswers = () => {
  let correct = 0
  props.questions.forEach((q, idx) => {
    if (answers.value[idx] === q.correct) correct++
  })

  score.value = (correct / props.questions.length) * 100
  showResults.value = true

  emit('progress', { score: score.value })
}
</script>

<style scoped>
.reading-section {
  margin-bottom: 2rem;
  padding: 2rem;
  background-color: var(--color-surface-02);
  border-radius: 1rem;
  border: 1px solid var(--color-surface-04);
}

.reading-content {
  margin-bottom: 2rem;
}

.reading-image {
  width: 100%;
  max-height: 300px;
  object-fit: cover;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.passage {
  font-size: 1.0625rem;
  line-height: 1.75;
  color: var(--color-text-base);
  text-align: justify;
}

.passage :deep(.vocab-highlight) {
  background-color: rgba(251, 146, 60, 0.2);
  border-bottom: 2px solid #fb923c;
  cursor: help;
  padding: 0.125rem 0;
}

.vocab-footnotes {
  margin-bottom: 2rem;
  padding: 1rem;
  background-color: rgba(99, 102, 241, 0.05);
  border-left: 3px solid #6366F1;
  border-radius: 0.25rem;
}

.vocab-item {
  margin-bottom: 0.75rem;
}

.vocab-item:last-child {
  margin-bottom: 0;
}

.reading-questions {
  margin-top: 2rem;
}

.reading-questions h3 {
  margin-bottom: 1rem;
  font-size: 1rem;
  color: var(--color-text-base);
}

.question-item {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: var(--color-surface-03);
  border-radius: 0.5rem;
}

.question-text {
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--color-text-base);
}

.options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s;
}

.option:hover {
  background-color: rgba(99, 102, 241, 0.1);
}

.option input[type="radio"] {
  cursor: pointer;
}

.btn-submit {
  display: block;
  margin: 1rem 0;
  padding: 0.75rem 1.5rem;
  background-color: var(--color-primary-600);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-submit:hover {
  opacity: 0.9;
}

.results {
  margin-top: 1.5rem;
  padding: 1rem;
  background-color: rgba(34, 197, 94, 0.1);
  border-radius: 0.5rem;
  border-left: 3px solid #22C55E;
}

.score {
  font-size: 1.125rem;
  font-weight: 700;
  color: #22C55E;
  margin-bottom: 1rem;
}

.result-item {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background-color: var(--color-surface-03);
  border-radius: 0.25rem;
}

.correct {
  color: #22C55E;
  font-weight: 600;
}

.incorrect {
  color: #EF4444;
  font-weight: 600;
}

.correct-answer {
  color: #22C55E;
  font-size: 0.875rem;
}

.explanation {
  color: var(--color-text-muted);
  font-size: 0.875rem;
  font-style: italic;
  margin-top: 0.5rem;
}
</style>
```

---

## 4. API INTEGRATION

### API Module (`curriculum.js`)

```javascript
import api from './client.js'

export const curriculumApi = {
  // ── CEFR Levels ──────────────────────────
  getCefrLevels: () =>
    api.get('/curriculum/cefr-levels/'),

  // ── Courses ──────────────────────────────
  getCourses: (params = {}) =>
    api.get('/curriculum/courses/', { params }),

  getCourse: (id) =>
    api.get(`/curriculum/courses/${id}/`),

  // ── Chapters ─────────────────────────────
  getChapters: (courseId) =>
    api.get(`/curriculum/courses/${courseId}/chapters/`),

  // ── Lessons ──────────────────────────────
  getLessons: (courseId, chapterId) =>
    api.get(`/curriculum/courses/${courseId}/chapters/${chapterId}/lessons/`),

  getLesson: (id) =>
    api.get(`/curriculum/lessons/${id}/`),

  getLessonContent: (id) =>
    api.get(`/curriculum/lessons/${id}/content/`),

  // ── Progress ─────────────────────────────
  enroll: (courseId) =>
    api.post('/progress/enroll/', { course_id: courseId }),

  markLessonComplete: (lessonId, data = {}) =>
    api.post(`/progress/lessons/${lessonId}/complete/`, data),

  getLessonProgress: (lessonId) =>
    api.get(`/progress/lessons/${lessonId}/`),
}

export const exercisesApi = {
  getListening: (id) => api.get(`/exercises/listening/${id}/`),
  getSpeaking: (id) => api.get(`/exercises/speaking/${id}/`),
  getReading: (id) => api.get(`/exercises/reading/${id}/`),
  getWriting: (id) => api.get(`/exercises/writing/${id}/`),
}

export const grammarApi = {
  getTopic: (slug) => api.get(`/grammar/${slug}/`),
  getProgress: () => api.get('/grammar/progress/'),
}

export const vocabularyApi = {
  getWord: (id) => api.get(`/vocabulary/words/${id}/`),
  addToFlashcard: (wordId) =>
    api.post('/vocabulary/flashcards/add-word/', { word_id: wordId }),
}

export function getExercise(type, id) {
  switch (type) {
    case 'listening': return exercisesApi.getListening(id)
    case 'speaking': return exercisesApi.getSpeaking(id)
    case 'reading': return exercisesApi.getReading(id)
    case 'writing': return exercisesApi.getWriting(id)
    default: throw new Error(`Unknown exercise type: ${type}`)
  }
}
```

---

## 5. STATE MANAGEMENT

### Optional Pinia Store

```javascript
// stores/curriculum.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { curriculumApi } from '@/api/curriculum'

export const useCurriculumStore = defineStore('curriculum', () => {
  const courses = ref([])
  const currentCourse = ref(null)
  const currentLesson = ref(null)
  const cefrLevels = ref([])
  const loading = ref(false)

  const getCourses = computed(() => courses.value)

  const fetchCourses = async (params = {}) => {
    loading.value = true
    try {
      const res = await curriculumApi.getCourses(params)
      courses.value = res.data
    } finally {
      loading.value = false
    }
  }

  const fetchCourse = async (id) => {
    loading.value = true
    try {
      const res = await curriculumApi.getCourse(id)
      currentCourse.value = res.data
    } finally {
      loading.value = false
    }
  }

  const fetchLesson = async (id) => {
    loading.value = true
    try {
      const res = await curriculumApi.getLesson(id)
      currentLesson.value = res.data
    } finally {
      loading.value = false
    }
  }

  return {
    courses,
    currentCourse,
    currentLesson,
    cefrLevels,
    loading,
    getCourses,
    fetchCourses,
    fetchCourse,
    fetchLesson,
  }
})
```

---

## 6. ROUTING

### Route Definitions

```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/courses',
    name: 'Courses',
    component: () => import('@/views/CoursesView.vue'),
    meta: { title: 'Khoá học' }
  },
  {
    path: '/courses/:id',
    name: 'CourseDetail',
    component: () => import('@/views/CourseDetailView.vue'),
    meta: { title: 'Chi tiết khoá học' }
  },
  {
    path: '/lessons/:id',
    name: 'LessonDetail',
    component: () => import('@/views/LessonDetailView.vue'),
    meta: { title: 'Bài học', requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
```

---

## 7. STYLING

### CSS Variables (Theming)

```css
:root {
  /* Colors */
  --color-primary-600: #4f46e5;
  --color-text-base: #1f2937;
  --color-text-soft: #6b7280;
  --color-text-muted: #9ca3af;
  --color-surface-02: #f9fafb;
  --color-surface-03: #f3f4f6;
  --color-surface-04: #e5e7eb;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Typography */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'Menlo', 'Monaco', 'Courier New', monospace;

  /* Transitions */
  --transition-fast: 0.15s;
  --transition-base: 0.2s;
  --transition-slow: 0.3s;
}

/* Light mode (default) */
body {
  font-family: var(--font-sans);
  background-color: white;
  color: var(--color-text-base);
}

/* Dark mode (optional) */
@media (prefers-color-scheme: dark) {
  :root {
    --color-text-base: #f3f4f6;
    --color-surface-02: #1f2937;
    --color-surface-03: #111827;
    --color-surface-04: #374151;
  }

  body {
    background-color: #0f172a;
  }
}
```

---

## 📝 Tóm tắt

| Layer | Tập tin | Mục đích |
|---|---|---|
| **View** | `CoursesView.vue` | List courses |
| **View** | `CourseDetailView.vue` | Course + chapters + lessons |
| **View** | `LessonDetailView.vue` | Full lesson content |
| **Component** | `ReadingSection.vue` | Reading + vocab + Q&A |
| **Component** | `GrammarSection.vue` | Grammar explanation + exercises |
| **Component** | `ListeningSection.vue` | Audio + dictation |
| **Component** | `SpeakingSection.vue` | Repeat/Shadow/Dialogue |
| **Component** | `WritingSection.vue` | Gap-fill/sentence completion |
| **API** | `curriculum.js` | API calls to backend |
| **Router** | `router/index.js` | Route definitions |
| **Store** | `curriculum.js` | Optional state mgmt |

---

**Kiến trúc này là modular, scalable, và dễ mở rộng với các features mới!**
