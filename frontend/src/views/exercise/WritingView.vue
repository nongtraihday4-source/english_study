<template>
  <!-- Normal mode wrapper -->
  <div class="p-4 sm:p-6 max-w-4xl mx-auto">

    <!-- Error toast -->
    <Transition name="toast">
      <div v-if="errorToast"
           class="fixed bottom-6 left-1/2 z-50 px-5 py-3 rounded-xl shadow-xl text-sm font-semibold"
           style="-webkit-transform:translateX(-50%);transform:translateX(-50%);
                  background:#450a0a; border:1px solid rgba(239,68,68,0.5); color:#fca5a5;">
        ⚠️ {{ errorToast }}
      </div>
    </Transition>

    <!-- Header -->
    <div class="flex items-center justify-between gap-3 mb-6 flex-wrap">
      <div class="flex items-center gap-3">
        <RouterLink to="/courses" class="text-sm transition hover:opacity-80"
                    style="color: var(--color-text-muted)">← Quay lại</RouterLink>
        <h1 class="text-xl font-bold" style="color: var(--color-text-base)">Luyện viết</h1>
      </div>
      <div class="flex items-center gap-2">
        <!-- Timer -->
        <span v-if="timerSeconds > 0" class="text-sm font-mono font-semibold px-3 py-1 rounded-lg"
              :style="timerSeconds <= 60
                ? { background: 'rgba(239,68,68,0.1)', color: '#ef4444' }
                : { background: 'var(--color-surface-03)', color: 'var(--color-text-muted)' }">
          ⏱ {{ formatTime(timerSeconds) }}
        </span>
        <!-- Zen mode toggle -->
        <button v-if="exercise" @click="enterZen"
                class="px-3 py-1.5 rounded-lg text-sm font-semibold transition hover:opacity-80"
                style="background-color: var(--color-surface-03); color: var(--color-text-muted)">
          ☯ Zen mode
        </button>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-4">
      <div class="h-32 rounded-2xl animate-pulse" style="background-color: var(--color-surface-02)"></div>
      <div class="h-10 rounded-xl animate-pulse" style="background-color: var(--color-surface-02)"></div>
      <div class="h-64 rounded-2xl animate-pulse" style="background-color: var(--color-surface-02)"></div>
    </div>

    <!-- Draft restore banner -->
    <Transition name="slide-down">
      <div v-if="showDraftBanner"
           class="mb-4 flex items-center justify-between gap-3 rounded-xl px-4 py-3 flex-wrap"
           style="background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.28)">
        <p class="text-sm" style="color: var(--color-text-base)">
          📝 Bạn có bản nháp chưa hoàn thành. Tiếp tục?
        </p>
        <div class="flex gap-2">
          <button @click="restoreDraft"
                  class="px-3 py-1 rounded-lg text-xs font-semibold text-white transition hover:opacity-90"
                  style="background: #4f46e5">Tiếp tục</button>
          <button @click="discardDraft"
                  class="px-3 py-1 rounded-lg text-xs font-semibold transition hover:opacity-80"
                  style="background-color: var(--color-surface-03); color: var(--color-text-muted)">Bỏ qua</button>
        </div>
      </div>
    </Transition>

    <div v-if="exercise" class="space-y-4">

      <!-- Prompt card -->
      <div class="rounded-2xl p-5"
           style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
        <p class="text-xs font-semibold uppercase tracking-wider mb-2"
           style="color: var(--color-text-muted)">Đề bài</p>
        <p class="font-semibold text-base leading-relaxed"
           style="color: var(--color-text-base)">{{ exercise.prompt_text }}</p>
        <p class="text-xs mt-2" style="color: var(--color-text-muted)">
          Yêu cầu: {{ exercise.min_words }}–{{ exercise.max_words }} từ
          <template v-if="exercise.time_limit_minutes">
            · Thời gian: {{ exercise.time_limit_minutes }} phút
          </template>
        </p>
        <!-- Structure tips -->
        <div v-if="structureTips.length" class="mt-3 pt-3"
             style="border-top: 1px solid var(--color-surface-04)">
          <p class="text-xs font-semibold mb-2" style="color: var(--color-text-muted)">💡 Gợi ý cấu trúc</p>
          <ul class="space-y-0.5">
            <li v-for="(tip, idx) in structureTips" :key="idx"
                class="text-xs" style="color: var(--color-text-muted)">• {{ tip }}</li>
          </ul>
        </div>
      </div>

      <!-- Smart toolbar -->
      <div class="flex items-center gap-2 flex-wrap rounded-xl px-3 py-2"
           style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
        <span class="text-xs font-semibold mr-1" style="color: var(--color-text-muted)">Gợi ý:</span>
        <button v-for="tool in toolbarItems" :key="tool.label"
                @click="insertFormat(tool.prefix, tool.suffix, tool.placeholder)"
                :title="tool.title"
                class="px-2 py-0.5 rounded text-xs font-semibold transition hover:opacity-80"
                style="background-color: var(--color-surface-03); color: var(--color-text-base)">
          {{ tool.label }}
        </button>
        <div class="flex-1 min-w-0" />
        <span v-if="lastSavedTime" class="text-xs" style="color: var(--color-text-muted)">
          💾 {{ lastSavedTime }}
        </span>
        <button @click="saveDraft"
                class="px-3 py-1 rounded-lg text-xs font-semibold transition hover:opacity-80"
                style="background-color: var(--color-surface-03); color: var(--color-text-base)">
          Lưu nháp
        </button>
      </div>

      <!-- Textarea editor -->
      <div class="rounded-2xl overflow-hidden"
           style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
        <textarea ref="textareaRef" v-model="content" rows="14"
                  placeholder="Viết bài của bạn tại đây..."
                  class="w-full px-5 py-4 outline-none resize-none"
                  style="background-color: transparent; color: var(--color-text-base);
                         font-size: 15px; line-height: 1.85; min-height: 280px"></textarea>
      </div>

      <!-- Word count + progress bar -->
      <div class="space-y-1.5">
        <div class="flex items-center justify-between text-sm">
          <span class="font-semibold" :style="{ color: wordCountColor }">
            {{ wordCount }} / {{ exercise.min_words }} từ
          </span>
          <span class="text-xs" style="color: var(--color-text-muted)">
            Tối đa: {{ exercise.max_words }} từ
          </span>
        </div>
        <div class="h-2 w-full rounded-full overflow-hidden"
             style="background-color: var(--color-surface-04)">
          <div class="h-2 rounded-full transition-all duration-300"
               :style="{ width: wordCountBarWidth, background: wordCountBarColor }"></div>
        </div>
        <p v-if="wordCount > exercise.max_words" class="text-xs" style="color: #eab308">
          ⚠️ Vượt quá {{ exercise.max_words }} từ (thừa {{ wordCount - exercise.max_words }} từ)
        </p>
      </div>

      <!-- Submit -->
      <button @click="submit" :disabled="submitting || wordCount < (exercise.min_words || 1)"
              class="w-full py-3 rounded-xl font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
              style="background: linear-gradient(135deg, #4f46e5, #7c3aed)">
        {{ submitting ? 'Đang nộp...' : 'Nộp bài' }}
      </button>
    </div>

    <!-- Not found -->
    <div v-else-if="!loading" class="text-center py-16" style="color: var(--color-text-muted)">
      <p class="text-4xl mb-3">✍️</p>
      <p>Không tìm thấy bài tập.</p>
    </div>
  </div>

  <!-- Zen mode overlay — Teleport to body to cover sidebar/header -->
  <Teleport to="body">
    <Transition name="zen-fade">
      <div v-if="isZenMode" class="zen-overlay" @keydown.esc.prevent="exitZen" tabindex="-1">
        <!-- Top bar -->
        <div class="zen-topbar">
          <span class="zen-brand">☯ Zen Mode</span>
          <div style="display: flex; align-items: center; gap: 12px">
            <span class="text-sm font-mono font-semibold" :style="{ color: wordCountColor }">
              {{ wordCount }} từ
            </span>
            <button @click="exitZen" class="zen-exit-btn">← Thoát</button>
          </div>
        </div>
        <!-- Writing area -->
        <div class="zen-content">
          <p class="zen-prompt-label">Đề bài</p>
          <p class="zen-prompt-text">{{ exercise?.prompt_text }}</p>
          <textarea v-model="content" class="zen-textarea" autofocus
                    placeholder="Viết bài của bạn..."
                    @keydown.esc.prevent="exitZen"></textarea>
          <!-- Word count bar -->
          <div class="zen-wordcount">
            <span :style="{ color: wordCountColor }">
              {{ wordCount }} / {{ exercise?.min_words }} từ
            </span>
            <div class="zen-progress">
              <div :style="{ width: wordCountBarWidth, background: wordCountBarColor }"></div>
            </div>
          </div>
          <!-- Zen submit -->
          <button @click="submit" :disabled="submitting || wordCount < (exercise?.min_words || 1)"
                  class="zen-submit-btn">
            {{ submitting ? 'Đang nộp...' : 'Nộp bài' }}
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getExercise } from '@/api/curriculum.js'
import { progressApi } from '@/api/progress.js'

const route = useRoute()
const router = useRouter()

const exercise = ref(null)
const loading = ref(false)
const content = ref('')
const submitting = ref(false)
const textareaRef = ref(null)
const isZenMode = ref(false)

const showDraftBanner = ref(false)
const savedDraftContent = ref('')
const lastSavedTime = ref('')

const errorToast = ref('')
let _errorToastTimer = null

function showErrorToast(message) {
  clearTimeout(_errorToastTimer)
  errorToast.value = message
  _errorToastTimer = setTimeout(() => { errorToast.value = '' }, 4000)
}

const timerSeconds = ref(0)
let timerInterval = null
let autoSaveInterval = null

// ─── Draft key ───────────────────────────────────────────────────────────────
const draftKey = computed(() =>
  exercise.value ? `draft_writing_${exercise.value.id}` : null
)

// ─── Word count ───────────────────────────────────────────────────────────────
const wordCount = computed(() =>
  content.value.trim() ? content.value.trim().split(/\s+/).length : 0
)

const wordCountColor = computed(() => {
  if (!exercise.value) return 'var(--color-text-muted)'
  if (wordCount.value < exercise.value.min_words) return '#ef4444'
  if (wordCount.value <= exercise.value.max_words) return '#22c55e'
  return '#eab308'
})

const wordCountBarWidth = computed(() => {
  if (!exercise.value) return '0%'
  const pct = Math.min((wordCount.value / exercise.value.min_words) * 100, 100)
  return `${Math.max(0, pct)}%`
})

const wordCountBarColor = computed(() => {
  if (!exercise.value) return '#ef4444'
  if (wordCount.value < exercise.value.min_words) return 'linear-gradient(90deg,#ef4444,#f87171)'
  if (wordCount.value <= exercise.value.max_words) return 'linear-gradient(90deg,#22c55e,#4ade80)'
  return 'linear-gradient(90deg,#eab308,#facc15)'
})

// ─── Structure tips ───────────────────────────────────────────────────────────
const structureTips = computed(() => {
  if (!exercise.value?.structure_tips_json) return []
  try {
    const tips = typeof exercise.value.structure_tips_json === 'string'
      ? JSON.parse(exercise.value.structure_tips_json)
      : exercise.value.structure_tips_json
    return Array.isArray(tips) ? tips : []
  } catch { return [] }
})

// ─── Toolbar items ────────────────────────────────────────────────────────────
const toolbarItems = [
  { label: 'B', title: 'Bold (chữ đậm)',      prefix: '**', suffix: '**', placeholder: 'chữ đậm' },
  { label: 'I', title: 'Italic (chữ nghiêng)', prefix: '_',  suffix: '_',   placeholder: 'chữ nghiêng' },
  { label: 'H2', title: 'Heading (tiêu đề)',   prefix: '\n## ', suffix: '\n', placeholder: 'Tiêu đề' },
  { label: '¶',  title: 'Đoạn mới',            prefix: '\n\n', suffix: '',   placeholder: '' },
]

function insertFormat(prefix, suffix, placeholder) {
  const ta = textareaRef.value
  if (!ta) return
  const start = ta.selectionStart
  const end   = ta.selectionEnd
  const selected = content.value.substring(start, end) || placeholder
  const before = content.value.substring(0, start)
  const after  = content.value.substring(end)
  content.value = before + prefix + selected + suffix + after
  nextTick(() => {
    ta.focus()
    ta.setSelectionRange(start + prefix.length, start + prefix.length + selected.length)
  })
}

// ─── Zen mode ─────────────────────────────────────────────────────────────────
function enterZen() {
  isZenMode.value = true
  document.body.style.overflow = 'hidden'
}

function exitZen() {
  isZenMode.value = false
  document.body.style.overflow = ''
}

// ─── Draft save / restore ─────────────────────────────────────────────────────
function saveDraft() {
  if (!draftKey.value) return
  localStorage.setItem(draftKey.value, content.value)
  const now = new Date()
  lastSavedTime.value = `${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}`
}

function restoreDraft() {
  content.value = savedDraftContent.value
  showDraftBanner.value = false
}

function discardDraft() {
  if (draftKey.value) localStorage.removeItem(draftKey.value)
  showDraftBanner.value = false
}

function checkForDraft() {
  if (!draftKey.value) return
  const saved = localStorage.getItem(draftKey.value)
  if (saved && saved.trim()) {
    savedDraftContent.value = saved
    showDraftBanner.value = true
  }
}

// ─── Timer ────────────────────────────────────────────────────────────────────
function formatTime(secs) {
  const m = Math.floor(secs / 60).toString().padStart(2, '0')
  const s = (secs % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

function startTimer(limitMinutes) {
  timerSeconds.value = limitMinutes * 60
  timerInterval = setInterval(() => {
    if (timerSeconds.value <= 0) {
      clearInterval(timerInterval)
      submit()
      return
    }
    timerSeconds.value--
  }, 1000)
}

// ─── Auto-save ────────────────────────────────────────────────────────────────
function startAutoSave() {
  autoSaveInterval = setInterval(() => {
    if (content.value.trim()) saveDraft()
  }, 30000)
}

// ─── Submit + AI poll ─────────────────────────────────────────────────────────
async function submit() {
  if (submitting.value) return
  submitting.value = true
  try {
    const res = await progressApi.submitWriting({
      exercise_id: exercise.value.id,
      lesson_id: route.query.lesson_id || null,
      content_text: content.value,
    })
    const payload = res.data?.data ?? res.data
    const submissionId = payload?.submission_id || payload?.id
    if (draftKey.value) localStorage.removeItem(draftKey.value)
    exitZen()
    router.push(`/learn/result/${submissionId}?type=writing`)
  } catch (err) {
    showErrorToast(err?.response?.data?.detail || 'Đã có lỗi xảy ra, vui lòng thử lại.')
  }
  finally { submitting.value = false }
}

// ─── Lifecycle ────────────────────────────────────────────────────────────────
onMounted(async () => {
  loading.value = true
  try {
    const res = await getExercise('writing', route.params.id)
    exercise.value = res.data?.data ?? res.data
    checkForDraft()
    if (exercise.value?.time_limit_minutes > 0) {
      startTimer(exercise.value.time_limit_minutes)
    }
    startAutoSave()
  } catch {
    exercise.value = null
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  clearInterval(timerInterval)
  clearInterval(autoSaveInterval)
  exitZen()
})
</script>

<style scoped>
/* ── Zen mode overlay ─────────────────────────────────────────────────────── */
.zen-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: linear-gradient(135deg, #0d0d1a 0%, #111827 60%, #0f0f1e 100%);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.zen-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 28px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.zen-brand {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.3);
}

.zen-exit-btn {
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.07);
  border: none;
  cursor: pointer;
  transition: all 0.15s;
}
.zen-exit-btn:hover {
  color: rgba(255, 255, 255, 0.85);
  background: rgba(255, 255, 255, 0.12);
}

.zen-content {
  flex: 1;
  overflow-y: auto;
  max-width: 760px;
  width: 100%;
  margin: 0 auto;
  padding: 44px 28px 32px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.zen-prompt-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: rgba(255, 255, 255, 0.28);
}

.zen-prompt-text {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 16px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.65);
  padding: 16px 20px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.07);
}

.zen-textarea {
  flex: 1;
  min-height: 320px;
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  resize: none;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 18px;
  line-height: 1.95;
  color: rgba(255, 255, 255, 0.88);
  caret-color: #818cf8;
}
.zen-textarea::placeholder {
  color: rgba(255, 255, 255, 0.2);
}

.zen-wordcount {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
}

.zen-progress {
  height: 3px;
  width: 100%;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  overflow: hidden;
}
.zen-progress > div {
  height: 3px;
  border-radius: 999px;
  transition: width 0.3s ease;
}

.zen-submit-btn {
  align-self: flex-start;
  padding: 10px 32px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border: none;
  cursor: pointer;
  transition: opacity 0.15s;
}
.zen-submit-btn:hover:not(:disabled) { opacity: 0.88; }
.zen-submit-btn:disabled { opacity: 0.45; cursor: not-allowed; }

/* ── Transitions ──────────────────────────────────────────────────────────── */
.zen-fade-enter-active { transition: opacity 0.2s ease; }
.zen-fade-leave-active { transition: opacity 0.15s ease; }
.zen-fade-enter-from, .zen-fade-leave-to { opacity: 0; }

.slide-down-enter-active { transition: all 0.25s ease; }
.slide-down-leave-active { transition: all 0.2s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-8px); }

.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translate(-50%, 12px); }
</style>
