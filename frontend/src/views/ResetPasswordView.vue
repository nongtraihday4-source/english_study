<template>
  <div class="min-h-screen flex items-center justify-center p-4" style="background-color: var(--color-surface-01)">
    <div class="w-full max-w-sm rounded-2xl p-8 space-y-5" style="background-color: var(--color-surface-02)">
      <div class="text-center">
        <div class="text-3xl mb-2">🔐</div>
        <h1 class="text-xl font-bold" style="color: var(--color-text-base)">Đặt lại mật khẩu</h1>
        <p class="text-sm mt-1" style="color: var(--color-text-muted)">Nhập mật khẩu mới cho tài khoản của bạn</p>
      </div>

      <!-- Success state -->
      <div v-if="success" class="text-center space-y-4">
        <div class="text-4xl">✅</div>
        <p class="font-semibold" style="color: #4ade80">Đặt lại mật khẩu thành công!</p>
        <p class="text-sm" style="color: var(--color-text-muted)">Bạn có thể đăng nhập với mật khẩu mới.</p>
        <RouterLink to="/login" class="block w-full text-center py-2.5 rounded-xl text-sm font-semibold hover:opacity-80 transition" style="background-color:#3b82f6;color:#fff">← Đăng nhập</RouterLink>
      </div>

      <!-- Error state — invalid/expired token -->
      <div v-else-if="tokenError" class="text-center space-y-4">
        <div class="text-4xl">❌</div>
        <p class="font-semibold" style="color: #f87171">Liên kết không hợp lệ hoặc đã hết hạn</p>
        <p class="text-sm" style="color: var(--color-text-muted)">Vui lòng liên hệ CSKH để nhận liên kết mới.</p>
        <RouterLink to="/login" class="block w-full text-center py-2.5 rounded-xl text-sm font-semibold hover:opacity-80 transition" style="background-color:var(--color-surface-03);color:var(--color-text-base)">← Đăng nhập</RouterLink>
      </div>

      <!-- Form -->
      <form v-else class="space-y-4" @submit.prevent="submit">
        <div class="space-y-1">
          <label class="text-xs font-semibold" style="color: var(--color-text-muted)">Mật khẩu mới</label>
          <input
            v-model="password"
            type="password"
            minlength="8"
            required
            class="w-full rounded-xl px-3 py-2.5 text-sm border focus:outline-none"
            style="background-color:var(--color-surface-03);border-color:var(--color-surface-04);color:var(--color-text-base)"
          />
        </div>
        <div class="space-y-1">
          <label class="text-xs font-semibold" style="color: var(--color-text-muted)">Xác nhận mật khẩu</label>
          <input
            v-model="confirm"
            type="password"
            minlength="8"
            required
            class="w-full rounded-xl px-3 py-2.5 text-sm border focus:outline-none"
            style="background-color:var(--color-surface-03);border-color:var(--color-surface-04);color:var(--color-text-base)"
          />
        </div>
        <p v-if="error" class="text-xs" style="color:#f87171">{{ error }}</p>
        <button
          type="submit"
          :disabled="loading"
          class="w-full py-2.5 rounded-xl text-sm font-semibold hover:opacity-80 transition disabled:opacity-50"
          style="background-color:#3b82f6;color:#fff"
        >{{ loading ? 'Đang xử lý...' : 'Xác nhận đặt lại' }}</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { authPasswordResetConfirm } from '@/api/support.js'

const route = useRoute()
const uid = ref('')
const token = ref('')
const password = ref('')
const confirm = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)
const tokenError = ref(false)

onMounted(() => {
  uid.value = route.query.uid ?? ''
  token.value = route.query.token ?? ''
  if (!uid.value || !token.value) tokenError.value = true
})

async function submit() {
  error.value = ''
  if (password.value.length < 8) { error.value = 'Mật khẩu phải có ít nhất 8 ký tự.'; return }
  if (password.value !== confirm.value) { error.value = 'Mật khẩu xác nhận không khớp.'; return }
  loading.value = true
  try {
    await authPasswordResetConfirm({ uid: uid.value, token: token.value, new_password: password.value })
    success.value = true
  } catch (e) {
    const d = e?.response?.data
    if (d?.token || d?.uid) { tokenError.value = true; return }
    error.value = d?.detail ?? (typeof d === 'object' ? Object.values(d).flat().join(' ') : 'Đặt lại thất bại.')
  } finally { loading.value = false }
}
</script>
