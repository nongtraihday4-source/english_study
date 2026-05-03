<template>
  <div class="p-6 max-w-4xl mx-auto min-h-screen">
    <h1 class="text-2xl font-bold mb-6" style="color: var(--color-text-base)">Quản lý hồ sơ</h1>

    <div v-if="!initialized" class="space-y-4">
      <div class="h-24 rounded-2xl animate-pulse" style="background-color: var(--color-surface-02)"></div>
      <div class="h-64 rounded-2xl animate-pulse" style="background-color: var(--color-surface-02)"></div>
    </div>

    <div v-else class="flex flex-col md:flex-row gap-6">
      
      <!-- LEFT SIDEBAR -->
      <div class="w-full md:w-64 shrink-0">
        <!-- Avatar Block -->
        <div class="rounded-2xl p-6 mb-4 flex flex-col items-center text-center shadow-sm"
             style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
          <div class="w-20 h-20 rounded-full flex items-center justify-center text-3xl font-black text-white mb-3"
               style="background: linear-gradient(135deg, #6366f1, #8b5cf6); box-shadow: 0 4px 14px rgba(99,102,241,0.3)">
            {{ auth.displayName?.[0]?.toUpperCase() || '?' }}
          </div>
          <h2 class="font-bold text-lg mb-1" style="color: var(--color-text-base)">{{ auth.displayName }}</h2>
          <div class="flex gap-2 justify-center mb-3">
            <span class="px-2 py-0.5 rounded text-xs font-bold"
                  style="background-color: var(--color-primary-600); color: white">
              {{ auth.user?.current_level || 'A1' }}
            </span>
            <span v-if="auth.isPremium" class="px-2 py-0.5 rounded text-xs font-bold flex items-center gap-1"
                  style="background: linear-gradient(135deg, #f59e0b, #fbbf24); color: #1a1400;">
              👑 Premium
            </span>
          </div>
          <p class="text-xs truncate w-full" style="color: var(--color-text-muted)">{{ auth.user?.email }}</p>
        </div>

        <!-- Navigation Tabs -->
        <nav class="flex flex-col gap-1">
          <button v-for="t in tabs" :key="t.id" @click="activeTab = t.id"
                  class="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition"
                  :class="activeTab === t.id ? 'active-tab' : 'inactive-tab'">
            <span>{{ t.icon }}</span> {{ t.label }}
          </button>
        </nav>
      </div>

      <!-- RIGHT CONTENT AREA -->
      <div class="flex-1 min-w-0">
        <!-- TAB 1: TỔNG QUAN -->
        <div v-if="activeTab === 'overview'" class="rounded-2xl p-6 shadow-sm"
             style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
          <h3 class="font-semibold text-lg mb-5 flex items-center gap-2" style="color: var(--color-text-base)">
            <span>👤</span> Thông tin cá nhân
          </h3>
          <form @submit.prevent="saveProfile" class="space-y-5">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-semibold mb-2 uppercase tracking-wider" style="color: var(--color-text-muted)">Họ</label>
                <input v-model="profileForm.last_name" class="w-full px-4 py-2.5 rounded-xl text-sm outline-none focus:ring-2 focus:ring-indigo-500 transition"
                       style="background-color: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)" />
              </div>
              <div>
                <label class="block text-xs font-semibold mb-2 uppercase tracking-wider" style="color: var(--color-text-muted)">Tên</label>
                <input v-model="profileForm.first_name" class="w-full px-4 py-2.5 rounded-xl text-sm outline-none focus:ring-2 focus:ring-indigo-500 transition"
                       style="background-color: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)" />
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold mb-2 uppercase tracking-wider" style="color: var(--color-text-muted)">Số điện thoại</label>
              <input v-model="profileForm.phone_number" type="tel" class="w-full px-4 py-2.5 rounded-xl text-sm outline-none focus:ring-2 focus:ring-indigo-500 transition"
                     style="background-color: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)" />
            </div>

            <div class="pt-2 flex items-center gap-4">
              <button type="submit" :disabled="saving"
                      class="px-6 py-2.5 rounded-xl font-semibold text-sm text-white transition hover:opacity-90 disabled:opacity-50"
                      style="background: linear-gradient(135deg, #4f46e5, #7c3aed)">
                {{ saving ? 'Đang lưu...' : 'Lưu thay đổi' }}
              </button>
              <Transition name="fade">
                <span v-if="saved" class="text-sm font-medium text-emerald-400">✓ Đã lưu thành công</span>
                <span v-else-if="saveError" class="text-sm font-medium text-red-400">⚠️ {{ saveError }}</span>
              </Transition>
            </div>
          </form>
        </div>

        <!-- TAB 2: BẢO MẬT -->
        <div v-else-if="activeTab === 'security'" class="space-y-6">
          
          <!-- Password Card -->
          <div class="rounded-2xl p-6 shadow-sm" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <h3 class="font-semibold text-lg mb-5 flex items-center gap-2" style="color: var(--color-text-base)">
              <span>🔑</span> Đổi mật khẩu
            </h3>
            <form @submit.prevent="changePassword" class="space-y-4 max-w-md">
              <div>
                <label class="block text-xs font-semibold mb-2 uppercase tracking-wider" style="color: var(--color-text-muted)">Mật khẩu hiện tại</label>
                <input v-model="pwdForm.old" type="password" required class="w-full px-4 py-2.5 rounded-xl text-sm outline-none focus:ring-2 focus:ring-indigo-500 transition"
                       style="background-color: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)" />
              </div>
              <div>
                <label class="block text-xs font-semibold mb-2 uppercase tracking-wider" style="color: var(--color-text-muted)">Mật khẩu mới</label>
                <input v-model="pwdForm.new" type="password" required class="w-full px-4 py-2.5 rounded-xl text-sm outline-none focus:ring-2 focus:ring-indigo-500 transition"
                       style="background-color: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)" />
              </div>
              <div class="pt-2">
                <button type="submit" :disabled="changingPwd"
                        class="px-6 py-2.5 rounded-xl font-semibold text-sm transition hover:opacity-90 disabled:opacity-50 text-white"
                        style="background: linear-gradient(135deg, #4f46e5, #7c3aed)">
                  {{ changingPwd ? 'Đang cập nhật...' : 'Cập nhật mật khẩu' }}
                </button>
              </div>
            </form>
          </div>

          <!-- 2FA Card -->
          <div class="rounded-2xl p-6 shadow-sm" style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
            <h3 class="font-semibold text-lg mb-2 flex items-center gap-2" style="color: var(--color-text-base)">
              <span>🛡️</span> Xác thực 2 bước (2FA)
            </h3>
            <p class="text-sm mb-5" style="color: var(--color-text-muted)">
              Bảo vệ tài khoản với một bước bổ sung khi đăng nhập qua ứng dụng như Google Authenticator.
            </p>
            
            <div class="flex items-center justify-between p-4 rounded-xl mb-4" style="background-color: var(--color-surface-03); border: 1px solid var(--color-surface-04)">
              <div>
                <p class="font-semibold" style="color: var(--color-text-base)">Trạng thái</p>
                <p class="text-sm" :class="is2FAEnabled ? 'text-emerald-400' : 'text-red-400'">
                  {{ is2FAEnabled ? 'Đang bật' : 'Chưa bật' }}
                </p>
              </div>
              <button v-if="!is2FAEnabled" @click="start2FASetup" class="px-5 py-2 rounded-lg text-sm font-semibold text-white transition hover:opacity-90"
                      style="background: linear-gradient(135deg, #059669, #10b981)">Bật 2FA</button>
              <button v-else @click="showDisable2FA = true" class="px-5 py-2 rounded-lg text-sm font-semibold transition border"
                      style="color: #ef4444; border-color: #ef4444; background: transparent;">Tắt 2FA</button>
            </div>

            <!-- Setup 2FA Flow -->
            <div v-if="setup2FAData" class="mt-6 border-t pt-6" style="border-color: var(--color-surface-04);">
              <h4 class="font-semibold mb-3">Cài đặt 2FA</h4>
              <p class="text-sm mb-4" style="color: var(--color-text-soft)">1. Quét mã QR dưới đây bằng Google Authenticator hoặc Authy.</p>
              <div class="bg-white p-2 rounded-xl inline-block mb-4">
                <img :src="setup2FAData.qr_code" alt="QR Code" class="w-40 h-40" />
              </div>
              <p class="text-sm mb-2" style="color: var(--color-text-soft)">Bí mật (Secret Key): <code class="px-2 py-1 rounded" style="background-color: var(--color-surface-03)">{{ setup2FAData.secret }}</code></p>
              
              <p class="text-sm mt-4 mb-2" style="color: var(--color-text-soft)">2. Nhập mã gồm 6 chữ số từ ứng dụng:</p>
              <div class="flex gap-2 max-w-xs">
                <input v-model="otpInput" type="text" maxlength="6" class="w-full px-4 py-2.5 rounded-xl text-center font-mono tracking-widest outline-none focus:ring-2 focus:ring-indigo-500 transition"
                       style="background-color: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)" />
                <button @click="verify2FASetup" :disabled="!otpInput || otpInput.length < 6" class="px-5 py-2.5 rounded-xl text-white font-semibold disabled:opacity-50"
                        style="background: linear-gradient(135deg, #059669, #10b981)">Xác nhận</button>
              </div>
            </div>

            <!-- Disable 2FA Modal style inline -->
            <div v-if="showDisable2FA" class="mt-4 p-4 rounded-xl border" style="background-color: rgba(239,68,68,0.05); border-color: rgba(239,68,68,0.3)">
              <h4 class="font-semibold mb-2 text-red-400">Tắt xác thực 2 bước</h4>
              <p class="text-sm mb-3" style="color: var(--color-text-muted)">Vui lòng nhập mật khẩu để tiếp tục.</p>
              <div class="flex gap-2 max-w-sm">
                <input v-model="disablePwd" type="password" class="w-full px-3 py-2 rounded-lg text-sm outline-none border"
                       style="background-color: var(--color-surface-04); color: white; border-color: var(--color-surface-04)" />
                <button @click="confirmDisable2FA" class="px-4 py-2 rounded-lg text-white text-sm font-semibold"
                        style="background: linear-gradient(135deg, #ef4444, #dc2626)">Xác nhận tắt</button>
              </div>
            </div>
            
          </div>
        </div>

        <!-- TAB 3: THIẾT BỊ -->
        <div v-else-if="activeTab === 'devices'" class="rounded-2xl p-6 shadow-sm"
             style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
          <h3 class="font-semibold text-lg flex items-center gap-2 mb-1" style="color: var(--color-text-base)">
            <span>💻</span> Lịch sử đăng nhập
          </h3>
          <p class="text-sm mb-6" style="color: var(--color-text-muted)">Quản lý các thiết bị đang đăng nhập vào tài khoản của bạn.</p>
          
          <div v-if="loadingDevices" class="text-center text-sm py-4">Đang tải...</div>
          <div v-else-if="displayDevices.length === 0" class="text-center text-sm py-4">Không có thiết bị khả dụng.</div>
          <div v-else class="space-y-4">
            <div v-for="d in displayDevices" :key="d.id" class="flex items-center justify-between p-4 rounded-xl"
                 style="background-color: var(--color-surface-03); border: 1px solid var(--color-surface-04)">
              <div>
                <p class="font-medium text-sm mb-0.5" style="color: var(--color-text-base)">{{ d.device_name || 'Không rõ thiết bị' }}</p>
                <p class="text-xs" style="color: var(--color-text-muted)">
                   IP: {{ d.ip_address }} · Hoạt động: {{ new Date(d.created_at).toLocaleString('vi-VN') }}
                </p>
              </div>
              <div class="flex items-center gap-2">
              <button
                v-if="d.canRevoke"
                @click="revokeDevice(d.id)"
                :disabled="revokingId === d.id"
                class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition"
                :class="revokingId === d.id
                  ? 'opacity-60 cursor-not-allowed text-yellow-400 border-yellow-500'
                  : 'text-red-400 border-red-500 hover:bg-red-500 hover:text-white'"
              >
                {{ revokingId === d.id ? '...' : 'Đăng xuất' }}
              </button>
              <span v-if="revokedIds.has(d.id)" class="text-xs font-semibold text-emerald-400">✓ Đã đăng xuất</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { authApi } from '@/api/auth.js'

const auth = useAuthStore()
const initialized = ref(false)

const tabs = [
  { id: 'overview', label: 'Tổng quan', icon: '👤' },
  { id: 'security', label: 'Bảo mật', icon: '🛡️' },
  { id: 'devices', label: 'Thiết bị & Lịch sử', icon: '💻' }
]
const activeTab = ref('overview')

// --- Overview Tab ---
const profileForm = reactive({ first_name: '', last_name: '', phone_number: '' })
const saving = ref(false)
const saved = ref(false)
const saveError = ref('')

watch(() => auth.user, (u) => {
  if (u) {
    profileForm.first_name = u.first_name || ''
    profileForm.last_name = u.last_name || ''
    profileForm.phone_number = u.phone_number || ''
    initialized.value = true
  }
}, { immediate: true, deep: true })

onMounted(async () => {
  await auth.refreshUser()
  // Ensure profileForm is synced after refresh immediately
  if (auth.user) {
    profileForm.first_name = auth.user.first_name || ''
    profileForm.last_name = auth.user.last_name || ''
    profileForm.phone_number = auth.user.phone_number || ''
  }
  initialized.value = true
})
async function saveProfile() {
  saving.value = true
  saved.value = false
  saveError.value = ''
  try {
    await authApi.updateMe({
      first_name: profileForm.first_name,
      last_name: profileForm.last_name,
      profile: { phone: profileForm.phone_number },
    })
    await auth.refreshUser()
    if (auth.user) {
       profileForm.phone_number = auth.user.phone_number || profileForm.phone_number
    }
    saved.value = true
    setTimeout(() => saved.value = false, 3000)
  } catch (e) {
    console.error(e)
    saveError.value = 'Không thể lưu. Vui lòng kiểm tra lại.'
  } finally {
    saving.value = false
  }
}

// --- Security Tab ---
// Password Change
const pwdForm = reactive({ old: '', new: '' })
const changingPwd = ref(false)
async function changePassword() {
  changingPwd.value = true
  try {
    await authApi.changePassword(pwdForm.old, pwdForm.new)
    pwdForm.old = ''
    pwdForm.new = ''
    alert('Đổi mật khẩu thành công. Vui lòng đăng nhập lại.')
    await auth.logout()
    window.location.href = '/login'
  } catch (e) {
    alert(e.response?.data?.old_password?.[0] || e.response?.data?.new_password?.[0] || 'Lỗi khi đổi mật khẩu.')
  } finally {
    changingPwd.value = false
  }
}

// 2FA Management
const is2FAEnabled = ref(false)
const setup2FAData = ref(null)
const otpInput = ref('')
const showDisable2FA = ref(false)
const disablePwd = ref('')

watch(() => auth.user, (u) => {
  if (u && u.settings) is2FAEnabled.value = u.settings.is_2fa_enabled
}, { immediate: true })

async function start2FASetup() {
  try {
    const res = await authApi.generate2FA()
    setup2FAData.value = res.data?.data || res.data
  } catch (e) {
    alert('Lỗi tạo mã QR. Vui lòng thử lại.')
  }
}

async function verify2FASetup() {
  if (!otpInput.value) return
  try {
    await authApi.verify2FA(otpInput.value)
    is2FAEnabled.value = true
    setup2FAData.value = null
    otpInput.value = ''
    auth.refreshUser()
    alert('Bật tính năng bảo mật 2 lớp thành công!')
  } catch (e) {
    alert('Mã OTP không đúng hoặc đã hết hạn.')
  }
}

async function confirmDisable2FA() {
  try {
    await authApi.disable2FA(disablePwd.value)
    is2FAEnabled.value = false
    showDisable2FA.value = false
    disablePwd.value = ''
    auth.refreshUser()
    alert('Đã tắt bảo mật 2 lớp.')
  } catch (e) {
    alert('Mật khẩu không hợp lệ.')
  }
}

// --- Devices Tab ---
const devices = ref([])
const loadingDevices = ref(false)

const displayDevices = computed(() => {
  const grouped = {}
  devices.value.forEach(d => {
    const key = `${d.ip_address}|${d.device_name}`
    if (!grouped[key]) grouped[key] = []
    grouped[key].push(d)
  })

  let result = []
  for (const key in grouped) {
    const group = grouped[key]
    // Giữ tối đa 5 lần truy cập gần nhất. 
    // Các bản ghi cũ hơn giữ lại bị bỏ qua để tránh rác list. 
    const top5 = group.slice(0, 5)
    top5.forEach((item, index) => {
      result.push({
        ...item,
        // Chỉ nút đăng xuất cho device mới nhất của group này
        canRevoke: index === 0 
      })
    })
  }
  
  // Sort lại toàn bộ kết quả theo thời gian mới nhất lên đầu
  return result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

async function loadDevices() {
  loadingDevices.value = true
  try {
    const res = await authApi.getDevices()
    const rd = res.data?.data || res.data || {}
    devices.value = Array.isArray(rd) ? rd : (rd.results || [])
  } catch (e) {
    console.error(e)
  } finally {
    loadingDevices.value = false
  }
}
const revokingId = ref(null)
const revokedIds = ref(new Set())

async function revokeDevice(id) {
  if (!confirm('Bạn có chắc muốn đăng xuất phiên đăng nhập này không?')) return
  revokingId.value = id
  try {
    await authApi.revokeDevice(id)
    revokedIds.value = new Set([...revokedIds.value, id])

    // Gọi API trực tiếp (KHÔNG qua loadDevices) để 403 không bị nuốt bên trong
    try {
      const res = await authApi.getDevices()
      const rd = res.data?.data || res.data || {}
      devices.value = Array.isArray(rd) ? rd : (rd.results || [])
    } catch (loadErr) {
      const status = loadErr?.response?.status
      if (status === 403 || status === 401) {
        // Phiên hiện tại bị revoke → logout + chuyển về trang đăng nhập
        await auth.logout()
        window.location.href = '/login'
        return
      }
      // Lỗi khác (network, server 500...) — bỏ qua, list sẽ hiển thị lần load trước
      console.error('loadDevices after revoke failed:', loadErr)
    }
  } catch (e) {
    console.error(e)
    if (e?.response?.status === 403 || e?.response?.status === 401) {
      await auth.logout()
      window.location.href = '/login'
      return
    }
    alert('Lỗi khi đăng xuất thiết bị. Vui lòng thử lại.')
  } finally {
    revokingId.value = null
  }
}

watch(activeTab, (val) => {
  if (val === 'devices' && devices.value.length === 0) loadDevices()
})
</script>

<style scoped>
.active-tab {
  background-color: var(--color-surface-03);
  color: var(--color-primary-400);
  border-left: 3px solid var(--color-primary-500);
}
.inactive-tab {
  color: var(--color-text-muted);
  border-left: 3px solid transparent;
}
.inactive-tab:hover {
  background-color: var(--color-surface-03);
  color: var(--color-text-base);
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
