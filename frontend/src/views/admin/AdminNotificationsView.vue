<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-xl font-bold" style="color: var(--color-text-base)">Thông báo</h2>
      <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">Mẫu thông báo, phát tin và lịch sử</p>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 p-1 rounded-xl w-fit" style="background-color:var(--color-surface-02)">
      <button v-for="tab in TABS" :key="tab.key" @click="activeTab = tab.key"
        class="px-4 py-2 text-sm rounded-lg font-medium transition-all"
        :style="activeTab === tab.key ? 'background-color:var(--color-primary-500);color:#fff' : 'color:var(--color-text-muted)'">
        {{ tab.label }}
      </button>
    </div>

    <!-- ── Templates ─────────────────────────────────────────────── -->
    <section v-if="activeTab === 'templates'">
      <div v-if="tplLoading" class="space-y-3">
        <div v-for="n in 4" :key="n" class="h-16 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
      </div>
      <div v-else class="space-y-4">
        <div v-for="tpl in templates" :key="tpl.notification_type"
          class="rounded-2xl p-4" style="background-color:var(--color-surface-02)">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="font-medium text-sm" style="color:var(--color-text-base)">{{ tpl.notification_type }}</div>
              <div class="text-xs mt-1" style="color:var(--color-text-muted)">{{ tpl.title_vi }}</div>
              <div class="text-xs mt-1 line-clamp-2" style="color:var(--color-text-muted)">{{ tpl.message_template_vi }}</div>
              <div class="flex gap-3 mt-2">
                <span class="text-xs" :style="tpl.push_enabled ? 'color:#166534' : 'color:#9ca3af'">
                  📱 Push {{ tpl.push_enabled ? 'bật' : 'tắt' }}
                </span>
                <span class="text-xs" :style="tpl.email_enabled ? 'color:#166534' : 'color:#9ca3af'">
                  📧 Email {{ tpl.email_enabled ? 'bật' : 'tắt' }}
                </span>
              </div>
            </div>
            <button @click="openTplModal(tpl)" class="text-xs px-3 py-1.5 rounded-lg shrink-0"
              style="background-color:var(--color-surface-03);color:var(--color-text-base)">Sửa</button>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Broadcast ──────────────────────────────────────────────── -->
    <section v-if="activeTab === 'broadcast'" class="max-w-xl">
      <div class="rounded-2xl p-6 space-y-4" style="background-color:var(--color-surface-02)">
        <h3 class="text-sm font-semibold" style="color:var(--color-text-base)">Phát thông báo hàng loạt</h3>
        <div class="space-y-3">
          <div>
            <label class="text-xs mb-1 block" style="color:var(--color-text-muted)">Đối tượng</label>
            <select v-model="broadcastForm.target" class="input-base w-full">
              <option value="all">Tất cả người dùng</option>
              <option value="premium">Người dùng Premium</option>
              <option value="free">Người dùng Free</option>
            </select>
          </div>
          <div>
            <label class="text-xs mb-1 block" style="color:var(--color-text-muted)">Tiêu đề *</label>
            <input v-model="broadcastForm.title" placeholder="Nhập tiêu đề thông báo" class="input-base w-full" />
          </div>
          <div>
            <label class="text-xs mb-1 block" style="color:var(--color-text-muted)">Nội dung *</label>
            <textarea v-model="broadcastForm.message" placeholder="Nhập nội dung thông báo" rows="4" class="input-base w-full resize-none" />
          </div>
        </div>
        <button @click="doBroadcast" :disabled="broadcastSending"
          class="btn-primary text-sm px-6 py-2.5 rounded-lg w-full font-medium">
          {{ broadcastSending ? 'Đang gửi...' : '📤 Gửi thông báo' }}
        </button>
        <div v-if="broadcastResult" class="text-sm rounded-xl px-4 py-3" style="background-color:var(--color-surface-03);color:var(--color-text-base)">
          {{ broadcastResult }}
        </div>
      </div>
    </section>

    <!-- ── History ────────────────────────────────────────────────── -->
    <section v-if="activeTab === 'history'">
      <div class="flex flex-wrap gap-3 mb-4">
        <input v-model="histSearch" @input="loadHistory" placeholder="Email / tiêu đề..." class="input-sm" />
        <select v-model="histType" @change="loadHistory" class="input-sm">
          <option value="">Tất cả loại</option>
          <option value="system_announcement">system_announcement</option>
          <option value="lesson_reminder">lesson_reminder</option>
          <option value="achievement_unlocked">achievement_unlocked</option>
        </select>
      </div>
      <div v-if="histLoading" class="space-y-2">
        <div v-for="n in 5" :key="n" class="h-12 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
      </div>
      <div v-else class="rounded-2xl overflow-x-auto" style="background-color:var(--color-surface-02)">
        <table class="w-full text-sm min-w-[560px]">
          <thead>
            <tr class="text-left border-b" style="border-color:var(--color-border);color:var(--color-text-muted)">
              <th class="px-4 py-3">Người nhận</th>
              <th class="px-4 py-3">Tiêu đề</th>
              <th class="px-4 py-3">Loại</th>
              <th class="px-4 py-3">Đã đọc</th>
              <th class="px-4 py-3">Thời gian</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="h in history" :key="h.id" class="border-b last:border-0" style="border-color:var(--color-border)">
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-base)">{{ h.user_email }}</td>
              <td class="px-4 py-3 text-xs font-medium" style="color:var(--color-text-base)">{{ h.title }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ h.notification_type }}</td>
              <td class="px-4 py-3">
                <span class="text-xs">{{ h.is_read ? '✅' : '○' }}</span>
              </td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ fmtDate(h.created_at) }}</td>
            </tr>
          </tbody>
        </table>
        <PaginationBar :pagination="histPagination" @change="loadHistoryPage" />
      </div>
    </section>

    <!-- ── Template Edit Modal ───────────────────────────────────── -->
    <div v-if="tplModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="w-full max-w-lg rounded-2xl p-6 space-y-4" style="background-color:var(--color-surface-01)">
        <h3 class="text-base font-bold" style="color:var(--color-text-base)">
          Sửa mẫu: {{ tplModal.item?.notification_type }}
        </h3>
        <div class="space-y-3">
          <div>
            <label class="text-xs mb-1 block" style="color:var(--color-text-muted)">Tiêu đề (VI)</label>
            <input v-model="tplForm.title_vi" class="input-base w-full" />
          </div>
          <div>
            <label class="text-xs mb-1 block" style="color:var(--color-text-muted)">Mẫu nội dung (VI)</label>
            <textarea v-model="tplForm.message_template_vi" rows="4" class="input-base w-full resize-none" />
          </div>
          <div class="flex gap-6">
            <label class="flex items-center gap-2 text-sm" style="color:var(--color-text-muted)">
              <input type="checkbox" v-model="tplForm.push_enabled" />
              Push notification
            </label>
            <label class="flex items-center gap-2 text-sm" style="color:var(--color-text-muted)">
              <input type="checkbox" v-model="tplForm.email_enabled" />
              Email
            </label>
          </div>
        </div>
        <div class="flex gap-3 justify-end">
          <button @click="tplModal.open = false" class="text-sm px-4 py-2 rounded-lg" style="background-color:var(--color-surface-02);color:var(--color-text-base)">Huỷ</button>
          <button @click="saveTpl" :disabled="tplSaving" class="btn-primary text-sm px-4 py-2 rounded-lg">
            {{ tplSaving ? '...' : 'Lưu' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { adminApi } from '@/api/admin.js'
import PaginationBar from '@/components/PaginationBar.vue'

const TABS = [
  { key: 'templates', label: 'Mẫu thông báo' },
  { key: 'broadcast', label: 'Phát tin' },
  { key: 'history', label: 'Lịch sử' },
]
const activeTab = ref('templates')

const templates = ref([])
const tplLoading = ref(false)
const tplModal = reactive({ open: false, item: null })
const tplForm = reactive({ title_vi: '', message_template_vi: '', push_enabled: true, email_enabled: false })
const tplSaving = ref(false)

const broadcastForm = reactive({ target: 'all', title: '', message: '' })
const broadcastSending = ref(false)
const broadcastResult = ref('')

const history = ref([])
const histLoading = ref(false)
const histSearch = ref('')
const histType = ref('')
const histPagination = reactive({ count: 0, next: null, previous: null, page: 1 })

watch(activeTab, (tab) => {
  if (tab === 'history' && history.value.length === 0) loadHistory()
})

onMounted(() => loadTemplates())

async function loadTemplates() {
  tplLoading.value = true
  try { const r = await adminApi.getNotificationTemplates(); templates.value = r.data.results ?? r.data }
  finally { tplLoading.value = false }
}

function openTplModal(item) {
  tplModal.item = item
  Object.assign(tplForm, { title_vi: item.title_vi, message_template_vi: item.message_template_vi, push_enabled: item.push_enabled, email_enabled: item.email_enabled })
  tplModal.open = true
}
async function saveTpl() {
  tplSaving.value = true
  try {
    await adminApi.updateNotificationTemplate(tplModal.item.notification_type, tplForm)
    tplModal.open = false
    await loadTemplates()
  } finally { tplSaving.value = false }
}

async function doBroadcast() {
  if (!broadcastForm.title || !broadcastForm.message) return
  broadcastSending.value = true
  broadcastResult.value = ''
  try {
    const r = await adminApi.broadcastNotification(broadcastForm)
    broadcastResult.value = r.data.detail
    broadcastForm.title = ''
    broadcastForm.message = ''
  } finally { broadcastSending.value = false }
}

async function loadHistory(page = 1) {
  histLoading.value = true
  try {
    const r = await adminApi.getNotificationHistory({ search: histSearch.value || undefined, notification_type: histType.value || undefined, page })
    history.value = r.data.results ?? r.data
    Object.assign(histPagination, { count: r.data.count, next: r.data.next, previous: r.data.previous, page })
  } finally { histLoading.value = false }
}
function loadHistoryPage(p) { loadHistory(p) }

function fmtDate(d) { return d ? new Date(d).toLocaleString('vi-VN') : '—' }
</script>
