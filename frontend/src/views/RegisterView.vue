<template>
  <div class="min-h-screen flex items-center justify-center px-4"
       style="background: radial-gradient(ellipse at 40% 0%, rgba(99,102,241,0.12) 0%, transparent 60%), var(--color-surface)">
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
        <h1 class="text-2xl font-black" style="color: var(--color-text-base)">Tạo tài khoản</h1>
        <p class="text-sm mt-1" style="color: var(--color-text-muted)">Bắt đầu học tiếng Anh miễn phí ngay hôm nay</p>
      </div>

      <div class="rounded-2xl p-8"
           style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
        <form @submit.prevent="handleRegister" class="space-y-4" novalidate>
          <!-- Name row -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold mb-1.5 uppercase tracking-wider"
                     style="color: var(--color-text-muted)">Họ</label>
              <input v-model="form.last_name" type="text" placeholder="Nguyễn"
                     class="w-full px-3 py-2.5 rounded-xl text-sm outline-none"
                     :class="errors.last_name ? 'ring-2 ring-red-500' : ''"
                     style="background-color: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)"
                     @focus="errors.last_name = ''" />
              <p v-if="errors.last_name" class="text-xs mt-1 text-red-400">{{ errors.last_name }}</p>
            </div>
            <div>
              <label class="block text-xs font-semibold mb-1.5 uppercase tracking-wider"
                     style="color: var(--color-text-muted)">Tên</label>
              <input v-model="form.first_name" type="text" placeholder="Văn A"
                     class="w-full px-3 py-2.5 rounded-xl text-sm outline-none"
                     :class="errors.first_name ? 'ring-2 ring-red-500' : ''"
                     style="background-color: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)"
                     @focus="errors.first_name = ''" />
              <p v-if="errors.first_name" class="text-xs mt-1 text-red-400">{{ errors.first_name }}</p>
            </div>
          </div>

          <!-- Email -->
          <div>
            <label class="block text-xs font-semibold mb-1.5 uppercase tracking-wider"
                   style="color: var(--color-text-muted)">Email</label>
            <input v-model="form.email" type="email" autocomplete="email" placeholder="hoc.vien@example.com"
                   class="w-full px-4 py-2.5 rounded-xl text-sm outline-none"
                   :class="errors.email ? 'ring-2 ring-red-500' : ''"
                   style="background-color: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)"
                   @focus="errors.email = ''" />
            <p v-if="errors.email" class="text-xs mt-1 text-red-400">{{ errors.email }}</p>
          </div>

          <!-- Password -->
          <div>
            <label class="block text-xs font-semibold mb-1.5 uppercase tracking-wider"
                   style="color: var(--color-text-muted)">Mật khẩu</label>
            <div class="relative">
              <input v-model="form.password" :type="showPwd ? 'text' : 'password'"
                     autocomplete="new-password" placeholder="Ít nhất 8 ký tự"
                     class="w-full px-4 py-2.5 pr-12 rounded-xl text-sm outline-none"
                     :class="errors.password ? 'ring-2 ring-red-500' : ''"
                     style="background-color: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)"
                     @focus="errors.password = ''" />
              <button type="button" @click="showPwd = !showPwd"
                      class="absolute right-3 top-1/2 -translate-y-1/2"
                      style="color: var(--color-text-soft)">
                {{ showPwd ? '🙈' : '👁️' }}
              </button>
            </div>
            <p v-if="errors.password" class="text-xs mt-1 text-red-400">{{ errors.password }}</p>
          </div>

          <!-- Confirm password -->
          <div>
            <label class="block text-xs font-semibold mb-1.5 uppercase tracking-wider"
                   style="color: var(--color-text-muted)">Xác nhận mật khẩu</label>
            <input v-model="form.password2" :type="showPwd ? 'text' : 'password'"
                   autocomplete="new-password" placeholder="Nhập lại mật khẩu"
                   class="w-full px-4 py-2.5 rounded-xl text-sm outline-none"
                   :class="errors.password2 ? 'ring-2 ring-red-500' : ''"
                   style="background-color: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)"
                   @focus="errors.password2 = ''" />
            <p v-if="errors.password2" class="text-xs mt-1 text-red-400">{{ errors.password2 }}</p>
          </div>

          <!-- Phone (optional) -->
          <div>
            <label class="block text-xs font-semibold mb-1.5 uppercase tracking-wider"
                   style="color: var(--color-text-muted)">Số điện thoại <span class="normal-case font-normal">(tùy chọn)</span></label>
            <input v-model="form.phone_number" type="tel" placeholder="0912345678"
                   class="w-full px-4 py-2.5 rounded-xl text-sm outline-none"
                   style="background-color: var(--color-surface-03); color: var(--color-text-base); border: 1px solid var(--color-surface-04)" />
          </div>

          <!-- Error banner -->
          <Transition name="fade">
            <div v-if="globalError" class="flex items-center gap-2 p-3 rounded-xl text-sm"
                 style="background-color: rgba(239,68,68,0.1); color: #fca5a5; border: 1px solid rgba(239,68,68,0.3)">
              <span>⚠️</span>{{ globalError }}
            </div>
          </Transition>

          <!-- Submit -->
          <button type="submit" :disabled="auth.loading"
                  class="w-full py-3 rounded-xl font-semibold text-sm text-white transition hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
                  style="background: linear-gradient(135deg, #4f46e5, #7c3aed)">
            <span v-if="auth.loading" class="inline-flex items-center gap-2">
              <span class="animate-spin">⟳</span> Đang tạo tài khoản...
            </span>
            <span v-else>Đăng ký</span>
          </button>
        </form>

        <p class="text-center text-sm mt-6" style="color: var(--color-text-soft)">
          Đã có tài khoản?
          <RouterLink to="/login" class="font-semibold transition hover:opacity-80"
                      style="color: var(--color-primary-400)">Đăng nhập</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({
  first_name: '', last_name: '', email: '',
  password: '', password2: '', phone_number: '',
})
const errors = reactive({
  first_name: '', last_name: '', email: '', password: '', password2: '',
})
const globalError = ref('')
const showPwd = ref(false)

// Translate Django's English validation messages → Vietnamese
const PASSWORD_ERROR_MAP = {
  'This password is too common.': 'Mật khẩu này quá phổ biến, vui lòng chọn mật khẩu khác.',
  'This password is entirely numeric.': 'Mật khẩu không được chứa toàn số (phải có chữ cái hoặc ký tự đặc biệt).',
  'This password is too short. It must contain at least 8 characters.': 'Mật khẩu phải có ít nhất 8 ký tự.',
  'The password is too similar to the email address.': 'Mật khẩu quá giống địa chỉ email, vui lòng chọn mật khẩu khác.',
  'The password is too similar to the username.': 'Mật khẩu quá giống tên đăng nhập.',
  'The password is too similar to the first name.': 'Mật khẩu quá giống tên của bạn.',
  'The password is too similar to the last name.': 'Mật khẩu quá giống họ của bạn.',
}

function translate(msg) {
  if (!msg) return msg
  return PASSWORD_ERROR_MAP[msg] ?? msg
}

function validate() {
  let ok = true
  Object.keys(errors).forEach(k => errors[k] = '')
  if (!form.first_name.trim()) { errors.first_name = 'Vui lòng nhập tên.'; ok = false }
  if (!form.last_name.trim()) { errors.last_name = 'Vui lòng nhập họ.'; ok = false }
  if (!form.email.includes('@')) { errors.email = 'Email không hợp lệ.'; ok = false }
  if (form.password.length < 8) { errors.password = 'Mật khẩu phải ít nhất 8 ký tự.'; ok = false }
  if (form.password !== form.password2) { errors.password2 = 'Mật khẩu không khớp.'; ok = false }
  return ok
}

async function handleRegister() {
  globalError.value = ''
  if (!validate()) return

  const result = await auth.register({
    first_name: form.first_name.trim(),
    last_name: form.last_name.trim(),
    email: form.email.trim(),
    password: form.password,
    password2: form.password2,
    phone_number: form.phone_number.trim() || undefined,
  })

  if (result.success) {
    router.push('/dashboard')
  } else {
    // Map field-level errors from backend response to per-field display
    let hasFieldErrors = false
    const backendErrors = result.errors
    if (backendErrors && typeof backendErrors === 'object') {
      Object.keys(backendErrors).forEach(key => {
        const raw = backendErrors[key]
        const msg = Array.isArray(raw)
          ? raw.map(translate).join(' ')
          : translate(String(raw))
        if (Object.prototype.hasOwnProperty.call(errors, key)) {
          errors[key] = msg
          hasFieldErrors = true
        }
      })
    }

    // Global banner: show specific non-field error, or a summary if only field errors exist
    const nonField = backendErrors?.non_field_errors ?? backendErrors?.detail
    if (nonField) {
      const m = Array.isArray(nonField) ? nonField[0] : nonField
      globalError.value = translate(String(m))
    } else if (!hasFieldErrors) {
      globalError.value = result.message || 'Đăng ký thất bại. Vui lòng thử lại.'
    } else {
      globalError.value = 'Vui lòng kiểm tra lại thông tin bên trên.'
    }
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
