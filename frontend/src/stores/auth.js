import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)          // { id, email, full_name, role, account_type, current_level }
  const loading = ref(false)
  const initialized = ref(false)  // true after first getMe attempt

  const isLoggedIn = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isTeacher = computed(() => user.value?.role === 'teacher' || user.value?.role === 'admin')
  const isPremium = computed(() => user.value?.account_type === 'premium')
  const displayName = computed(() =>
    user.value ? (user.value.full_name || user.value.email) : ''
  )

  /** Map a UserMeSerializer response object to the user store shape. */
  function _mapMeData(raw) {
    const fn = raw.first_name || ''
    const ln = raw.last_name || ''
    return {
      id: raw.id,
      email: raw.email,
      first_name: fn,
      last_name: ln,
      full_name: `${fn} ${ln}`.trim() || raw.email || '',
      role: raw.role,
      account_type: raw.account_type,
      current_level: raw.current_level,
      target_level: raw.target_level,
      profile: raw.profile,
      settings: raw.settings,
      phone_number: raw.profile?.phone || raw.profile?.phone_number || '',
    }
  }

  /**
   * Called once on app boot — re-hydrates session from HttpOnly cookie.
   */
  async function init() {
    if (initialized.value) return
    try {
      const res = await authApi.getMe()
      // VNNumberJSONRenderer wraps: { success: true, data: <payload> }
      const raw = res.data?.data ?? res.data
      user.value = _mapMeData(raw)
    } catch {
      user.value = null
    } finally {
      initialized.value = true
    }
  }

  /** Re-fetches user profile without the `initialized` guard (e.g. after profile update). */
  async function refreshUser() {
    try {
      const res = await authApi.getMe()
      const raw = res.data?.data ?? res.data
      user.value = _mapMeData(raw)
    } catch { /* ignore — user stays as-is */ }
  }

  async function login(email, password, otpCode) {
    loading.value = true
    try {
      const res = await authApi.login(email, password, otpCode)
      // VNNumberJSONRenderer wraps: { success: true, data: { message, user } }
      const payload = res.data?.data ?? res.data
      const u = payload.user ?? payload
      user.value = {
        id: u.id,
        email: u.email,
        first_name: u.first_name || '',
        last_name: u.last_name || '',
        full_name: u.full_name || `${u.first_name || ''} ${u.last_name || ''}`.trim() || u.email || '',
        role: u.role,
        account_type: u.account_type,
        current_level: u.current_level,
      }
      return { success: true }
    } catch (err) {
      const respData = err.response?.data || {}
      if (respData.requires_2fa || respData.errors?.requires_2fa) {
        const msg = respData.errors?.detail?.[0] || respData.detail || "Tài khoản được bảo vệ bởi 2FA. Vui lòng nhập mã OTP."
        return { success: false, requires2FA: true, message: msg }
      }
      const msg = respData.detail || respData.message || respData.errors?.otp_code?.[0] || 'Đăng nhập thất bại.'
      return { success: false, message: msg }
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try { await authApi.logout() } catch { /* ignore */ }
    user.value = null
    initialized.value = false
  }

  async function register(payload) {
    loading.value = true
    try {
      await authApi.register(payload)
      // Auto-login to obtain JWT cookies, then fetch profile
      await authApi.login(payload.email, payload.password)
      const meRes = await authApi.getMe()
      const meData = meRes.data?.data ?? meRes.data
      user.value = {
        id: meData.id,
        email: meData.email,
        first_name: meData.first_name || '',
        last_name: meData.last_name || '',
        full_name: `${meData.first_name || ''} ${meData.last_name || ''}`.trim() || meData.email || '',
        role: meData.role,
        account_type: meData.account_type,
        current_level: meData.current_level,
      }
      return { success: true }
    } catch (err) {
      const body = err.response?.data ?? {}
      // Unwrap VNNumberJSONRenderer envelope if present
      const errors = body.errors ?? body
      const message = body.message ?? null
      return { success: false, errors, message }
    } finally {
      loading.value = false
    }
  }

  return {
    user, loading, initialized,
    isLoggedIn, isAdmin, isTeacher, isPremium, displayName,
    init, login, logout, register, refreshUser,
  }
})
