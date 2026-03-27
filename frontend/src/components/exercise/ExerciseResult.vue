<template>
  <div class="space-y-8">

    <!-- ── Score circle ──────────────────────────────────────────── -->
    <div class="er-rise flex flex-col items-center gap-4" style="--er-delay:0s">
      <div class="relative" style="width:200px;height:200px">
        <svg viewBox="0 0 200 200" width="200" height="200">
          <defs>
            <linearGradient :id="`sg-${uid}`" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%"   :stop-color="scoreColor" />
              <stop offset="100%" :stop-color="scoreColorEnd" />
            </linearGradient>
          </defs>
          <!-- Track -->
          <circle cx="100" cy="100" r="85" fill="none"
                  stroke="var(--color-surface-04)" stroke-width="14" />
          <!-- Progress arc -->
          <circle cx="100" cy="100" r="85" fill="none"
                  :stroke="`url(#sg-${uid})`" stroke-width="14"
                  stroke-linecap="round"
                  :stroke-dasharray="CIRCUMFERENCE"
                  :stroke-dashoffset="dashOffset"
                  transform="rotate(-90 100 100)"
                  style="transition:stroke-dashoffset 1.5s cubic-bezier(0.22,1,0.36,1)" />
        </svg>
        <!-- Center text -->
        <div class="absolute inset-0 flex flex-col items-center justify-center select-none">
          <p class="font-black leading-none" style="font-size:3.25rem;color:var(--color-text-base)">
            {{ animatedScore }}<span style="font-size:1.5rem">%</span>
          </p>
          <p class="text-xs font-semibold uppercase tracking-widest mt-1"
             style="color:var(--color-text-muted)">Điểm</p>
        </div>
      </div>

      <!-- PASS / FAIL badge -->
      <span class="px-5 py-1.5 rounded-full text-sm font-bold"
            :style="passed
              ? 'background:rgba(34,197,94,0.15);color:#16a34a;border:1px solid rgba(34,197,94,0.3)'
              : 'background:rgba(239,68,68,0.12);color:#ef4444;border:1px solid rgba(239,68,68,0.25)'">
        {{ passed ? '✓ PASS' : '✗ FAIL' }} &nbsp;·&nbsp; Ngưỡng 60%
      </span>

      <!-- CEFR pill -->
      <span class="px-4 py-1.5 rounded-full text-xs font-semibold"
            style="background:rgba(99,102,241,0.12);color:#818cf8;border:1px solid rgba(99,102,241,0.25)">
        Tương đương CEFR: {{ computedCefr }}
      </span>
    </div>

    <!-- ── Detail tabs ────────────────────────────────────────────── -->
    <div v-if="availableTabs.length" class="er-rise" style="--er-delay:0.15s">
      <!-- Tab strip -->
      <div class="flex gap-1 p-1 rounded-xl mb-4" style="background-color:var(--color-surface-02)">
        <button v-for="tab in availableTabs" :key="tab.key"
                @click="activeTab = tab.key"
                class="flex-1 px-3 py-2 rounded-lg text-sm font-semibold transition"
                :style="activeTab === tab.key
                  ? 'background:linear-gradient(135deg,#4f46e5,#7c3aed);color:white'
                  : 'color:var(--color-text-muted)'">
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab panels -->
      <Transition name="er-tab" mode="out-in">

        <!-- Tab: Đáp án (Listening / Reading) -->
        <div v-if="activeTab === 'answers'" key="answers"
             class="rounded-2xl overflow-hidden"
             style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
          <div class="px-5 py-3 flex items-center justify-between"
               style="border-bottom:1px solid var(--color-surface-04);background-color:var(--color-surface-03)">
            <p class="text-sm font-semibold" style="color:var(--color-text-base)">Chi tiết câu trả lời</p>
            <span class="text-xs" style="color:var(--color-text-muted)">
              Đúng {{ correctCount }}/{{ totalQuestions }}
            </span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm" style="color:var(--color-text-base)">
              <thead style="color:var(--color-text-muted)">
                <tr>
                  <th class="text-left px-4 py-2.5 w-10 font-medium">#</th>
                  <th class="text-left px-4 py-2.5 font-medium">Câu hỏi</th>
                  <th class="text-left px-4 py-2.5 font-medium">Bạn chọn</th>
                  <th class="text-left px-4 py-2.5 font-medium">Đáp án đúng</th>
                  <th class="text-center px-4 py-2.5 font-medium w-16">Kết quả</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in answers" :key="row.question_id ?? idx"
                    class="border-t transition hover:bg-white/5"
                    style="border-color:var(--color-surface-04)">
                  <td class="px-4 py-3 text-center" style="color:var(--color-text-muted)">{{ idx + 1 }}</td>
                  <td class="px-4 py-3">{{ row.question || `Câu ${idx + 1}` }}</td>
                  <td class="px-4 py-3" style="color:var(--color-text-soft)">{{ row.user_answer ?? '—' }}</td>
                  <td class="px-4 py-3" style="color:#4ade80">{{ row.correct_answer ?? '—' }}</td>
                  <td class="px-4 py-3 text-center text-base">{{ row.is_correct ? '✅' : '❌' }}</td>
                </tr>
                <tr v-if="!answers?.length">
                  <td colspan="5" class="px-4 py-8 text-center text-sm"
                      style="color:var(--color-text-muted)">Không có dữ liệu chi tiết câu hỏi.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Tab: Rubric (Speaking / Writing) -->
        <div v-else-if="activeTab === 'rubric'" key="rubric"
             class="rounded-2xl p-6 space-y-5"
             style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
          <div v-if="!rubric?.length" class="text-center py-8 text-sm"
               style="color:var(--color-text-muted)">
            Kết quả đang được chấm...
          </div>
          <template v-else>
            <div v-for="item in rubric" :key="item.criterion">
              <div class="flex items-center justify-between text-sm mb-1.5">
                <span class="font-medium" style="color:var(--color-text-base)">
                  {{ item.criterion }}
                  <span class="text-xs font-normal ml-1"
                        style="color:var(--color-text-muted)">({{ item.weight }}%)</span>
                </span>
                <span class="font-bold tabular-nums"
                      style="color:var(--color-text-base)">{{ item.score ?? '?' }}/100</span>
              </div>
              <div class="h-2.5 w-full rounded-full overflow-hidden"
                   style="background-color:var(--color-surface-04)">
                <div class="h-full rounded-full transition-all duration-700"
                     :style="{ width:`${Math.min(item.score ?? 0, 100)}%`,
                               background: rubricBarColor(item.score) }"></div>
              </div>
              <p v-if="item.feedback" class="text-xs mt-1"
                 style="color:var(--color-text-muted)">{{ item.feedback }}</p>
            </div>
            <div v-if="feedbackText" class="rounded-xl p-4 mt-2"
                 style="background-color:var(--color-surface-03);border:1px solid var(--color-surface-04)">
              <p class="text-sm font-semibold mb-1"
                 style="color:var(--color-text-base)">💬 Nhận xét tổng quan</p>
              <p class="text-sm" style="color:var(--color-text-muted)">{{ feedbackText }}</p>
            </div>
          </template>
        </div>

        <!-- Tab: Lỗi phát âm (Speaking) -->
        <div v-else-if="activeTab === 'pronunciation'" key="pronunciation"
             class="rounded-2xl overflow-hidden"
             style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
          <div class="px-5 py-3"
               style="border-bottom:1px solid var(--color-surface-04);background-color:var(--color-surface-03)">
            <p class="text-sm font-semibold" style="color:var(--color-text-base)">
              🔤 Phân tích phát âm từng từ
            </p>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm" style="color:var(--color-text-base)">
              <thead style="color:var(--color-text-muted)">
                <tr class="border-b" style="border-color:var(--color-surface-04)">
                  <th class="text-left px-4 py-2.5 font-medium">Từ</th>
                  <th class="text-left px-4 py-2.5 font-medium">Bạn phát âm</th>
                  <th class="text-left px-4 py-2.5 font-medium">Chuẩn IPA</th>
                  <th class="text-center px-4 py-2.5 font-medium w-16">Điểm</th>
                  <th class="text-left px-4 py-2.5 font-medium">Gợi ý</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(err, idx) in errorList" :key="idx"
                    class="border-t transition hover:bg-white/5"
                    style="border-color:var(--color-surface-04)">
                  <td class="px-4 py-3 font-semibold">{{ err.word ?? '—' }}</td>
                  <td class="px-4 py-3 font-mono text-xs"
                      :style="(err.score ?? 100) < 60 ? 'color:#f87171' : 'color:var(--color-text-muted)'">
                    {{ err.user_ipa ?? '—' }}
                  </td>
                  <td class="px-4 py-3 font-mono text-xs" style="color:#4ade80">
                    {{ err.expected_ipa ?? '—' }}
                  </td>
                  <td class="px-4 py-3 text-center">
                    <span class="px-2 py-0.5 rounded text-xs font-semibold"
                          :style="(err.score ?? 0) >= 60
                            ? 'background:rgba(34,197,94,0.12);color:#16a34a'
                            : 'background:rgba(239,68,68,0.12);color:#ef4444'">
                      {{ err.score ?? '—' }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-xs"
                      style="color:var(--color-text-muted)">{{ err.feedback ?? '—' }}</td>
                </tr>
                <tr v-if="!errorList?.length">
                  <td colspan="5" class="px-4 py-8 text-center text-sm"
                      style="color:var(--color-text-muted)">
                    Tuyệt vời! Không phát hiện lỗi phát âm nào.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Tab: Lỗi viết (Writing) -->
        <div v-else-if="activeTab === 'errors'" key="errors"
             class="rounded-2xl overflow-hidden"
             style="background-color:var(--color-surface-02);border:1px solid var(--color-surface-04)">
          <div class="px-5 py-3"
               style="border-bottom:1px solid var(--color-surface-04);background-color:var(--color-surface-03)">
            <p class="text-sm font-semibold"
               style="color:var(--color-text-base)">✏️ Lỗi ngữ pháp / từ vựng</p>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm" style="color:var(--color-text-base)">
              <thead style="color:var(--color-text-muted)">
                <tr class="border-b" style="border-color:var(--color-surface-04)">
                  <th class="text-left px-4 py-2.5 font-medium">Lỗi</th>
                  <th class="text-left px-4 py-2.5 font-medium">Loại</th>
                  <th class="text-left px-4 py-2.5 font-medium">Sửa thành</th>
                  <th class="text-left px-4 py-2.5 font-medium">Ghi chú</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(err, idx) in errorList" :key="idx"
                    class="border-t transition hover:bg-white/5"
                    style="border-color:var(--color-surface-04)">
                  <td class="px-4 py-3">
                    <span class="px-1.5 py-0.5 rounded text-xs font-mono"
                          style="background:rgba(239,68,68,0.1);color:#f87171">
                      {{ err.word || err.phrase || '—' }}
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    <span class="px-2 py-0.5 rounded text-xs font-semibold capitalize"
                          :style="(err.type || err.error_type) === 'grammar'
                            ? 'background:rgba(59,130,246,0.12);color:#60a5fa'
                            : 'background:rgba(168,85,247,0.12);color:#c084fc'">
                      {{ err.type || err.error_type || '—' }}
                    </span>
                  </td>
                  <td class="px-4 py-3 font-mono text-xs" style="color:#4ade80">
                    {{ err.suggestion || err.correction || '—' }}
                  </td>
                  <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">
                    {{ err.feedback || err.note || '—' }}
                  </td>
                </tr>
                <tr v-if="!errorList?.length">
                  <td colspan="4" class="px-4 py-8 text-center text-sm"
                      style="color:var(--color-text-muted)">
                    Không tìm thấy lỗi ngữ pháp hay từ vựng.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </Transition>
    </div>

    <!-- ── Action buttons ─────────────────────────────────────────── -->
    <div class="er-rise flex flex-col sm:flex-row items-center justify-center gap-3 pt-2"
         style="--er-delay:0.3s">
      <button v-if="passed"
              @click="$emit('next-lesson')"
              class="w-full sm:w-auto px-8 py-2.5 rounded-xl font-semibold text-white text-sm transition hover:opacity-90"
              style="background:linear-gradient(135deg,#22c55e,#16a34a)">
        Bài tiếp theo →
      </button>
      <button v-else
              @click="$emit('retry')"
              class="w-full sm:w-auto px-8 py-2.5 rounded-xl font-semibold text-white text-sm transition hover:opacity-90"
              style="background:linear-gradient(135deg,#4f46e5,#7c3aed)">
        🔄 Làm lại
      </button>
      <button @click="$emit('dashboard')"
              class="w-full sm:w-auto px-6 py-2.5 rounded-xl text-sm font-medium transition hover:opacity-80"
              style="background-color:var(--color-surface-02);color:var(--color-text-muted)">
        ← Về Dashboard
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  type:          { type: String,  required: true },
  score:         { type: Number,  default: 0 },
  passed:        { type: Boolean, default: false },
  maxScore:      { type: Number,  default: 100 },
  answers:       { type: Array,   default: () => [] },
  rubric:        { type: Array,   default: () => [] },
  errorList:     { type: Array,   default: () => [] },
  feedbackText:  { type: String,  default: '' },
  cefrEquivalent:{ type: String,  default: '' },
  nextLessonId:  { type: Number,  default: null },
})

defineEmits(['retry', 'next-lesson', 'dashboard'])

// Unique ID per instance so SVG gradient IDs don't clash if mounted twice
const uid = Math.random().toString(36).slice(2, 7)

// ── Score circle ─────────────────────────────────────────────────────────────
const CIRCUMFERENCE = 2 * Math.PI * 85  // r = 85
const animatedScore = ref(0)

const dashOffset = computed(() => CIRCUMFERENCE * (1 - animatedScore.value / 100))

const scoreColor = computed(() => {
  const s = animatedScore.value
  if (s < 40) return '#ef4444'
  if (s < 60) return '#f97316'
  if (s < 75) return '#eab308'
  return '#22c55e'
})
const scoreColorEnd = computed(() => {
  const s = animatedScore.value
  if (s < 40) return '#dc2626'
  if (s < 60) return '#ea580c'
  if (s < 75) return '#ca8a04'
  return '#16a34a'
})

function runCountUp(target) {
  const duration = 1500
  const start = performance.now()
  const from = animatedScore.value
  function frame(now) {
    const t = Math.min((now - start) / duration, 1)
    const eased = 1 - Math.pow(1 - t, 3)    // cubic ease-out
    animatedScore.value = Math.round(from + eased * (target - from))
    if (t < 1) requestAnimationFrame(frame)
  }
  requestAnimationFrame(frame)
}

onMounted(() => runCountUp(props.score ?? 0))
watch(() => props.score, (val) => runCountUp(val ?? 0))

// ── CEFR ─────────────────────────────────────────────────────────────────────
const computedCefr = computed(() => {
  if (props.cefrEquivalent) return props.cefrEquivalent
  const s = props.score
  if (s <= 39) return 'Below A1'
  if (s <= 59) return 'A1'
  if (s <= 74) return 'A2'
  if (s <= 84) return 'B1'
  if (s <= 92) return 'B2'
  return 'C1/C2'
})

// ── Answers tab ──────────────────────────────────────────────────────────────
const correctCount  = computed(() => (props.answers || []).filter(a => a.is_correct).length)
const totalQuestions = computed(() => (props.answers || []).length)

// ── Rubric tab ───────────────────────────────────────────────────────────────
function rubricBarColor(score) {
  if (!score) return '#6b7280'
  if (score < 40) return '#ef4444'
  if (score < 60) return '#f97316'
  if (score < 75) return '#eab308'
  return '#22c55e'
}

// ── Tabs ─────────────────────────────────────────────────────────────────────
const availableTabs = computed(() => {
  const tabs = []
  const t = props.type
  if (t === 'listening' || t === 'reading')  tabs.push({ key: 'answers',       label: '📋 Đáp án' })
  if (t === 'speaking'  || t === 'writing')  tabs.push({ key: 'rubric',        label: '📊 Rubric' })
  if (t === 'speaking')                       tabs.push({ key: 'pronunciation', label: '🔤 Lỗi phát âm' })
  if (t === 'writing' && (props.errorList?.length || 0) > 0)
                                              tabs.push({ key: 'errors',        label: '✏️ Lỗi viết' })
  return tabs
})

const activeTab = ref('')
watch(availableTabs, (tabs) => {
  if (tabs.length && !tabs.find(t => t.key === activeTab.value)) {
    activeTab.value = tabs[0].key
  }
}, { immediate: true })
</script>

<style scoped>
/* ── Appear animations ──────────────────────────────────────────────────── */
.er-rise {
  animation: er-rise-in 0.5s ease-out both;
  animation-delay: var(--er-delay, 0s);
}
@keyframes er-rise-in {
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0);    }
}

/* ── Tab panel transition ───────────────────────────────────────────────── */
.er-tab-enter-active,
.er-tab-leave-active { transition: opacity 0.18s ease; }
.er-tab-enter-from,
.er-tab-leave-to     { opacity: 0; }
</style>
