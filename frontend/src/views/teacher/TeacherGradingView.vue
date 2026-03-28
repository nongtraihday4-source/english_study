<template>
  <div class="flex gap-0 h-[calc(100vh-8rem)] overflow-hidden -m-6">
    <!-- ── Left column: table ─────────────────────────────────────────────── -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden p-6">

      <!-- Filters -->
      <div class="flex flex-wrap gap-3 mb-4 shrink-0">
        <input
          v-model="search" type="search" placeholder="Tìm học viên / bài tập…"
          class="flex-1 min-w-[180px] px-3 py-2 rounded-xl text-sm focus:outline-none"
          style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-text-base)"
        />
        <select v-model="statusFilter"
          class="px-3 py-2 rounded-xl text-sm focus:outline-none"
          style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-text-base)"
        >
          <option value="pending">Chờ chấm</option>
          <option value="completed">Đã chấm</option>
          <option value="all">Tất cả</option>
        </select>
        <select v-model="typeFilter"
          class="px-3 py-2 rounded-xl text-sm focus:outline-none"
          style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04); color: var(--color-text-base)"
        >
          <option value="all">Mọi loại</option>
          <option value="speaking">Speaking 🎤</option>
          <option value="writing">Writing ✍️</option>
        </select>
        <button @click="load" class="px-3 py-2 rounded-xl text-sm hover:opacity-80 transition"
          style="background-color: var(--color-surface-03); color: var(--color-text-base)"
        >
          {{ loading ? '⟳' : '🔄' }}
        </button>
      </div>

      <!-- Table -->
      <div class="flex-1 overflow-y-auto rounded-2xl"
        style="border: 1px solid var(--color-surface-04)"
      >
        <table class="w-full text-sm border-collapse">
          <thead>
            <tr style="background-color: var(--color-surface-03); color: var(--color-text-muted)">
              <th class="text-left px-4 py-3 font-semibold">Học viên</th>
              <th class="text-left px-4 py-3 font-semibold hidden md:table-cell">Bài tập</th>
              <th class="text-left px-4 py-3 font-semibold">Loại</th>
              <th class="text-left px-4 py-3 font-semibold hidden sm:table-cell">Nộp lúc</th>
              <th class="text-left px-4 py-3 font-semibold">Trạng thái</th>
            </tr>
          </thead>
          <tbody>
            <template v-if="loading">
              <tr v-for="i in 8" :key="i">
                <td colspan="5" class="px-4 py-3">
                  <div class="h-4 rounded animate-pulse w-3/4"
                    style="background-color: var(--color-surface-03)"
                  />
                </td>
              </tr>
            </template>
            <template v-else-if="!filteredItems.length">
              <tr>
                <td colspan="5" class="text-center py-12"
                  style="color: var(--color-text-muted)"
                >
                  Không có bài nào
                </td>
              </tr>
            </template>
            <template v-else>
              <tr
                v-for="item in filteredItems"
                :key="item.type + item.id"
                @click="select(item)"
                class="cursor-pointer hover:opacity-80 transition"
                :class="{ 'ring-1 ring-inset ring-[var(--color-primary-500)]': selected?.id === item.id && selected?.type === item.type }"
                style="border-top: 1px solid var(--color-surface-04)"
              >
                <td class="px-4 py-3">
                  <p class="font-medium" style="color: var(--color-text-base)">
                    {{ item.student?.full_name || item.student?.email }}
                  </p>
                  <p class="text-xs mt-0.5" style="color: var(--color-text-muted)">
                    {{ item.student?.email }}
                  </p>
                </td>
                <td class="px-4 py-3 hidden md:table-cell" style="color: var(--color-text-soft)">
                  {{ item.exercise_title || '—' }}
                </td>
                <td class="px-4 py-3">
                  <span class="px-2 py-0.5 rounded-full text-xs font-semibold"
                    :style="item.type === 'speaking'
                      ? 'background-color:color-mix(in srgb,#fb923c 15%,transparent);color:#fb923c'
                      : 'background-color:color-mix(in srgb,#60a5fa 15%,transparent);color:#60a5fa'"
                  >
                    {{ item.type === 'speaking' ? '🎤 Speaking' : '✍️ Writing' }}
                  </span>
                </td>
                <td class="px-4 py-3 hidden sm:table-cell text-xs" style="color: var(--color-text-muted)">
                  {{ fmtDate(item.submitted_at) }}
                </td>
                <td class="px-4 py-3">
                  <span class="px-2 py-0.5 rounded-full text-xs font-semibold"
                    :style="item.status === 'completed'
                      ? 'background-color:color-mix(in srgb,#4ade80 15%,transparent);color:#4ade80'
                      : 'background-color:color-mix(in srgb,#fcd34d 15%,transparent);color:#fcd34d'"
                  >
                    {{ item.status === 'completed' ? '✅ Đã chấm' : '⏳ Chờ chấm' }}
                  </span>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── Right panel: grading ───────────────────────────────────────────── -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      leave-active-class="transition-all duration-150 ease-in"
      enter-from-class="translate-x-full opacity-0"
      leave-to-class="translate-x-full opacity-0"
    >
      <aside v-if="selected"
        class="w-96 shrink-0 overflow-y-auto flex flex-col"
        style="background-color: var(--color-surface-02); border-left: 1px solid var(--color-surface-04)"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-5 py-4 shrink-0"
          style="border-bottom: 1px solid var(--color-surface-04)"
        >
          <div>
            <p class="font-bold" style="color: var(--color-text-base)">Chấm bài</p>
            <p class="text-xs mt-0.5" style="color: var(--color-text-muted)">
              {{ selected.student?.full_name || selected.student?.email }}
            </p>
          </div>
          <button @click="selected = null" class="text-xl leading-none opacity-60 hover:opacity-100">×</button>
        </div>

        <div class="p-5 flex-1 space-y-5">

          <!-- Exercise info -->
          <div>
            <p class="text-xs font-semibold mb-1" style="color: var(--color-text-muted)">BÀI TẬP</p>
            <p class="text-sm font-medium" style="color: var(--color-text-base)">
              {{ selected.exercise_title || '—' }}
            </p>
          </div>

          <!-- Content -->
          <template v-if="selected.type === 'speaking'">
            <div v-if="selected.target_sentence">
              <p class="text-xs font-semibold mb-1" style="color: var(--color-text-muted)">CÂU MẪU</p>
              <p class="text-sm italic px-3 py-2 rounded-xl"
                style="background-color: var(--color-surface-03); color: var(--color-text-soft)"
              >
                "{{ selected.target_sentence }}"
              </p>
            </div>
            <div>
              <p class="text-xs font-semibold mb-1" style="color: var(--color-text-muted)">TRANSCRIPT HỌC VIÊN</p>
              <p class="text-sm px-3 py-2 rounded-xl whitespace-pre-wrap"
                style="background-color: var(--color-surface-03); color: var(--color-text-base)"
              >
                {{ selected.transcript || '(không có transcript)' }}
              </p>
            </div>
            <div v-if="selected.audio_s3_key">
              <p class="text-xs font-semibold mb-2" style="color: var(--color-text-muted)">NGHE LẠI</p>
              <audio controls class="w-full rounded-xl" :src="selected.audio_s3_key" />
            </div>
          </template>

          <template v-else>
            <div>
              <p class="text-xs font-semibold mb-1" style="color: var(--color-text-muted)">BÀI VIẾT</p>
              <p class="text-sm px-3 py-2 rounded-xl whitespace-pre-wrap max-h-56 overflow-y-auto"
                style="background-color: var(--color-surface-03); color: var(--color-text-base)"
              >
                {{ selected.content_text || '(trống)' }}
              </p>
            </div>
            <div v-if="selected.prompt_text">
              <p class="text-xs font-semibold mb-1" style="color: var(--color-text-muted)">ĐỀ BÀI</p>
              <p class="text-sm italic px-3 py-2 rounded-xl"
                style="background-color: var(--color-surface-03); color: var(--color-text-soft)"
              >
                {{ selected.prompt_text }}
              </p>
            </div>
          </template>

          <!-- AI score badge -->
          <div v-if="selected.ai_score != null"
            class="flex items-center gap-2 px-3 py-2 rounded-xl"
            style="background-color: var(--color-surface-03)"
          >
            <span class="text-sm">🤖</span>
            <p class="text-xs" style="color: var(--color-text-muted)">
              AI chấm: <strong style="color: var(--color-primary-400)">{{ selected.ai_score }}</strong>/100
            </p>
            <p v-if="selected.feedback_vi || selected.feedback_text" class="text-xs ml-2" style="color: var(--color-text-muted)">—
              {{ (selected.feedback_vi || selected.feedback_text)?.slice(0, 60) }}…
            </p>
          </div>

          <!-- Grading form -->
          <div style="border-top: 1px solid var(--color-surface-04)" class="pt-4 space-y-4">
            <div>
              <label class="text-xs font-semibold" style="color: var(--color-text-muted)">
                ĐIỂM GIÁO VIÊN (0–100)
              </label>
              <div class="flex items-center gap-3 mt-2">
                <input type="range" min="0" max="100" v-model.number="form.score"
                  class="flex-1 accent-[var(--color-primary-500)]"
                />
                <input type="number" min="0" max="100" v-model.number="form.score"
                  class="w-16 text-center px-2 py-1.5 rounded-xl text-sm font-bold focus:outline-none"
                  style="background-color: var(--color-surface-03); border: 1px solid var(--color-surface-04); color: var(--color-primary-400)"
                />
              </div>
            </div>

            <div>
              <label class="text-xs font-semibold" style="color: var(--color-text-muted)">
                NHẬN XÉT (gửi cho học viên)
              </label>
              <textarea v-model="form.feedback" rows="4"
                placeholder="Nhận xét điểm mạnh, điểm cần cải thiện…"
                class="w-full mt-2 px-3 py-2 rounded-xl text-sm resize-none focus:outline-none"
                style="background-color: var(--color-surface-03); border: 1px solid var(--color-surface-04); color: var(--color-text-base)"
              />
            </div>

            <button @click="submitGrade" :disabled="submitting"
              class="w-full py-3 rounded-xl font-bold text-sm hover:opacity-80 transition disabled:opacity-50"
              style="background-color: var(--color-primary-500); color: #fff"
            >
              {{ submitting ? 'Đang lưu…' : selected.status === 'completed' ? '💾 Cập nhật' : '✅ Chấm bài' }}
            </button>
          </div>
        </div>
      </aside>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { teacherApi } from '@/api/teacher.js'

const route = useRoute()

const loading   = ref(false)
const submitting = ref(false)
const items      = ref([])
const selected   = ref(null)
const form       = ref({ score: 75, feedback: '' })

// Filters
const search       = ref('')
const statusFilter = ref(route.query.status || 'pending')
const typeFilter   = ref(route.query.type   || 'all')

// ── Helpers ────────────────────────────────────────────────────────────────
function fmtDate(iso) {
  if (!iso) return '—'
  return new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }).format(new Date(iso))
}

// ── Data ──────────────────────────────────────────────────────────────────
async function load() {
  loading.value = true
  selected.value = null
  try {
    const res = await teacherApi.getGradingQueue({ status: statusFilter.value, type: typeFilter.value })
    items.value = res.data?.data ?? res.data?.results ?? res.data ?? []
  } catch { items.value = [] }
  finally { loading.value = false }
}

const filteredItems = computed(() => {
  const q = search.value.toLowerCase().trim()
  if (!q) return items.value
  return items.value.filter(it =>
    it.student?.full_name?.toLowerCase().includes(q) ||
    it.student?.email?.toLowerCase().includes(q) ||
    it.exercise_title?.toLowerCase().includes(q)
  )
})

// ── Selection ─────────────────────────────────────────────────────────────
function select(item) {
  selected.value = item
  form.value = {
    score: item.ai_score ?? 75,
    feedback: (item.type === 'speaking' ? item.feedback_vi : item.feedback_text) ?? '',
  }
}

// ── Submit grade ──────────────────────────────────────────────────────────
async function submitGrade() {
  if (!selected.value) return
  submitting.value = true
  try {
    const payload = { score: form.value.score, feedback: form.value.feedback }
    if (selected.value.type === 'speaking') {
      await teacherApi.gradeSpeaking(selected.value.id, payload)
    } else {
      await teacherApi.gradeWriting(selected.value.id, payload)
    }
    // Update in-place
    const idx = items.value.findIndex(it => it.type === selected.value.type && it.id === selected.value.id)
    if (idx !== -1) {
      items.value[idx] = { ...items.value[idx], ai_score: form.value.score, status: 'completed' }
      selected.value = items.value[idx]
    }
  } catch { /* TODO: toast */ }
  finally { submitting.value = false }
}

watch([statusFilter, typeFilter], load)
onMounted(load)
</script>
