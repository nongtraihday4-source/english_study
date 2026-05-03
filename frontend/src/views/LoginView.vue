<template>
  <div class="min-h-screen flex items-center justify-center px-4"
       style="background: radial-gradient(ellipse at 60% 0%, rgba(99,102,241,0.15) 0%, transparent 60%), var(--color-surface)">
    <div class="w-full max-w-md">
      <!-- Back to home -->
      <div class="text-center mb-4">
        <RouterLink to="/" class="inline-flex items-center gap-1.5 text-xs font-medium transition hover:opacity-70"
                    style="color: var(--color-text-muted)">
          ← Về trang chủ
        </RouterLink>
      </div>

      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="inline-flex w-16 h-16 rounded-2xl items-center justify-center text-white font-black text-2xl mb-4"
             style="background: linear-gradient(135deg, #6366f1, #8b5cf6)">ES</div>
        <h1 class="text-2xl font-black" style="color: var(--color-text-base)">
          {{ step === 1 ? 'Chào mừng trở lại' : 'Xác thực 2 lớp' }}
        </h1>
        <p class="text-sm mt-1" style="color: var(--color-text-muted)">
          {{ step === 1 ? 'Tiếp tục hành trình học tiếng Anh của bạn' : 'Vui lòng nhập mã OTP từ ứng dụng Authenticator' }}
        </p>
      </div>

      <!-- Card -->
      <div class="rounded-2xl p-8"
           style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
        <form @submit.prevent="handleLogin" class="space-y-5" novalidate>
          
          <template v-if="step === 1">
            <!-- Email -->
            <div>
              <label class="block text-xs font-semibold mb-2 uppercase tracking-wider"
                     style="color: var(--color-text-muted)">Email</label>
              <input
                v-model="form.email"
                type="email"
                autocomplete="email"
                placeholder="hoc.vien@example.com"
                required
                class="w-full px-4 py-3 rounded-xl text-sm outline-none transition focus:ring-2"
                :class="errors.email ? 'ring-2 ring-red-500' : ''"
                style="background-color: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)"
                @focus="errors.email = ''"
              />
              <p v-if="errors.email" class="text-xs mt-1.5 text-red-400">{{ errors.email }}</p>
            </div>

            <!-- Password -->
            <div>
              <label class="block text-xs font-semibold mb-2 uppercase tracking-wider"
                     style="color: var(--color-text-muted)">Mật khẩu</label>
              <div class="relative">
                <input
                  v-model="form.password"
                  :type="showPwd ? 'text' : 'password'"
                  autocomplete="current-password"
                  placeholder="••••••••"
                  required
                  class="w-full px-4 py-3 pr-12 rounded-xl text-sm outline-none transition"
                  :class="errors.password ? 'ring-2 ring-red-500' : ''"
                  style="background-color: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)"
                  @focus="errors.password = ''"
                />
                <button type="button" @click="showPwd = !showPwd"
                        class="absolute right-3 top-1/2 -translate-y-1/2 text-sm"
                        style="color: var(--color-text-soft)">
                  {{ showPwd ? '🙈' : '👁️' }}
                </button>
              </div>
              <p v-if="errors.password" class="text-xs mt-1.5 text-red-400">{{ errors.password }}</p>
            </div>
          </template>

          <template v-else>
            <!-- 2FA OTP Code -->
            <div>
              <label class="block text-xs font-semibold mb-2 uppercase tracking-wider text-center"
                     style="color: var(--color-text-muted)">Mã OTP 6 số</label>
              <input
                v-model="form.otpCode"
                type="text"
                maxlength="6"
                placeholder="000000"
                required
                class="w-full px-4 py-3 rounded-xl text-2xl tracking-widest text-center font-mono outline-none transition focus:ring-2"
                style="background-color: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)"
                @input="form.otpCode = form.otpCode.replace(/\D/g, '')"
              />
            </div>
          </template>

          <!-- Error banner -->
          <Transition name="fade">
            <div v-if="globalError"
                 class="flex items-center gap-2 p-3 rounded-xl text-sm"
                 style="background-color: rgba(239,68,68,0.1); color: #fca5a5; border: 1px solid rgba(239,68,68,0.3)">
              <span>⚠️</span>{{ globalError }}
            </div>
          </Transition>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="auth.loading || (step === 2 && form.otpCode.length < 6)"
            class="w-full py-3 rounded-xl font-semibold text-sm text-white transition hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
            style="background: linear-gradient(135deg, #4f46e5, #7c3aed)"
          >
            <span v-if="auth.loading" class="inline-flex items-center gap-2">
              <span class="animate-spin">⟳</span> Đang xử lý...
            </span>
            <span v-else>{{ step === 1 ? 'Đăng nhập' : 'Xác thực' }}</span>
          </button>
          
          <!-- Back button if on 2FA step -->
          <button v-if="step === 2 && !auth.loading" type="button" @click="step = 1; form.otpCode = ''" 
                  class="w-full text-sm text-center transition hover:opacity-80"
                  style="color: var(--color-text-muted)">
            ← Quay lại
          </button>
        </form>

        <p v-if="step === 1" class="text-center text-sm mt-6" style="color: var(--color-text-soft)">
          Chưa có tài khoản?
          <RouterLink to="/register" class="font-semibold transition hover:opacity-80"
                      style="color: var(--color-primary-400)">Đăng ký ngay</RouterLink>
        </p>
        <p v-if="step === 1" class="text-center text-xs mt-3" style="color: var(--color-text-muted)">
          Không đăng nhập được?
          <RouterLink to="/help/support-request" class="font-semibold transition hover:opacity-80" style="color: #3b82f6">
            Gửi yêu cầu hỗ trợ tại đây
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const step = ref(1) // 1: Email/Password, 2: OTP (2FA)
const form = reactive({ email: '', password: '', otpCode: '' })
const errors = reactive({ email: '', password: '' })
const globalError = ref('')
const showPwd = ref(false)

function validate() {
  if (step.value === 2) return true
  errors.email = ''
  errors.password = ''
  let ok = true
  if (!form.email.includes('@')) { errors.email = 'Email không hợp lệ.'; ok = false }
  if (form.password.length < 6) { errors.password = 'Mật khẩu phải ít nhất 6 ký tự.'; ok = false }
  return ok
}

async function handleLogin() {
  globalError.value = ''
  if (!validate()) return

  const result = await auth.login(form.email, form.password, step.value === 2 ? form.otpCode : undefined)
  
  if (result.requires2FA) {
    step.value = 2; // Move to step 2 if backend demands 2FA
    if (form.otpCode) {
       globalError.value = result.message || 'Mã xác thực không đúng.'
    }
  } else if (result.success) {
    const role = auth.user?.role
    let redirect = route.query.redirect || ''
    if (!redirect) {
      if (role === 'support') redirect = '/support'
      else redirect = '/dashboard'
    }
    router.push(redirect)
  } else {
    globalError.value = result.message
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
