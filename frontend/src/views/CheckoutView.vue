<template>
  <div class="checkout-page">
    <!-- Back link -->
    <RouterLink to="/pricing" class="back-link">← Quay lại gói học</RouterLink>

    <!-- Loading plan details -->
    <div v-if="loadingPlan" class="checkout-skeleton">
      <div class="skel-block animate-pulse" style="height:180px;border-radius:1rem;"></div>
      <div class="skel-block animate-pulse" style="height:280px;border-radius:1rem;margin-top:1.25rem;"></div>
    </div>

    <!-- Plan not found -->
    <div v-else-if="!plan" class="not-found">
      <span class="text-5xl">😕</span>
      <p>Không tìm thấy gói học. <RouterLink to="/pricing" class="link-underline">Xem tất cả gói</RouterLink></p>
    </div>

    <!-- Checkout form -->
    <div v-else class="checkout-layout">
      <!-- LEFT — Order summary -->
      <div class="order-summary" :class="{ 'plan-gold': isYearly }">
        <div v-if="isYearly" class="gold-banner">🏆 Phổ biến nhất</div>
        <div class="summary-header">
          <span class="summary-icon">{{ isYearly ? '👑' : '⚡' }}</span>
          <div>
            <h2 class="summary-plan-name">{{ plan.name_vi }}</h2>
            <p class="summary-period">{{ periodLabel }}</p>
          </div>
        </div>

        <!-- Features -->
        <ul class="summary-features">
          <li v-for="f in plan.features_json || defaultFeatures" :key="f" class="summary-feat">✓ {{ f }}</li>
        </ul>

        <!-- Price breakdown -->
        <div class="price-breakdown">
          <div class="price-row">
            <span>Giá gốc</span>
            <span>{{ plan.price_display }}</span>
          </div>
          <div v-if="discountData" class="price-row price-discount">
            <span>Giảm giá ({{ discountData.discount_display }})</span>
            <span class="discount-amount">−{{ discountAmountDisplay }}</span>
          </div>
          <div class="price-row price-total">
            <span>Tổng cộng</span>
            <span :class="isYearly ? 'total-gold' : 'total-primary'">{{ finalPriceDisplay }}</span>
          </div>
        </div>
      </div>

      <!-- RIGHT — Checkout form -->
      <div class="checkout-form-card">
        <h1 class="form-title">Thông tin thanh toán</h1>

        <!-- Must login notice -->
        <div v-if="!isLoggedIn" class="login-notice">
          <span>🔐</span>
          <span>Bạn cần <RouterLink to="/login" class="link-underline">đăng nhập</RouterLink> để tiếp tục thanh toán.</span>
        </div>

        <template v-if="isLoggedIn">
          <!-- Coupon code -->
          <div class="form-group">
            <label class="form-label">Mã giảm giá (tuỳ chọn)</label>
            <div class="coupon-row">
              <input
                v-model="couponCode"
                type="text"
                placeholder="VD: HOCTOT2026"
                class="coupon-input"
                :disabled="couponApplied || checkingCoupon"
                @keyup.enter="validateCoupon"
              />
              <button
                v-if="!couponApplied"
                class="coupon-btn"
                :disabled="!couponCode.trim() || checkingCoupon"
                @click="validateCoupon"
              >
                <span v-if="checkingCoupon" class="spinner"></span>
                <span v-else>Áp dụng</span>
              </button>
              <button v-else class="coupon-btn coupon-btn-remove" @click="removeCoupon">Xoá</button>
            </div>
            <p v-if="couponError" class="field-error">{{ couponError }}</p>
            <p v-if="couponApplied" class="field-success">✓ {{ discountData.discount_display }} đã được áp dụng!</p>
          </div>

          <!-- Payment gateway -->
          <div class="form-group">
            <label class="form-label">Phương thức thanh toán</label>
            <div class="gateway-grid">
              <button
                v-for="gw in gateways"
                :key="gw.id"
                class="gateway-btn"
                :class="{ 'gateway-active': selectedGateway === gw.id }"
                @click="selectedGateway = gw.id"
              >
                <span class="gw-icon">{{ gw.icon }}</span>
                <span class="gw-label">{{ gw.label }}</span>
                <span v-if="selectedGateway === gw.id" class="gw-check">✓</span>
              </button>
            </div>
          </div>

          <!-- Terms -->
          <label class="terms-row">
            <input type="checkbox" v-model="agreedTerms" class="terms-checkbox" />
            <span class="terms-text">Tôi đồng ý với <a href="#" class="link-underline">Điều khoản dịch vụ</a> và <a href="#" class="link-underline">Chính sách hoàn tiền</a></span>
          </label>

          <!-- Submit -->
          <button
            class="pay-btn"
            :class="{ 'pay-btn-gold': isYearly, 'pay-btn-primary': !isYearly }"
            :disabled="!canPay || paying"
            @click="doCheckout"
          >
            <span v-if="paying" class="pay-processing">
              <span class="spinner spinner-light"></span>
              Đang xử lý...
            </span>
            <span v-else>
              Thanh toán {{ finalPriceDisplay }}
              <span class="pay-icon">{{ selectedGateway === 'vnpay' ? '🏦' : '💳' }}</span>
            </span>
          </button>

          <!-- Processing overlay -->
          <Transition name="fade">
            <div v-if="redirecting" class="redirect-overlay">
              <div class="redirect-card">
                <div class="redirect-spinner"></div>
                <h3>Đang chuyển đến cổng thanh toán...</h3>
                <p>Vui lòng không đóng tab này.</p>
              </div>
            </div>
          </Transition>

          <p class="secure-note">🔒 Thanh toán được mã hóa SSL 256-bit. Dữ liệu thẻ không lưu trên máy chủ.</p>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { paymentsApi } from '@/api/payments.js'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const isLoggedIn = computed(() => auth.isLoggedIn)

// ── State ──────────────────────────────────────────────────────────────
const plan = ref(null)
const loadingPlan = ref(true)
const couponCode = ref('')
const couponApplied = ref(false)
const checkingCoupon = ref(false)
const couponError = ref('')
const discountData = ref(null)   // { discount_display, final_price_display }
const selectedGateway = ref('vnpay')
const agreedTerms = ref(false)
const paying = ref(false)
const redirecting = ref(false)

// ── Gateways ───────────────────────────────────────────────────────────
const gateways = [
  { id: 'vnpay',  icon: '🏦', label: 'VNPay' },
  { id: 'stripe', icon: '💳', label: 'Stripe / Thẻ quốc tế' },
]

// ── Computed ───────────────────────────────────────────────────────────
const planId = computed(() => route.params.planId)
const isYearly = computed(() => plan.value?.billing_period === 'yearly')

const periodLabel = computed(() => {
  const p = plan.value?.billing_period
  if (p === 'monthly') return 'Thanh toán hàng tháng'
  if (p === 'yearly')  return 'Thanh toán hàng năm'
  if (p === 'free')    return 'Miễn phí'
  return ''
})

const defaultFeatures = computed(() =>
  isYearly.value
    ? ['Không giới hạn khoá học', 'AI Grading Speaking & Writing', 'Flashcards SRS', 'Chứng chỉ', 'Priority Support 24/7']
    : ['Không giới hạn khoá học', 'AI Grading Speaking & Writing', 'Flashcards SRS', 'Chứng chỉ']
)

const finalPriceDisplay = computed(() =>
  discountData.value?.final_price_display || plan.value?.price_display || '—'
)

const discountAmountDisplay = computed(() => {
  if (!discountData.value || !plan.value) return ''
  const orig = Number(plan.value.price_vnd) || 0
  const final = Number(plan.value.price_vnd) || 0
  // Use final_price_display but we don't have discount_vnd directly — just show coupon label
  return discountData.value.discount_display
})

const canPay = computed(() =>
  !!plan.value && !!selectedGateway.value && agreedTerms.value && !paying.value
)

// ── Methods ───────────────────────────────────────────────────────────
async function loadPlan() {
  loadingPlan.value = true
  try {
    const res = await paymentsApi.getPlans()
    const d = res.data?.data ?? res.data
    const all = Array.isArray(d) ? d : (d?.results || [])
    console.log('[Checkout] Plans loaded:', all.length, 'planId param:', planId.value)
    // planId can be numeric id OR billing_period slug like "monthly"/"yearly"
    plan.value = all.find(p =>
      String(p.id) === String(planId.value) ||
      p.billing_period === planId.value ||
      p.name === planId.value
    ) || null
    console.log('[Checkout] Matched plan:', plan.value?.name_vi || 'NONE')
  } catch (err) {
    console.error('[Checkout] Failed to load plans:', err.response?.status, err.message)
    plan.value = null
  } finally {
    loadingPlan.value = false
  }
}

async function validateCoupon() {
  if (!couponCode.value.trim()) return
  couponError.value = ''
  checkingCoupon.value = true
  try {
    const res = await paymentsApi.validateCoupon(couponCode.value.trim(), plan.value.id)
    const d = res.data?.data ?? res.data
    discountData.value = d
    couponApplied.value = true
  } catch (err) {
    const msg = err.response?.data?.detail ||
                err.response?.data?.message ||
                'Mã giảm giá không hợp lệ.'
    couponError.value = msg
    discountData.value = null
  } finally {
    checkingCoupon.value = false
  }
}

function removeCoupon() {
  couponCode.value = ''
  couponApplied.value = false
  discountData.value = null
  couponError.value = ''
}

async function doCheckout() {
  if (!canPay.value) return
  paying.value = true
  try {
    const res = await paymentsApi.checkout(
      plan.value.id,
      selectedGateway.value,
      couponApplied.value ? couponCode.value.trim() : null
    )
    const d = res.data?.data ?? res.data
    const paymentUrl = d.payment_url
    if (paymentUrl) {
      redirecting.value = true
      // Small delay to show the processing state
      setTimeout(() => { window.location.href = paymentUrl }, 600)
    } else {
      alert('Không nhận được URL thanh toán. Vui lòng thử lại.')
      paying.value = false
    }
  } catch (err) {
    const msg = err.response?.data?.detail || 'Thanh toán thất bại. Vui lòng thử lại.'
    alert(msg)
    paying.value = false
  }
}

onMounted(loadPlan)
</script>

<style scoped>
/* ── Page wrapper ─────────────────────────────────────────────────── */
.checkout-page {
  min-height: 100vh;
  padding: 1.5rem 1rem 4rem;
  background: var(--color-bg, #0f1117);
  font-family: 'Inter', system-ui, sans-serif;
  max-width: 1000px;
  margin: 0 auto;
}

/* ── Back link ──────────────────────────────────────────────────────── */
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: var(--color-text-muted, #94a3b8);
  text-decoration: none;
  margin-bottom: 1.75rem;
  transition: color 0.15s;
}
.back-link:hover { color: var(--color-text-soft, #cbd5e1); }

/* ── Skeleton ───────────────────────────────────────────────────────── */
.checkout-skeleton { max-width: 860px; margin: 0 auto; }
.skel-block { background: var(--color-surface-02, #1e2130); }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
.animate-pulse { animation: pulse 1.5s ease-in-out infinite; }

/* ── Not found ──────────────────────────────────────────────────────── */
.not-found {
  text-align: center;
  padding: 5rem 1rem;
  color: var(--color-text-muted, #94a3b8);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  font-size: 1rem;
}

/* ── Two-column layout ──────────────────────────────────────────────── */
.checkout-layout {
  display: grid;
  grid-template-columns: 1fr 1.3fr;
  gap: 1.5rem;
  align-items: start;
}
@media (max-width: 700px) {
  .checkout-layout { grid-template-columns: 1fr; }
}

/* ── Order summary (left) ───────────────────────────────────────────── */
.order-summary {
  border-radius: 1.25rem;
  background: var(--color-surface-02, #1e2130);
  border: 1px solid var(--color-surface-04, #2d3348);
  padding: 1.75rem;
  position: relative;
  overflow: hidden;
}
.plan-gold {
  background-image:
    linear-gradient(var(--color-surface-02, #1e2130), var(--color-surface-02, #1e2130)),
    linear-gradient(135deg, #f59e0b, #fbbf24, #f59e0b);
  background-clip: padding-box, border-box;
  background-origin: border-box;
  border: 2px solid transparent;
}
.gold-banner {
  background: linear-gradient(135deg, #d97706, #fbbf24);
  color: #1a1400;
  font-size: 0.72rem;
  font-weight: 800;
  text-align: center;
  padding: 0.3rem;
  margin: -1.75rem -1.75rem 1.25rem;
  letter-spacing: 0.04em;
}
.summary-header {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  margin-bottom: 1.25rem;
}
.summary-icon { font-size: 2rem; }
.summary-plan-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-text-base, #f1f5f9);
}
.summary-period {
  font-size: 0.8rem;
  color: var(--color-text-muted, #94a3b8);
  margin-top: 0.2rem;
}
.summary-features {
  list-style: none;
  padding: 0;
  margin: 0 0 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.summary-feat {
  font-size: 0.83rem;
  color: var(--color-text-soft, #cbd5e1);
}
.price-breakdown {
  border-top: 1px solid var(--color-surface-04, #2d3348);
  padding-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}
.price-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.88rem;
  color: var(--color-text-soft, #cbd5e1);
}
.price-discount { color: #4ade80; }
.discount-amount { color: #4ade80; font-weight: 600; }
.price-total {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text-base, #f1f5f9);
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-surface-04, #2d3348);
  margin-top: 0.25rem;
}
.total-primary { color: #818cf8; }
.total-gold {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ── Form card (right) ──────────────────────────────────────────────── */
.checkout-form-card {
  border-radius: 1.25rem;
  background: var(--color-surface-02, #1e2130);
  border: 1px solid var(--color-surface-04, #2d3348);
  padding: 1.75rem;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.form-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-text-base, #f1f5f9);
  margin-bottom: 0.25rem;
}

/* ── Login notice ───────────────────────────────────────────────────── */
.login-notice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #6366f111;
  border: 1px solid #6366f133;
  border-radius: 0.75rem;
  padding: 0.85rem 1rem;
  font-size: 0.88rem;
  color: var(--color-text-soft, #cbd5e1);
}

/* ── Form group ─────────────────────────────────────────────────────── */
.form-group { display: flex; flex-direction: column; gap: 0.5rem; }
.form-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-text-muted, #94a3b8);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* ── Coupon ─────────────────────────────────────────────────────────── */
.coupon-row {
  display: flex;
  gap: 0.5rem;
}
.coupon-input {
  flex: 1;
  background: var(--color-surface-03, #252836);
  border: 1px solid var(--color-surface-04, #2d3348);
  border-radius: 0.65rem;
  padding: 0.65rem 0.9rem;
  color: var(--color-text-base, #f1f5f9);
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s;
  font-family: 'Inter', monospace;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.coupon-input:focus {
  border-color: #6366f1;
}
.coupon-input:disabled {
  opacity: 0.5;
}
.coupon-btn {
  padding: 0.65rem 1.1rem;
  border-radius: 0.65rem;
  background: #6366f1;
  color: #fff;
  border: none;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: opacity 0.15s;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.coupon-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.coupon-btn-remove {
  background: #dc262622;
  color: #f87171;
  border: 1px solid #dc262655;
}
.field-error { font-size: 0.8rem; color: #f87171; }
.field-success { font-size: 0.8rem; color: #4ade80; font-weight: 600; }

/* ── Gateway ────────────────────────────────────────────────────────── */
.gateway-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.gateway-btn {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.9rem 1rem;
  border-radius: 0.75rem;
  border: 1.5px solid var(--color-surface-04, #2d3348);
  background: var(--color-surface-03, #252836);
  color: var(--color-text-soft, #cbd5e1);
  cursor: pointer;
  font-size: 0.88rem;
  font-weight: 500;
  position: relative;
  transition: border-color 0.2s, background 0.2s;
}
.gateway-active {
  border-color: #6366f1;
  background: #6366f111;
  color: #a5b4fc;
}
.gw-icon { font-size: 1.15rem; }
.gw-label { flex: 1; font-size: 0.85rem; }
.gw-check { color: #818cf8; font-weight: 700; font-size: 0.9rem; }

/* ── Terms ──────────────────────────────────────────────────────────── */
.terms-row {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  cursor: pointer;
}
.terms-checkbox {
  margin-top: 0.15rem;
  accent-color: #6366f1;
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
  cursor: pointer;
}
.terms-text {
  font-size: 0.82rem;
  color: var(--color-text-muted, #94a3b8);
  line-height: 1.5;
}

/* ── Pay button ─────────────────────────────────────────────────────── */
.pay-btn {
  width: 100%;
  padding: 0.95rem;
  border-radius: 0.85rem;
  border: none;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
}
.pay-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
.pay-btn:not(:disabled):hover { opacity: 0.9; transform: translateY(-1px); }
.pay-btn-primary { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; }
.pay-btn-gold    { background: linear-gradient(135deg, #d97706, #fbbf24); color: #1a1400; }
.pay-icon { font-size: 1.1rem; }
.pay-processing { display: flex; align-items: center; gap: 0.5rem; }

/* ── Spinner ─────────────────────────────────────────────────────────── */
.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
.spinner-light {
  border-color: rgba(255,255,255,0.3);
  border-top-color: #fff;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Redirect overlay ────────────────────────────────────────────────── */
.redirect-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.72);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}
.redirect-card {
  background: var(--color-surface-02, #1e2130);
  border-radius: 1.25rem;
  padding: 2.5rem 3rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  min-width: 280px;
}
.redirect-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #6366f133;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
.redirect-card h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text-base, #f1f5f9);
}
.redirect-card p {
  font-size: 0.85rem;
  color: var(--color-text-muted, #94a3b8);
}

/* ── Secure note ─────────────────────────────────────────────────────── */
.secure-note {
  font-size: 0.75rem;
  color: var(--color-text-muted, #64748b);
  text-align: center;
}

/* ── Links ───────────────────────────────────────────────────────────── */
.link-underline {
  color: #818cf8;
  text-decoration: underline;
  text-underline-offset: 2px;
}

/* ── Transition ──────────────────────────────────────────────────────── */
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
