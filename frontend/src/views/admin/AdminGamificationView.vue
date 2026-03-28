<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-xl font-bold" style="color: var(--color-text-base)">Gamification</h2>
      <p class="text-sm mt-0.5" style="color: var(--color-text-muted)">Thành tích, chứng chỉ và điểm XP</p>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 p-1 rounded-xl w-fit" style="background-color:var(--color-surface-02)">
      <button v-for="tab in TABS" :key="tab.key" @click="activeTab = tab.key"
        class="px-4 py-2 text-sm rounded-lg font-medium transition-all"
        :style="activeTab === tab.key ? 'background-color:var(--color-primary-500);color:#fff' : 'color:var(--color-text-muted)'">
        {{ tab.label }}
      </button>
    </div>

    <!-- ── Achievements ───────────────────────────────────────────── -->
    <section v-if="activeTab === 'achievements'">
      <div class="flex items-center justify-between mb-4">
        <span class="text-sm font-semibold" style="color:var(--color-text-base)">Danh sách thành tích</span>
        <button @click="openAchievModal(null)" class="btn-primary text-sm px-4 py-2 rounded-lg">+ Thêm</button>
      </div>
      <div v-if="achLoading" class="space-y-2">
        <div v-for="n in 4" :key="n" class="h-14 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
      </div>
      <div v-else class="rounded-2xl overflow-hidden" style="background-color:var(--color-surface-02)">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b" style="border-color:var(--color-border);color:var(--color-text-muted)">
              <th class="px-4 py-3">Icon</th>
              <th class="px-4 py-3">Tên</th>
              <th class="px-4 py-3">Danh mục</th>
              <th class="px-4 py-3">Điều kiện</th>
              <th class="px-4 py-3">XP</th>
              <th class="px-4 py-3">Trạng thái</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in achievements" :key="a.id" class="border-b last:border-0" style="border-color:var(--color-border)">
              <td class="px-4 py-3 text-xl">{{ a.icon_emoji }}</td>
              <td class="px-4 py-3 font-medium" style="color:var(--color-text-base)">{{ a.name_vi || a.name }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ a.category }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ a.condition_type }} ≥ {{ a.threshold_value }}</td>
              <td class="px-4 py-3 text-xs font-medium" style="color:var(--color-primary-500)">+{{ a.xp_reward }} XP</td>
              <td class="px-4 py-3">
                <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                  :style="a.is_active ? 'background:#dcfce7;color:#166534' : 'background:#f3f4f6;color:#6b7280'">
                  {{ a.is_active ? 'Hoạt động' : 'Ẩn' }}
                </span>
              </td>
              <td class="px-4 py-3 flex gap-2">
                <button @click="openAchievModal(a)" class="text-xs px-3 py-1 rounded-lg" style="background-color:var(--color-surface-03);color:var(--color-text-base)">Sửa</button>
                <button @click="deleteAchievement(a)" class="text-xs px-3 py-1 rounded-lg text-red-500" style="background-color:var(--color-surface-03)">Xoá</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- ── Certificates ───────────────────────────────────────────── -->
    <section v-if="activeTab === 'certificates'">
      <div class="flex flex-wrap gap-3 mb-4">
        <input v-model="certSearch" @input="loadCertificates" placeholder="Email người dùng..." class="input-sm" />
        <select v-model="certValid" @change="loadCertificates" class="input-sm">
          <option value="">Tất cả</option>
          <option value="true">Hợp lệ</option>
          <option value="false">Không hợp lệ</option>
        </select>
      </div>
      <div v-if="certLoading" class="space-y-2">
        <div v-for="n in 5" :key="n" class="h-12 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
      </div>
      <div v-else class="rounded-2xl overflow-x-auto" style="background-color:var(--color-surface-02)">
        <table class="w-full text-sm min-w-[560px]">
          <thead>
            <tr class="text-left border-b" style="border-color:var(--color-border);color:var(--color-text-muted)">
              <th class="px-4 py-3">Người dùng</th>
              <th class="px-4 py-3">Khoá học / Cấp độ</th>
              <th class="px-4 py-3">Mã xác nhận</th>
              <th class="px-4 py-3">Ngày cấp</th>
              <th class="px-4 py-3">Hợp lệ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in certificates" :key="c.id" class="border-b last:border-0" style="border-color:var(--color-border)">
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-base)">{{ c.user_email }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ c.course_title || c.level_code || '—' }}</td>
              <td class="px-4 py-3 text-xs font-mono" style="color:var(--color-text-muted)">{{ c.verification_code }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ fmtDate(c.issued_at) }}</td>
              <td class="px-4 py-3">
                <span class="text-xs px-2 py-0.5 rounded-full"
                  :style="c.is_valid ? 'background:#dcfce7;color:#166534' : 'background:#fee2e2;color:#991b1b'">
                  {{ c.is_valid ? 'Hợp lệ' : 'Vô hiệu' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <PaginationBar :pagination="certPagination" @change="loadCertPage" />
      </div>
    </section>

    <!-- ── XP Log ──────────────────────────────────────────────────── -->
    <section v-if="activeTab === 'xp'">
      <div class="flex flex-wrap gap-3 items-end mb-4">
        <input v-model="xpSearch" @input="loadXP" placeholder="Email người dùng..." class="input-sm" />
        <button @click="grantModal.open = true" class="btn-primary text-sm px-4 py-2 rounded-lg">+ Cộng XP thủ công</button>
      </div>
      <div v-if="xpLoading" class="space-y-2">
        <div v-for="n in 5" :key="n" class="h-12 animate-pulse rounded-xl" style="background-color:var(--color-surface-02)" />
      </div>
      <div v-else class="rounded-2xl overflow-x-auto" style="background-color:var(--color-surface-02)">
        <table class="w-full text-sm min-w-[480px]">
          <thead>
            <tr class="text-left border-b" style="border-color:var(--color-border);color:var(--color-text-muted)">
              <th class="px-4 py-3">Người dùng</th>
              <th class="px-4 py-3">Nguồn</th>
              <th class="px-4 py-3">XP</th>
              <th class="px-4 py-3">Thời gian</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="x in xpLog" :key="x.id" class="border-b last:border-0" style="border-color:var(--color-border)">
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-base)">{{ x.user_email }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ x.source }}</td>
              <td class="px-4 py-3 text-xs font-medium" style="color:var(--color-primary-500)">+{{ x.amount }}</td>
              <td class="px-4 py-3 text-xs" style="color:var(--color-text-muted)">{{ fmtDate(x.created_at) }}</td>
            </tr>
          </tbody>
        </table>
        <PaginationBar :pagination="xpPagination" @change="loadXPPage" />
      </div>
    </section>

    <!-- ── Achievement Modal ──────────────────────────────────────── -->
    <div v-if="achModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="w-full max-w-md rounded-2xl p-6 space-y-4" style="background-color:var(--color-surface-01)">
        <h3 class="text-base font-bold" style="color:var(--color-text-base)">
          {{ achModal.item ? 'Sửa thành tích' : 'Thêm thành tích' }}
        </h3>
        <div class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <input v-model="achForm.name" placeholder="Tên (EN)*" class="input-base" />
            <input v-model="achForm.name_vi" placeholder="Tên (VI)*" class="input-base" />
          </div>
          <textarea v-model="achForm.description" placeholder="Mô tả" rows="2" class="input-base w-full resize-none" />
          <div class="grid grid-cols-2 gap-3">
            <input v-model="achForm.icon_emoji" placeholder="Icon emoji 🏆" class="input-base" />
            <input v-model="achForm.category" placeholder="Danh mục" class="input-base" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <input v-model="achForm.condition_type" placeholder="condition_type" class="input-base" />
            <input v-model.number="achForm.threshold_value" type="number" placeholder="Ngưỡng" class="input-base" />
          </div>
          <input v-model.number="achForm.xp_reward" type="number" placeholder="XP thưởng" class="input-base w-full" />
          <label class="flex items-center gap-2 text-sm" style="color:var(--color-text-muted)">
            <input type="checkbox" v-model="achForm.is_active" />
            Kích hoạt
          </label>
        </div>
        <div class="flex gap-3 justify-end">
          <button @click="achModal.open = false" class="text-sm px-4 py-2 rounded-lg" style="background-color:var(--color-surface-02);color:var(--color-text-base)">Huỷ</button>
          <button @click="saveAchievement" :disabled="achSaving" class="btn-primary text-sm px-4 py-2 rounded-lg">
            {{ achSaving ? '...' : 'Lưu' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Grant XP Modal ──────────────────────────────────────────── -->
    <div v-if="grantModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="w-full max-w-sm rounded-2xl p-6 space-y-4" style="background-color:var(--color-surface-01)">
        <h3 class="text-base font-bold" style="color:var(--color-text-base)">Cộng XP thủ công</h3>
        <div class="space-y-3">
          <input v-model.number="grantForm.user_id" type="number" placeholder="User ID*" class="input-base w-full" />
          <input v-model.number="grantForm.amount" type="number" placeholder="Số XP*" class="input-base w-full" />
          <input v-model="grantForm.description" placeholder="Lý do" class="input-base w-full" />
        </div>
        <div class="flex gap-3 justify-end">
          <button @click="grantModal.open = false" class="text-sm px-4 py-2 rounded-lg" style="background-color:var(--color-surface-02);color:var(--color-text-base)">Huỷ</button>
          <button @click="doGrant" :disabled="grantSaving" class="btn-primary text-sm px-4 py-2 rounded-lg">
            {{ grantSaving ? '...' : 'Cộng XP' }}
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
  { key: 'achievements', label: 'Thành tích' },
  { key: 'certificates', label: 'Chứng chỉ' },
  { key: 'xp', label: 'XP Log' },
]
const activeTab = ref('achievements')

const achievements = ref([])
const achLoading = ref(false)
const achModal = reactive({ open: false, item: null })
const achForm = reactive({ name: '', name_vi: '', description: '', icon_emoji: '🏆', category: '', condition_type: '', threshold_value: 1, xp_reward: 0, is_active: true })
const achSaving = ref(false)

const certificates = ref([])
const certLoading = ref(false)
const certSearch = ref('')
const certValid = ref('')
const certPagination = reactive({ count: 0, next: null, previous: null, page: 1 })

const xpLog = ref([])
const xpLoading = ref(false)
const xpSearch = ref('')
const xpPagination = reactive({ count: 0, next: null, previous: null, page: 1 })
const grantModal = reactive({ open: false })
const grantForm = reactive({ user_id: null, amount: 0, description: '' })
const grantSaving = ref(false)

watch(activeTab, (tab) => {
  if (tab === 'certificates' && certificates.value.length === 0) loadCertificates()
  if (tab === 'xp' && xpLog.value.length === 0) loadXP()
})

onMounted(() => loadAchievements())

async function loadAchievements() {
  achLoading.value = true
  try { const r = await adminApi.getAchievements(); achievements.value = r.data.results ?? r.data }
  finally { achLoading.value = false }
}
async function loadCertificates(page = 1) {
  certLoading.value = true
  try {
    const r = await adminApi.getCertificates({ search: certSearch.value || undefined, is_valid: certValid.value || undefined, page })
    certificates.value = r.data.results ?? r.data
    Object.assign(certPagination, { count: r.data.count, next: r.data.next, previous: r.data.previous, page })
  } finally { certLoading.value = false }
}
function loadCertPage(p) { loadCertificates(p) }

async function loadXP(page = 1) {
  xpLoading.value = true
  try {
    const r = await adminApi.getXPLog({ search: xpSearch.value || undefined, page })
    xpLog.value = r.data.results ?? r.data
    Object.assign(xpPagination, { count: r.data.count, next: r.data.next, previous: r.data.previous, page })
  } finally { xpLoading.value = false }
}
function loadXPPage(p) { loadXP(p) }

function openAchievModal(item) {
  achModal.item = item
  if (item) Object.assign(achForm, { name: item.name, name_vi: item.name_vi ?? '', description: item.description ?? '', icon_emoji: item.icon_emoji ?? '🏆', category: item.category ?? '', condition_type: item.condition_type ?? '', threshold_value: item.threshold_value, xp_reward: item.xp_reward, is_active: item.is_active })
  else Object.assign(achForm, { name: '', name_vi: '', description: '', icon_emoji: '🏆', category: '', condition_type: '', threshold_value: 1, xp_reward: 0, is_active: true })
  achModal.open = true
}
async function saveAchievement() {
  achSaving.value = true
  try {
    if (achModal.item) await adminApi.updateAchievement(achModal.item.id, achForm)
    else await adminApi.createAchievement(achForm)
    achModal.open = false
    await loadAchievements()
  } finally { achSaving.value = false }
}
async function deleteAchievement(a) {
  if (!confirm(`Xoá thành tích "${a.name}"?`)) return
  await adminApi.deleteAchievement(a.id)
  await loadAchievements()
}
async function doGrant() {
  grantSaving.value = true
  try {
    await adminApi.grantXP(grantForm)
    grantModal.open = false
    await loadXP()
  } finally { grantSaving.value = false }
}

function fmtDate(d) { return d ? new Date(d).toLocaleDateString('vi-VN') : '—' }
</script>
