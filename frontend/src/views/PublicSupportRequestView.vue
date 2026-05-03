<template>
  <div
    class="min-h-screen px-4 py-10 sm:py-14"
    style="background: radial-gradient(1100px 480px at 80% -5%, color-mix(in srgb, var(--color-primary-600) 18%, transparent) 0%, transparent 55%), radial-gradient(800px 420px at 5% 100%, color-mix(in srgb, var(--color-accent-500) 10%, transparent) 0%, transparent 52%), var(--color-surface)"
  >
    <!-- Brand header -->
    <div class="max-w-5xl mx-auto mb-8 flex items-center gap-3">
      <RouterLink to="/login" class="flex items-center gap-3 group">
        <div class="w-9 h-9 rounded-xl flex items-center justify-center text-white font-black text-sm shrink-0"
             style="background: linear-gradient(135deg, var(--color-primary-500), #8b5cf6)">ES</div>
        <span class="font-bold text-base tracking-wide" style="color: var(--color-text-base)">English Study</span>
      </RouterLink>
      <span class="text-xs px-2 py-0.5 rounded-full font-medium ml-1"
            style="background-color: var(--color-surface-03); color: var(--color-text-muted); border: 1px solid var(--color-surface-04)">
        Hỗ trợ khách hàng
      </span>
    </div>

    <div class="max-w-5xl mx-auto grid lg:grid-cols-12 gap-6 lg:gap-8">
      <!-- Left info panel -->
      <section class="lg:col-span-7 space-y-5">
        <div
          class="rounded-2xl p-6 sm:p-7"
          style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
        >
          <p
            class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold"
            style="background-color: color-mix(in srgb, var(--color-primary-500) 18%, transparent); color: var(--color-primary-300)"
          >
            <span>Hỗ trợ trực tuyến</span>
            <span class="w-1.5 h-1.5 rounded-full animate-pulse" style="background-color: #22c55e" />
            <span>Phản hồi trong ngày</span>
          </p>

          <h1 class="mt-4 text-3xl sm:text-4xl font-black tracking-tight" style="font-family: Nunito, sans-serif; color: var(--color-text-base)">
            Gửi yêu cầu hỗ trợ
          </h1>
          <p class="mt-2 text-sm sm:text-base leading-relaxed" style="color: var(--color-text-muted)">
            Nếu bạn không đăng nhập được, quên thông tin tài khoản hoặc gặp sự cố thanh toán —
            điền form bên cạnh để đội ngũ CSKH liên hệ hỗ trợ bạn.
          </p>

          <!-- Steps - user-facing language only -->
          <div class="mt-5 grid sm:grid-cols-3 gap-3">
            <div class="rounded-xl p-4" style="background-color: var(--color-surface-03); border: 1px solid var(--color-surface-04)">
              <div class="w-6 h-6 rounded-lg flex items-center justify-center text-xs font-bold mb-2"
                   style="background-color: color-mix(in srgb, var(--color-primary-500) 24%, transparent); color: var(--color-primary-300)">1</div>
              <p class="text-sm font-semibold" style="color: var(--color-text-base)">Điền thông tin liên hệ</p>
              <p class="text-xs mt-1 leading-relaxed" style="color: var(--color-text-soft)">Cung cấp email hoặc số điện thoại để chúng tôi liên hệ lại.</p>
            </div>
            <div class="rounded-xl p-4" style="background-color: var(--color-surface-03); border: 1px solid var(--color-surface-04)">
              <div class="w-6 h-6 rounded-lg flex items-center justify-center text-xs font-bold mb-2"
                   style="background-color: color-mix(in srgb, var(--color-accent-500) 20%, transparent); color: var(--color-accent-400)">2</div>
              <p class="text-sm font-semibold" style="color: var(--color-text-base)">Nhân viên xem xét</p>
              <p class="text-xs mt-1 leading-relaxed" style="color: var(--color-text-soft)">Đội ngũ CSKH tiếp nhận và xem xét yêu cầu của bạn.</p>
            </div>
            <div class="rounded-xl p-4" style="background-color: var(--color-surface-03); border: 1px solid var(--color-surface-04)">
              <div class="w-6 h-6 rounded-lg flex items-center justify-center text-xs font-bold mb-2"
                   style="background-color: color-mix(in srgb, #22c55e 20%, transparent); color: #4ade80">3</div>
              <p class="text-sm font-semibold" style="color: var(--color-text-base)">Nhận phản hồi</p>
              <p class="text-xs mt-1 leading-relaxed" style="color: var(--color-text-soft)">Chúng tôi phản hồi qua email hoặc gọi điện trong vòng 24 giờ.</p>
            </div>
          </div>
        </div>

        <!-- About the platform -->
        <div
          class="rounded-2xl p-6"
          style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
        >
          <div class="flex items-center gap-3 mb-4">
            <div class="w-8 h-8 rounded-xl flex items-center justify-center text-white font-black text-xs shrink-0"
                 style="background: linear-gradient(135deg, var(--color-primary-500), #8b5cf6)">ES</div>
            <div>
              <p class="text-sm font-bold" style="color: var(--color-text-base)">English Study</p>
              <p class="text-xs" style="color: var(--color-text-soft)">Nền tảng học tiếng Anh trực tuyến</p>
            </div>
          </div>
          <p class="text-sm leading-relaxed" style="color: var(--color-text-muted)">
            Chúng tôi cung cấp lộ trình học tiếng Anh cá nhân hoá với từ vựng, ngữ pháp, và luyện phát âm.
            Đội ngũ CSKH luôn sẵn sàng hỗ trợ bạn trong quá trình học.
          </p>
          <div class="mt-4 pt-4 flex flex-col gap-2" style="border-top: 1px solid var(--color-surface-04)">
            <p class="text-xs font-semibold" style="color: var(--color-text-soft)">Bạn nhớ mật khẩu?</p>
            <RouterLink
              to="/login"
              class="inline-flex items-center gap-1.5 text-sm font-medium transition-opacity hover:opacity-80"
              style="color: var(--color-primary-400)"
            >
              <span>→</span>
              <span>Quay lại trang đăng nhập</span>
            </RouterLink>
          </div>
        </div>
      </section>

      <!-- Right form panel -->
      <section class="lg:col-span-5">
        <div
          class="rounded-2xl p-6 sm:p-7"
          style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
        >
          <h2 class="text-lg font-black" style="font-family: Nunito, sans-serif; color: var(--color-text-base)">
            {{ auth.isLoggedIn ? 'Tạo phiếu hỗ trợ' : 'Gửi yêu cầu không cần đăng nhập' }}
          </h2>
          <p class="text-xs mt-1 leading-relaxed" style="color: var(--color-text-soft)">
            {{ auth.isLoggedIn ? 'Yêu cầu được ưu tiên xử lý cho tài khoản của bạn.' : 'Cung cấp ít nhất email hoặc số điện thoại để chúng tôi liên hệ lại.' }}
          </p>

          <form class="mt-5 space-y-4" @submit.prevent="submitRequest" novalidate>
            <div class="grid sm:grid-cols-2 gap-3">
              <div class="sm:col-span-2">
                <label class="block text-xs font-semibold mb-1.5" style="color: var(--color-text-soft)">Họ và tên <span style="color: var(--color-text-muted)">*</span></label>
                <input
                  v-model="form.full_name"
                  type="text"
                  class="input-base w-full px-3.5 py-2.5 rounded-xl text-sm transition-colors focus:ring-2"
                  :style="errors.full_name ? 'border-color: #ef4444' : ''"
                  placeholder="Nguyễn Văn A"
                  maxlength="120"
                />
                <p v-if="errors.full_name" class="text-xs mt-1" style="color: #f87171">{{ errors.full_name }}</p>
              </div>

              <div>
                <label class="block text-xs font-semibold mb-1.5" style="color: var(--color-text-soft)">Email</label>
                <input
                  v-model="form.email"
                  type="email"
                  class="input-base w-full px-3.5 py-2.5 rounded-xl text-sm transition-colors"
                  placeholder="ten@example.com"
                  maxlength="150"
                />
              </div>

              <div>
                <label class="block text-xs font-semibold mb-1.5" style="color: var(--color-text-soft)">Số điện thoại</label>
                <input
                  v-model="form.phone"
                  type="text"
                  class="input-base w-full px-3.5 py-2.5 rounded-xl text-sm transition-colors"
                  placeholder="09xx xxx xxx"
                  maxlength="20"
                />
              </div>
              <p v-if="!form.email.trim() && !form.phone.trim() && (errors.full_name || errors.subject)" class="sm:col-span-2 text-xs" style="color: #f87171">Cần nhập ít nhất email hoặc số điện thoại.</p>
            </div>

            <div>
              <label class="block text-xs font-semibold mb-1.5" style="color: var(--color-text-soft)">Loại vấn đề</label>
              <select
                v-model="form.issue_type"
                class="input-base w-full px-3.5 py-2.5 rounded-xl text-sm"
              >
                <option value="account_access">Không đăng nhập được / quên thông tin</option>
                <option value="payment">Thanh toán / hoàn tiền</option>
                <option value="technical">Lỗi kỹ thuật</option>
                <option v-if="auth.isLoggedIn" value="learning">Nội dung học tập</option>
                <option value="other">Khác</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-semibold mb-1.5" style="color: var(--color-text-soft)">Tiêu đề ngắn gọn <span style="color: var(--color-text-muted)">*</span></label>
              <input
                v-model="form.subject"
                type="text"
                class="input-base w-full px-3.5 py-2.5 rounded-xl text-sm transition-colors"
                :style="errors.subject ? 'border-color: #ef4444' : ''"
                placeholder="Ví dụ: Không nhận được OTP đăng nhập"
                maxlength="200"
              />
              <p v-if="errors.subject" class="text-xs mt-1" style="color: #f87171">{{ errors.subject }}</p>
            </div>

            <div>
              <div class="flex items-center justify-between mb-1.5">
                <label class="block text-xs font-semibold" style="color: var(--color-text-soft)">Mô tả chi tiết <span style="color: var(--color-text-muted)">*</span></label>
                <span
                  class="text-[11px] tabular-nums"
                  :style="{ color: form.description.length >= 30 ? '#4ade80' : 'var(--color-text-soft)' }"
                >{{ form.description.length }}/30</span>
              </div>
              <textarea
                v-model="form.description"
                rows="5"
                class="input-base w-full px-3.5 py-2.5 rounded-xl text-sm resize-y transition-colors"
                :style="errors.description ? 'border-color: #ef4444' : ''"
                placeholder="Mô tả rõ bước bạn đã làm, thời điểm lỗi xảy ra và ảnh hưởng cụ thể..."
              />
              <p v-if="errors.description" class="text-xs mt-1" style="color: #f87171">{{ errors.description }}</p>
            </div>

            <!-- Honeypot - hidden from real users -->
            <div class="hidden" aria-hidden="true">
              <label for="company_name">Company</label>
              <input id="company_name" v-model="form.honeypot" type="text" autocomplete="off" tabindex="-1" />
            </div>

            <label class="flex items-start gap-2.5 cursor-pointer" style="color: var(--color-text-muted)">
              <input v-model="form.consent" type="checkbox" class="mt-0.5 rounded shrink-0 accent-indigo-500" />
              <span class="text-xs leading-5">
                Tôi xác nhận thông tin trên là chính xác và đồng ý để English Study liên hệ hỗ trợ tài khoản của tôi.
              </span>
            </label>
            <p v-if="errors.consent" class="text-xs" style="color: #f87171">{{ errors.consent }}</p>

            <!-- Error feedback -->
            <div v-if="error" class="rounded-xl px-4 py-3 text-sm" style="background-color: color-mix(in srgb, #ef4444 14%, transparent); color: #fca5a5; border: 1px solid color-mix(in srgb, #ef4444 30%, transparent)">
              {{ error }}
            </div>

            <!-- Success feedback -->
            <div v-if="success" class="rounded-xl px-4 py-3 text-sm" style="background-color: color-mix(in srgb, #22c55e 14%, transparent); color: #86efac; border: 1px solid color-mix(in srgb, #22c55e 28%, transparent)">
              <p class="font-semibold">{{ success }}</p>
              <p class="text-xs mt-1 opacity-80">Mã yêu cầu: #{{ lastRequestId }}<span v-if="lastTicketId"> · Ticket #{{ lastTicketId }}</span></p>
            </div>

            <button
              type="submit"
              :disabled="submitting || !canSubmit || cooldownLeft > 0"
              class="w-full py-3 rounded-xl text-sm font-bold text-white transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              style="background: linear-gradient(135deg, var(--color-primary-500) 0%, var(--color-primary-700) 100%)"
            >
              <span v-if="submitting">Đang gửi yêu cầu...</span>
              <span v-else-if="cooldownLeft > 0">Chờ {{ cooldownLeft }}s để gửi lại</span>
              <span v-else>Gửi yêu cầu hỗ trợ</span>
            </button>
          </form>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { publicSupportApi } from '@/api/support.js'

const auth = useAuthStore()

const form = reactive({
  full_name: '',
  email: '',
  phone: '',
  issue_type: 'account_access',
  subject: '',
  description: '',
  consent: false,
  honeypot: '',
})
const errors = reactive({ full_name: '', subject: '', description: '', consent: '' })

const submitting = ref(false)
const error = ref('')
const success = ref('')
const lastRequestId = ref(null)
const lastTicketId = ref(null)
const cooldownLeft = ref(0)
let cooldownTimer = null

const canSubmit = computed(() => {
  const hasContact = !!(form.email.trim() || form.phone.trim())
  return (
    form.full_name.trim().length >= 2
    && hasContact
    && form.subject.trim().length >= 8
    && form.description.trim().length >= 30
    && form.consent
  )
})

function startCooldown(seconds = 45) {
  cooldownLeft.value = seconds
  if (cooldownTimer) clearInterval(cooldownTimer)
  localStorage.setItem('es_support_cooldown_until', String(Date.now() + seconds * 1000))
  cooldownTimer = setInterval(() => {
    cooldownLeft.value = Math.max(0, cooldownLeft.value - 1)
    if (cooldownLeft.value === 0) {
      clearInterval(cooldownTimer)
      cooldownTimer = null
      localStorage.removeItem('es_support_cooldown_until')
    }
  }, 1000)
}

function restoreCooldown() {
  const untilRaw = localStorage.getItem('es_support_cooldown_until')
  if (!untilRaw) return
  const remainMs = Number(untilRaw) - Date.now()
  if (remainMs <= 0) {
    localStorage.removeItem('es_support_cooldown_until')
    return
  }
  startCooldown(Math.ceil(remainMs / 1000))
}

function validate() {
  errors.full_name = ''
  errors.subject = ''
  errors.description = ''
  errors.consent = ''

  if (form.full_name.trim().length < 2) errors.full_name = 'Vui lòng nhập họ tên hợp lệ.'
  if (form.subject.trim().length < 8) errors.subject = 'Tiêu đề cần ít nhất 8 ký tự.'
  if (form.description.trim().length < 30) errors.description = 'Mô tả cần ít nhất 30 ký tự.'
  if (!form.consent) errors.consent = 'Bạn cần xác nhận trước khi gửi.'
  if (!form.email.trim() && !form.phone.trim()) {
    error.value = 'Bạn cần nhập email hoặc số điện thoại để nhân viên liên hệ.'
  }

  return !errors.full_name && !errors.subject && !errors.description && !errors.consent && !!(form.email.trim() || form.phone.trim())
}

async function submitRequest() {
  error.value = ''
  success.value = ''
  lastRequestId.value = null
  lastTicketId.value = null

  if (cooldownLeft.value > 0) return
  if (!validate()) return

  submitting.value = true
  try {
    const payload = {
      full_name: form.full_name.trim(),
      email: form.email.trim(),
      phone: form.phone.trim(),
      issue_type: form.issue_type,
      subject: form.subject.trim(),
      description: form.description.trim(),
      consent: form.consent,
      honeypot: form.honeypot,
    }

    const { data } = await publicSupportApi.submitRequest(payload)
    const result = data.data ?? data
    success.value = result.detail || 'Yêu cầu đã gửi thành công.'
    lastRequestId.value = result.request_id
    lastTicketId.value = result.ticket_id

    form.subject = ''
    form.description = ''
    form.honeypot = ''
    form.consent = false
    startCooldown()
  } catch (err) {
    const body = err.response?.data || {}
    error.value = body.detail || body.message || body.errors?.detail?.[0] || 'Không thể gửi yêu cầu. Vui lòng thử lại.'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  if (auth.user) {
    form.full_name = auth.user.full_name || auth.user.email || ''
    form.email = auth.user.email || ''
    form.phone = auth.user.phone_number || ''
    form.issue_type = 'technical'
  }
  restoreCooldown()
})

onBeforeUnmount(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})
</script>
