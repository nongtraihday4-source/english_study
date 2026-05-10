<template>
  <div class="max-w-6xl mx-auto p-4 sm:p-6 pb-24">

    <!-- Back -->
    <button @click="$router.back()"
            class="flex items-center gap-1 text-sm mb-5 transition hover:opacity-70"
            style="color: var(--color-text-muted)">
      ← Quay lại
    </button>

    <!-- ─── Skeleton ─────────────────────────────────────────────────── -->
    <div v-if="loading" class="space-y-4">
      <div class="h-32 rounded-2xl animate-pulse" style="background-color:var(--color-surface-02)"></div>
      <div class="h-48 rounded-2xl animate-pulse" style="background-color:var(--color-surface-02)"></div>
      <div class="h-64 rounded-2xl animate-pulse" style="background-color:var(--color-surface-02)"></div>
    </div>

    <!-- ─── Error ─────────────────────────────────────────────────────── -->
    <div v-else-if="error" class="text-center py-16" style="color:var(--color-text-muted)">
      <p class="text-4xl mb-3">⚠️</p>
      <p>{{ error }}</p>
    </div>

    <template v-else-if="lesson">

      <!-- ── Lesson Header ──────────────────────────────────────────── -->
      <div class="rounded-2xl p-5 mb-6"
           style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
        <div class="flex items-center gap-2 mb-2 flex-wrap">
          <span class="text-2xl">{{ lessonIcon(lesson.lesson_type) }}</span>
          <span class="px-2 py-0.5 text-xs rounded font-semibold" :style="typeColor(lesson.lesson_type)">
            {{ typeLabel(lesson.lesson_type) }}
          </span>
          <span class="text-xs" style="color:var(--color-text-muted)">~{{ lesson.estimated_minutes }} phút</span>
          <span class="ml-auto inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full"
                :style="statusStyle(progress.status)">
            {{ statusLabel(progress.status) }}
          </span>
        </div>
        <h1 class="text-lg font-bold" style="color:var(--color-text-base)">{{ lesson.title }}</h1>

        <!-- 🎯 Learning Objectives -->
        <div v-if="content?.learning_objectives?.length" class="mt-3 mb-1 px-3 py-2 rounded-xl"
             style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2)">
          <p class="text-xs font-semibold mb-1.5" style="color:#818cf8">🎯 Mục tiêu bài học</p>
          <ul class="list-disc list-inside space-y-0.5 text-xs" style="color:var(--color-text-base)">
            <li v-for="(obj, i) in content.learning_objectives" :key="i">{{ obj }}</li>
          </ul>
        </div>

        <p v-if="content?.chapter_title || lesson.chapter_title" class="text-xs mt-1" style="color:var(--color-text-muted)">
          📂 {{ content?.chapter_title || lesson.chapter_title }}
        </p>
        <div v-if="content" class="flex items-center gap-3 mt-3">
          <span class="text-xs px-2 py-0.5 rounded-full" style="background:rgba(251,146,60,0.15);color:#fb923c">
            ⚡ {{ content.completion_xp }} XP hoàn thành
          </span>
          <span class="text-xs px-2 py-0.5 rounded-full" style="background:rgba(250,204,21,0.15);color:#fbbf24">
            🌟 +{{ content.bonus_xp }} XP nếu 100%
          </span>
        </div>
      </div>

      <!-- ── Locked Gate ──────────────────────────────────────────── -->
      <div v-if="progress.status === 'locked'"
           class="rounded-2xl p-8 text-center"
           style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
        <p class="text-4xl mb-3">🔒</p>
        <p class="font-semibold mb-1" style="color:var(--color-text-base)">Bài học chưa được mở</p>
        <p class="text-sm" style="color:var(--color-text-muted)">Hoàn thành bài học trước để mở khoá bài này.</p>
      </div>

      <template v-else-if="content">

        <!-- ═══════════════════════════════════════════════════════════ -->
        <!-- SECTION 1: READING (60/40 — passage + MCQs)               -->
        <!-- ═══════════════════════════════════════════════════════════ -->
        <ReadingSection
          v-if="content.reading_passage"
          :passage="content.reading_passage"
          :questions="content.reading_questions || []"
          :vocab-items="content.vocab_items || []"
          @progress="onReadingProgress"
        />

        <!-- Section divider -->
        <div v-if="content.reading_passage && content.grammar_sections?.length"
             class="border-t my-8" style="border-color:var(--color-surface-04)"></div>

        <!-- ═══════════════════════════════════════════════════════════ -->
        <!-- SECTION 2: GRAMMAR SECTIONS (full 60/40 or tip card)      -->
        <!-- ═══════════════════════════════════════════════════════════ -->
        <template v-for="(gs, gi) in (content.grammar_sections || [])" :key="'gs-' + gi">
          <GrammarSection
            :section="gs"
            :mode="grammarMode"
            :section-index="gi"
            @progress="onGrammarProgress(gi, $event)"
          />
          <div v-if="gi < (content.grammar_sections.length - 1)"
               class="border-t my-6" style="border-color:var(--color-surface-04)"></div>
        </template>

        <!-- ═══════════════════════════════════════════════════════════ -->
        <!-- SECTION 3: LISTENING                                       -->
        <!-- ═══════════════════════════════════════════════════════════ -->
        <template v-if="content.listening_content?.audio_text">
          <div class="border-t my-8" style="border-color:var(--color-surface-04)"></div>
          <ListeningSection
            :content="content.listening_content"
            @progress="onListeningProgress"
          />
        </template>

        <!-- ═══════════════════════════════════════════════════════════ -->
        <!-- SECTION 4: SPEAKING                                        -->
        <!-- ═══════════════════════════════════════════════════════════ -->
        <template v-if="content.speaking_content?.sentences?.length">
          <div class="border-t my-8" style="border-color:var(--color-surface-04)"></div>
          <SpeakingSection
            :content="content.speaking_content"
            @progress="onSpeakingProgress"
          />
        </template>

        <!-- ═══════════════════════════════════════════════════════════ -->
        <!-- SECTION 5: WRITING                                         -->
        <!-- ═══════════════════════════════════════════════════════════ -->
        <template v-if="content.writing_content?.exercises?.length">
          <div class="border-t my-8" style="border-color:var(--color-surface-04)"></div>
          <WritingSection
            :content="content.writing_content"
            @progress="onWritingProgress"
          />
        </template>

        <!-- Section divider before completion -->
        <div class="border-t my-8" style="border-color:var(--color-surface-04)"></div>

        <!-- ═══════════════════════════════════════════════════════════ -->
        <!-- COMPLETION CARD                                            -->
        <!-- ═══════════════════════════════════════════════════════════ -->
        <div class="rounded-2xl p-5"
             style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
          <div v-if="showCourseCompletionCard"
               class="text-center py-2 space-y-4 rounded-2xl overflow-hidden relative"
               style="background:radial-gradient(circle at top, rgba(251,191,36,0.18), transparent 46%), linear-gradient(135deg, rgba(99,102,241,0.12), rgba(34,197,94,0.1))">
            <div class="absolute inset-0 course-complete-sheen"></div>
            <div class="relative">
              <p class="text-5xl mb-2">🏅</p>
              <p class="text-xs font-semibold uppercase tracking-[0.22em] mb-2" style="color:#fbbf24">Course Completed</p>
              <h3 class="text-xl font-bold" style="color:var(--color-text-base)">Bạn đã hoàn thành khóa học này!</h3>
              <p class="text-sm mt-2 max-w-xl mx-auto" style="color:var(--color-text-muted)">
                Toàn bộ lộ trình của khóa học hiện tại đã được đánh dấu hoàn thành.
              </p>
            </div>
            <div class="relative grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
              <div class="rounded-xl px-4 py-3" style="background-color:var(--color-surface-03);border:1px solid var(--color-surface-04)">
                <p class="text-xs mb-1" style="color:var(--color-text-muted)">Điểm bài cuối</p>
                <p class="text-lg font-bold" style="color:var(--color-text-base)">{{ displayScore }}/100</p>
              </div>
              <div class="rounded-xl px-4 py-3" style="background-color:var(--color-surface-03);border:1px solid var(--color-surface-04)">
                <p class="text-xs mb-1" style="color:var(--color-text-muted)">XP nhận được</p>
                <p class="text-lg font-bold" style="color:var(--color-text-base)">+{{ completionXp }}</p>
              </div>
              <div class="rounded-xl px-4 py-3" style="background-color:var(--color-surface-03);border:1px solid var(--color-surface-04)">
                <p class="text-xs mb-1" style="color:var(--color-text-muted)">Kết quả bài tập</p>
                <p class="text-lg font-bold" style="color:var(--color-text-base)">{{ exerciseCorrect }}/{{ totalExercises || 0 }}</p>
              </div>
            </div>
            <div class="relative flex flex-col sm:flex-row items-center justify-center gap-3 pt-1">
              <button @click="goBackToCourse"
                      class="w-full sm:w-auto px-5 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-90"
                      style="background-color:var(--color-primary-500);color:#fff">
                Về tổng quan khóa học
              </button>
              <button @click="goToCourses"
                      class="w-full sm:w-auto px-5 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-90"
                      style="background-color:var(--color-surface-03);color:var(--color-text-base);border:1px solid var(--color-surface-04)">
                Xem các khóa học khác
              </button>
            </div>
          </div>
          <div v-else-if="progress.status === 'completed'" class="text-center py-2 space-y-3">
            <div>
              <p class="text-4xl mb-2">{{ completionEmoji }}</p>
              <p class="font-semibold text-base" :style="`color:${completionAccent}`">{{ completionHeadline }}</p>
              <p class="text-sm mt-1" style="color:var(--color-text-muted)">{{ completionSubtext }}</p>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
              <div class="rounded-xl px-4 py-3" style="background-color:var(--color-surface-03);border:1px solid var(--color-surface-04)">
                <p class="text-xs mb-1" style="color:var(--color-text-muted)">Điểm bài này</p>
                <p class="text-lg font-bold" style="color:var(--color-text-base)">{{ displayScore }}/100</p>
              </div>
              <div class="rounded-xl px-4 py-3" style="background-color:var(--color-surface-03);border:1px solid var(--color-surface-04)">
                <p class="text-xs mb-1" style="color:var(--color-text-muted)">Kết quả câu hỏi</p>
                <p class="text-lg font-bold" style="color:var(--color-text-base)">{{ exerciseCorrect }}/{{ totalExercises || 0 }}</p>
              </div>
              <div class="rounded-xl px-4 py-3" style="background-color:var(--color-surface-03);border:1px solid var(--color-surface-04)">
                <p class="text-xs mb-1" style="color:var(--color-text-muted)">XP nhận được</p>
                <p class="text-lg font-bold" style="color:var(--color-text-base)">+{{ completionXp }}</p>
              </div>
            </div>
            <div class="flex flex-col sm:flex-row items-center justify-center gap-3 pt-1">
              <button v-if="completionMeta.next_lesson_id"
                      @click="goNextLesson"
                      class="w-full sm:w-auto px-5 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-90"
                      style="background-color:var(--color-primary-500);color:#fff">
                Bài học kế tiếp →
              </button>
              <button @click="goBackToCourse"
                      class="w-full sm:w-auto px-5 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-90"
                      style="background-color:var(--color-surface-03);color:var(--color-text-base);border:1px solid var(--color-surface-04)">
                Về khóa học
              </button>
            </div>
          </div>
          <div v-else class="flex flex-col items-center gap-3 py-1">
            <div v-if="exerciseDone > 0" class="w-full max-w-xs">
              <div class="flex items-center justify-between text-sm mb-1">
                <span style="color:var(--color-text-muted)">Kết quả:</span>
                <span class="font-semibold" style="color:var(--color-text-base)">
                  {{ exerciseCorrect }}/{{ totalExercises }} đúng ({{ autoScore }}%)
                </span>
              </div>
              <div class="h-2 rounded-full overflow-hidden" style="background:var(--color-surface-04)">
                <div class="h-full rounded-full transition-all duration-500"
                     :style="`width:${autoScore}%;background:${autoScore >= 70 ? '#22c55e' : autoScore >= 40 ? '#f59e0b' : '#ef4444'}`">
                </div>
              </div>
            </div>

            <!-- Auto-completing state -->
            <template v-if="autoCompleting || completing">
              <div class="flex items-center gap-2 text-sm" style="color:var(--color-text-muted)">
                <span class="inline-block animate-spin">⏳</span>
                Đang tự động ghi nhận hoàn thành...
              </div>
            </template>

            <!-- Waiting for exercises -->
            <template v-else-if="!canComplete">
              <p class="text-sm text-center" style="color:var(--color-text-muted)">
                Hãy hoàn thành tất cả phần bài tập — hệ thống sẽ tự động ghi nhận kết quả.
              </p>
            </template>

            <!-- canComplete but no exercises done (e.g. content-only lesson) — keep manual button -->
            <template v-else>
              <p class="text-sm text-center" style="color:var(--color-text-muted)">
                Hệ thống sẽ tự chấm điểm và mở bài tiếp theo.
              </p>
              <button @click="complete" :disabled="completing"
                      class="w-full max-w-xs py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-90"
                      style="background-color:var(--color-primary-500);color:#fff">
                {{ completing ? 'Đang lưu...' : '✓ Đánh dấu hoàn thành' }}
              </button>
            </template>
          </div>
        </div>

      </template>

      <!-- No content yet but unlocked -->
      <div v-else-if="!contentLoading"
           class="rounded-2xl p-8 text-center"
           style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
        <p class="text-4xl mb-3">🚧</p>
        <p class="font-semibold mb-1" style="color:var(--color-text-base)">Nội dung đang được chuẩn bị</p>
        <p class="text-sm mb-4" style="color:var(--color-text-muted)">Bài học này sẽ sớm có nội dung đầy đủ.</p>
        <button v-if="progress.status !== 'completed'" @click="complete" :disabled="completing"
                class="px-6 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-90"
                style="background-color:var(--color-primary-500);color:#fff">
          {{ completing ? 'Đang lưu...' : '✓ Đánh dấu hoàn thành' }}
        </button>
        <p v-else class="font-semibold text-sm" style="color:#86efac">✅ Đã hoàn thành</p>
      </div>

    </template>

    <!-- ─── Toast ─────────────────────────────────────────────────── -->
    <Transition name="toast">
      <div v-if="toast.show"
           class="fixed bottom-6 left-1/2 -translate-x-1/2 px-5 py-2.5 rounded-full text-sm font-medium shadow-lg z-50 whitespace-nowrap"
           style="background-color:var(--color-primary-500);color:#fff">
        {{ toast.message }}
      </div>
    </Transition>

    <Transition name="perfect-toast">
      <div v-if="perfectToast.show"
           class="fixed top-24 left-1/2 -translate-x-1/2 z-50 w-[min(92vw,34rem)] rounded-3xl px-6 py-5 shadow-2xl overflow-hidden"
           style="background:linear-gradient(135deg, rgba(251,191,36,0.96), rgba(249,115,22,0.94)); color:#fff; border:1px solid rgba(255,255,255,0.25)">
        <div class="absolute inset-0 perfect-toast-glow"></div>
        <div class="relative flex items-start gap-4">
          <div class="text-4xl leading-none perfect-toast-icon">🏆</div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold uppercase tracking-[0.18em] opacity-80">Perfect Score</p>
            <h3 class="text-xl font-bold leading-tight mt-1">Điểm tuyệt đối 100%</h3>
            <p class="text-sm mt-2 text-white/90">Bạn đã làm đúng toàn bộ bài tập và nhận trọn bonus của bài học này.</p>
            <div class="flex flex-wrap gap-2 mt-3 text-xs font-semibold">
              <span class="px-3 py-1 rounded-full bg-white/20">⚡ +{{ perfectToast.xp }} XP</span>
              <span class="px-3 py-1 rounded-full bg-white/20">🎯 {{ exerciseCorrect }}/{{ totalExercises || 0 }} câu đúng</span>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="perfect-toast">
      <div v-if="chapterToast.show"
           class="fixed top-24 left-1/2 -translate-x-1/2 z-50 w-[min(92vw,32rem)] rounded-3xl px-6 py-5 shadow-2xl overflow-hidden"
           style="background:linear-gradient(135deg, rgba(79,70,229,0.96), rgba(124,58,237,0.94)); color:#fff; border:1px solid rgba(255,255,255,0.18)">
        <div class="absolute inset-0 perfect-toast-glow"></div>
        <div class="relative flex items-start gap-4">
          <div class="text-4xl leading-none perfect-toast-icon">🏆</div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold uppercase tracking-[0.18em] opacity-80">Chapter Completed</p>
            <h3 class="text-xl font-bold leading-tight mt-1">Bạn đã hoàn thành chương này!</h3>
            <p class="text-sm mt-2 text-white/90">{{ chapterToast.title }}</p>
            <div class="flex flex-wrap gap-2 mt-3 text-xs font-semibold">
              <span class="px-3 py-1 rounded-full bg-white/20">📊 Trung bình {{ chapterToast.avgScore }}</span>
              <span class="px-3 py-1 rounded-full bg-white/20">🚀 Mở tiếp chương sau</span>
            </div>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { curriculumApi } from '@/api/curriculum.js'
import { progressApi } from '@/api/progress.js'
import { writeCourseRefreshMarker } from '@/utils/courseProgressRefresh.js'
import { useLessonStore } from '@/stores/lesson.js'
import ReadingSection from '@/components/lesson/ReadingSection.vue'
import GrammarSection from '@/components/lesson/GrammarSection.vue'
import ListeningSection from '@/components/lesson/ListeningSection.vue'
import SpeakingSection from '@/components/lesson/SpeakingSection.vue'
import WritingSection from '@/components/lesson/WritingSection.vue'

const route = useRoute()
const router = useRouter()
const lessonStore = useLessonStore()

// ── State ─────────────────────────────────────────────────────────────────────
const lesson         = ref(null)
const content        = ref(null)
const loading        = ref(false)
const contentLoading = ref(false)
const error          = ref('')
const completing     = ref(false)
const autoCompleting = ref(false)

const progress = reactive({ status: 'locked', best_score: null, attempts_count: 0 })
const completionMeta = reactive({
  attempt_score: null,
  score: null,
  xp_gained: 0,
  next_lesson_id: null,
  next_lesson_title: '',
  course_id: null,
  chapter_id: null,
  course_completed: false,
})

// ── Section progress tracking ─────────────────────────────────────────────────
// Each child section emits { done, correct, total } — we accumulate here.
const readingProgress   = reactive({ done: 0, correct: 0, total: 0 })
const listeningProgress = reactive({ done: 0, correct: 0, total: 0 })
const speakingProgress  = reactive({ done: 0, total: 0 })
const writingProgress   = reactive({ done: 0, correct: 0, total: 0 })
const grammarProgressList = ref([])  // Array<{ done, correct, total }> — one per grammar section

// Initialise per-section totals as soon as content loads
watch(() => content.value, (c) => {
  if (!c) return
  readingProgress.done    = 0
  readingProgress.correct = 0
  readingProgress.total   = c.reading_questions?.length ?? 0

  listeningProgress.done    = 0
  listeningProgress.correct = 0
  listeningProgress.total   =
    (c.listening_content?.comprehension_questions?.length ?? 0) +
    (c.listening_content?.dictation_sentences?.length ?? 0)

  speakingProgress.done  = 0
  speakingProgress.total = c.speaking_content?.sentences?.length ?? 0

  writingProgress.done    = 0
  writingProgress.correct = 0
  writingProgress.total   = c.writing_content?.exercises?.length ?? 0

  grammarProgressList.value = (c.grammar_sections ?? []).map(gs => ({
    done:    0,
    correct: 0,
    total:   grammarMode.value === 'full' ? (gs.exercises?.length ?? 0) : 0,
  }))
}, { immediate: true })

function onReadingProgress({ done, correct, total }) {
  readingProgress.done    = done
  readingProgress.correct = correct
  readingProgress.total   = total
}

function onGrammarProgress(sectionIndex, { done, correct, total }) {
  if (!grammarProgressList.value[sectionIndex]) {
    grammarProgressList.value[sectionIndex] = { done: 0, correct: 0, total: 0 }
  }
  grammarProgressList.value[sectionIndex] = { done, correct, total }
}

function onListeningProgress({ done, correct, total }) {
  listeningProgress.done    = done
  listeningProgress.correct = correct
  listeningProgress.total   = total
}

function onSpeakingProgress({ done, total }) {
  speakingProgress.done  = done
  speakingProgress.total = total
}

function onWritingProgress({ done, correct, total }) {
  writingProgress.done    = done
  writingProgress.correct = correct
  writingProgress.total   = total
}

// ── Toast ─────────────────────────────────────────────────────────────────────
const toast = reactive({ show: false, message: '' })
const perfectToast = reactive({ show: false, xp: 0 })
const chapterToast = reactive({ show: false, title: '', avgScore: 0 })
let _toastTimer = null, _perfectToastTimer = null, _chapterToastTimer = null

function showToast(msg) {
  clearTimeout(_toastTimer)
  toast.message = msg; toast.show = true
  _toastTimer = setTimeout(() => { toast.show = false }, 3500)
}
function showPerfectToast(xp) {
  clearTimeout(_perfectToastTimer)
  perfectToast.xp = xp; perfectToast.show = true
  _perfectToastTimer = setTimeout(() => { perfectToast.show = false }, 4200)
}
function showChapterToast(title, avgScore) {
  clearTimeout(_chapterToastTimer)
  chapterToast.title = title || 'Chương hiện tại'; chapterToast.avgScore = avgScore ?? 0; chapterToast.show = true
  _chapterToastTimer = setTimeout(() => { chapterToast.show = false }, 4600)
}

// ── Load ─────────────────────────────────────────────────────────────────────
onMounted(async () => {
  loading.value = true
  try {
    const [lessonRes, progressRes] = await Promise.all([
      curriculumApi.getLesson(route.params.id),
      progressApi.getLessonProgress(route.params.id),
    ])
    const ld = lessonRes.data?.data ?? lessonRes.data
    const pd = progressRes.data?.data ?? progressRes.data
    lesson.value            = ld
    progress.status         = pd?.status ?? ld?.progress_status ?? 'locked'
    progress.best_score     = pd?.best_score ?? null
    progress.attempts_count = pd?.attempts_count ?? 0
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Không thể tải bài học.'
    loading.value = false
    return
  }

  if (progress.status !== 'locked') {
    contentLoading.value = true
    try {
      const contentRes = await curriculumApi.getLessonContent(route.params.id)
      content.value = contentRes.data?.data ?? contentRes.data
    } catch (_) { /* content optional */ }
    contentLoading.value = false
  }
  loading.value = false
})

// ── Mark complete ──────────────────────────────────────────────────────────────
async function complete() {
  completing.value = true
  try {
    const payload = lessonStore.getPayload()
    const res = await progressApi.markLessonComplete(route.params.id, payload)
    const data = res.data?.data ?? res.data
    progress.status = 'completed'
    if (data?.best_score !== undefined && data?.best_score !== null) progress.best_score = data.best_score
    progress.attempts_count = data?.attempts_count ?? progress.attempts_count
    completionMeta.attempt_score = data?.attempt_score ?? null
    completionMeta.score         = data?.score ?? data?.attempt_score ?? null
    completionMeta.xp_gained     = data?.xp_gained ?? 0
    completionMeta.next_lesson_id    = data?.next_lesson_id ?? null
    completionMeta.next_lesson_title = data?.next_lesson_title ?? ''
    completionMeta.course_id     = data?.course_id ?? lesson.value?.course_id ?? null
    completionMeta.chapter_id    = data?.chapter_id ?? lesson.value?.chapter_id ?? null
    completionMeta.course_completed = !!data?.course_completed
    writeCourseRefreshMarker({
      course_id:        data?.course_id ?? lesson.value?.course_id,
      chapter_id:       data?.chapter_id ?? lesson.value?.chapter_id,
      next_lesson_id:   data?.next_lesson_id,
      course_completed: data?.course_completed,
      chapter_completed: data?.chapter_completed,
      chapter_title:    data?.chapter_title,
      chapter_avg_score: data?.chapter_avg_score,
    })
    if ((data?.attempt_score ?? 0) >= 100 && totalExercises.value > 0)
      showPerfectToast(data?.xp_gained ?? completionXp.value)
    if (data?.chapter_completed && !data?.course_completed)
      showChapterToast(data?.chapter_title, data?.chapter_avg_score)
    showToast(data?.next_lesson_id ? '✓ Hoàn thành! Bài học kế tiếp đã được mở khóa.' : '✓ Hoàn thành bài học.')
  } catch (e) {
    showToast('⚠ ' + (e?.response?.data?.detail || 'Lỗi khi lưu tiến độ.'))
  } finally {
    completing.value = false
    autoCompleting.value = false
    lessonStore.reset()
  }
}

function goNextLesson() {
  if (completionMeta.next_lesson_id) {
    router.push({ name: 'lesson-detail', params: { id: completionMeta.next_lesson_id } })
    return
  }
  goBackToCourse()
}
function goBackToCourse() {
  const courseId = completionMeta.course_id || lesson.value?.course_id
  if (courseId) {
    router.push({
      name: 'course-detail', params: { id: courseId },
      query: { refresh: String(Date.now()), chapter: String(completionMeta.chapter_id || lesson.value?.chapter_id || '') },
    })
    return
  }
  router.push('/courses')
}
function goToCourses() { router.push('/courses') }

// ── Computed ──────────────────────────────────────────────────────────────────
const grammarMode = computed(() => {
  const t = content.value?.lesson_type
  return ['reading', 'listening', 'speaking', 'writing', 'pronunciation'].includes(t) ? 'tip' : 'full'
})

const totalExercises = computed(() =>
  grammarProgressList.value.reduce((a, gp) => a + gp.total, 0) +
  readingProgress.total + listeningProgress.total +
  speakingProgress.total + writingProgress.total
)
const exerciseDone = computed(() =>
  grammarProgressList.value.reduce((a, gp) => a + gp.done, 0) +
  readingProgress.done + listeningProgress.done +
  speakingProgress.done + writingProgress.done
)
const exerciseCorrect = computed(() =>
  grammarProgressList.value.reduce((a, gp) => a + gp.correct, 0) +
  readingProgress.correct + listeningProgress.correct +
  speakingProgress.done + writingProgress.correct
)

const autoScore = computed(() =>
  totalExercises.value === 0 ? 0 : Math.round((exerciseCorrect.value / totalExercises.value) * 100)
)

const canComplete = computed(() => {
  return totalExercises.value === 0 || exerciseDone.value >= totalExercises.value
})

// ── Auto-complete when all exercises are done ──────────────────────────────────
watch(canComplete, (newVal, oldVal) => {
  if (
    newVal && !oldVal &&
    !completing.value &&
    exerciseDone.value > 0
  ) {
    // Allow re-scoring if already completed (so best_score can improve)
    autoCompleting.value = true
    setTimeout(() => {
      if (canComplete.value && !completing.value) {
        complete()
      } else {
        autoCompleting.value = false
      }
    }, 1200)
  }
})

const displayScore  = computed(() => {
  // Prefer the score from the current session's attempt if it's higher
  const sessionScore = completionMeta.attempt_score ?? completionMeta.score ?? null
  const storedScore  = progress.best_score ?? 0
  const liveScore    = exerciseDone.value > 0 ? autoScore.value : 0
  if (sessionScore !== null) return Math.max(sessionScore, liveScore)
  return Math.max(storedScore, liveScore)
})
const completionXp  = computed(() => completionMeta.xp_gained || (content.value ? content.value.completion_xp + (displayScore.value >= 100 ? (content.value.bonus_xp || 0) : 0) : 0))
const isPerfectScore = computed(() => displayScore.value >= 100 && (totalExercises.value === 0 || exerciseCorrect.value >= totalExercises.value))
const completionEmoji   = computed(() => isPerfectScore.value ? '🎉' : displayScore.value >= 70 ? '✅' : '📘')
const completionAccent  = computed(() => isPerfectScore.value ? '#fbbf24' : displayScore.value >= 70 ? '#86efac' : '#818cf8')
const completionHeadline = computed(() => {
  if (isPerfectScore.value) return 'Chúc mừng bạn đã hoàn thành bài học với điểm tuyệt đối!'
  if (displayScore.value >= 70) return 'Bạn đã hoàn thành bài học.'
  return 'Bài học đã được ghi nhận hoàn thành.'
})
const completionSubtext = computed(() => {
  if (completionMeta.next_lesson_title) return `Bài tiếp theo: ${completionMeta.next_lesson_title}`
  if (completionMeta.course_completed) return 'Bạn đã đi đến cuối khóa học hiện tại.'
  return 'Bạn có thể quay lại khóa học để tiếp tục lộ trình.'
})
const showCourseCompletionCard = computed(() => progress.status === 'completed' && completionMeta.course_completed)

// ── Cosmetic helpers ───────────────────────────────────────────────────────────
function lessonIcon(type) {
  return { vocabulary:'📝', grammar:'📐', reading:'📖', assessment:'🧩',
           listening:'🎧', speaking:'🎤', writing:'✍️' }[type] || '📚'
}
function typeLabel(type) {
  return { vocabulary:'Từ vựng', grammar:'Ngữ pháp', reading:'Đọc hiểu', assessment:'Kiểm tra',
           listening:'Nghe', speaking:'Nói', writing:'Viết' }[type] || type
}
function typeColor(type) {
  return { grammar:    'background:rgba(99,102,241,0.15);color:#818cf8',
           vocabulary: 'background:rgba(34,197,94,0.15);color:#86efac',
           reading:    'background:rgba(6,182,212,0.15);color:#22d3ee',
           assessment: 'background:rgba(249,115,22,0.15);color:#fb923c',
           listening:  'background:rgba(168,85,247,0.15);color:#c084fc',
           speaking:   'background:rgba(244,63,94,0.15);color:#fb7185',
           writing:    'background:rgba(234,179,8,0.15);color:#facc15',
         }[type] || 'background:var(--color-surface-04);color:var(--color-text-muted)'
}
function statusStyle(s) {
  if (s === 'completed') return 'background:rgba(34,197,94,0.15);color:#86efac'
  if (s === 'available') return 'background:rgba(99,102,241,0.15);color:#818cf8'
  return 'background:var(--color-surface-04);color:var(--color-text-muted)'
}
function statusLabel(s) {
  return { completed:'✅ Đã hoàn thành', available:'▶ Sẵn sàng', locked:'🔒 Chưa mở',
           in_progress:'⏳ Đang học' }[s] || s
}
</script>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: opacity .3s ease, transform .3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(0.5rem); }
.perfect-toast-enter-active, .perfect-toast-leave-active { transition: opacity .35s ease, transform .35s ease; }
.perfect-toast-enter-from, .perfect-toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(-0.75rem) scale(0.96); }
.perfect-toast-icon { animation: perfect-bob 1.4s ease-in-out infinite; }
.perfect-toast-glow {
  background: linear-gradient(110deg, transparent 0%, rgba(255,255,255,0.24) 35%, transparent 70%);
  transform: translateX(-100%);
  animation: perfect-sheen 2.2s ease-in-out infinite;
}
.course-complete-sheen {
  background: linear-gradient(120deg, transparent 0%, rgba(255,255,255,0.12) 30%, transparent 60%);
  transform: translateX(-120%);
  animation: perfect-sheen 3.6s ease-in-out infinite;
}
@keyframes perfect-sheen {
  0% { transform: translateX(-120%); }
  100% { transform: translateX(140%); }
}
@keyframes perfect-bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}
</style>
