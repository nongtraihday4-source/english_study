<template>
  <div class="pricing-page">
    <!-- Hero -->
    <div class="pricing-hero">
      <div class="hero-badge">💎 Nâng cấp tài khoản</div>
      <h1 class="hero-title">Chọn gói học phù hợp với bạn</h1>
      <p class="hero-sub">Học tiếng Anh toàn diện với AI grading, Flashcards SRS và chứng chỉ quốc tế</p>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="plans-grid">
      <div v-for="i in 3" :key="i" class="plan-skeleton animate-pulse"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-state">
      <span class="text-4xl">⚠️</span>
      <p>{{ error }}</p>
      <button @click="loadPlans" class="btn-retry">Thử lại</button>
    </div>

    <!-- Plans Grid -->
    <div v-else class="plans-grid">
      <!-- FREE / Demo card -->
      <div class="plan-card">
        <div class="plan-header">
          <div class="plan-icon">🎓</div>
          <h2 class="plan-name">Demo</h2>
          <p class="plan-desc">Trải nghiệm miễn phí</p>
        </div>
        <div class="plan-price-block">
          <span class="plan-price">Miễn phí</span>
        </div>
        <ul class="plan-features">
          <li class="feature-item feature-yes">✓ 2 khoá học cấp A1</li>
          <li class="feature-item feature-yes">✓ Bài tập cơ bản</li>
          <li class="feature-item feature-no">✗ AI Grading Speaking</li>
          <li class="feature-item feature-no">✗ Flashcards SRS</li>
          <li class="feature-item feature-no">✗ Chứng chỉ</li>
          <li class="feature-item feature-no">✗ Priority Support</li>
        </ul>
        <RouterLink to="/register" class="plan-cta plan-cta-ghost">Bắt đầu miễn phí</RouterLink>
      </div>

      <!-- MONTHLY plan (from API or fallback) -->
      <div class="plan-card" v-for="plan in [monthlyPlan].filter(Boolean)" :key="'monthly-'+plan.id">
        <div class="plan-header">
          <div class="plan-icon">⚡</div>
          <h2 class="plan-name">{{ plan.name_vi }}</h2>
          <p class="plan-desc">Truy cập toàn bộ nội dung</p>
        </div>
        <div class="plan-price-block">
          <span class="plan-price">{{ plan.price_display }}</span>
          <span class="plan-period">/tháng</span>
          <div v-if="plan.original_price_display" class="plan-original">
            <span class="strikethrough">{{ plan.original_price_display }}</span>
          </div>
        </div>
        <ul class="plan-features">
          <li class="feature-item feature-yes">✓ Không giới hạn khoá học</li>
          <li class="feature-item feature-yes">✓ AI Grading Speaking & Writing</li>
          <li class="feature-item feature-yes">✓ Flashcards SRS</li>
          <li class="feature-item feature-yes">✓ Chứng chỉ hoàn thành</li>
          <li class="feature-item feature-no">✗ Priority Support</li>
        </ul>
        <button @click="goCheckout(plan.id)" class="plan-cta plan-cta-primary">Đăng ký ngay</button>
      </div>

      <!-- YEARLY plan (popular) -->
      <div class="plan-card plan-card-popular" v-for="plan in [yearlyPlan].filter(Boolean)" :key="'yearly-'+plan.id">
        <div class="popular-badge">🏆 Phổ biến nhất</div>
        <div class="plan-header">
          <div class="plan-icon plan-icon-gold">👑</div>
          <h2 class="plan-name">{{ plan.name_vi }}</h2>
          <p class="plan-desc">Tiết kiệm nhất — {{ plan.discount_percent || '37%' }} off</p>
        </div>
        <div class="plan-price-block">
          <span class="plan-price plan-price-gold">{{ plan.price_display }}</span>
          <span class="plan-period">/năm</span>
          <div v-if="plan.original_price_display" class="plan-original">
            <span class="strikethrough">{{ plan.original_price_display }}</span>
            <span class="saving-badge">Tiết kiệm {{ plan.discount_percent || '37%' }}</span>
          </div>
        </div>
        <ul class="plan-features">
          <li class="feature-item feature-yes">✓ Không giới hạn khoá học</li>
          <li class="feature-item feature-yes">✓ AI Grading Speaking & Writing</li>
          <li class="feature-item feature-yes">✓ Flashcards SRS nâng cao</li>
          <li class="feature-item feature-yes">✓ Chứng chỉ hoàn thành</li>
          <li class="feature-item feature-yes">✓ Priority Support 24/7</li>
        </ul>
        <button @click="goCheckout(plan.id)" class="plan-cta plan-cta-gold">Đăng ký ngay ✨</button>
      </div>

      <!-- Fallback static cards if API has no yearly/monthly -->
      <template v-if="!monthlyPlan">
        <div class="plan-card">
          <div class="plan-header">
            <div class="plan-icon">⚡</div>
            <h2 class="plan-name">Gói Tháng</h2>
            <p class="plan-desc">Truy cập toàn bộ nội dung</p>
          </div>
          <div class="plan-price-block">
            <span class="plan-price">199.000 ₫</span>
            <span class="plan-period">/tháng</span>
          </div>
          <ul class="plan-features">
            <li class="feature-item feature-yes">✓ Không giới hạn khoá học</li>
            <li class="feature-item feature-yes">✓ AI Grading Speaking & Writing</li>
            <li class="feature-item feature-yes">✓ Flashcards SRS</li>
            <li class="feature-item feature-yes">✓ Chứng chỉ hoàn thành</li>
            <li class="feature-item feature-no">✗ Priority Support</li>
          </ul>
          <RouterLink to="/checkout/monthly" class="plan-cta plan-cta-primary">Đăng ký ngay</RouterLink>
        </div>
      </template>
      <template v-if="!yearlyPlan">
        <div class="plan-card plan-card-popular">
          <div class="popular-badge">🏆 Phổ biến nhất</div>
          <div class="plan-header">
            <div class="plan-icon plan-icon-gold">👑</div>
            <h2 class="plan-name">Gói Năm</h2>
            <p class="plan-desc">Tiết kiệm nhất — 37% off</p>
          </div>
          <div class="plan-price-block">
            <span class="plan-price plan-price-gold">1.499.000 ₫</span>
            <span class="plan-period">/năm</span>
            <div class="plan-original">
              <span class="strikethrough">2.388.000 ₫</span>
              <span class="saving-badge">Tiết kiệm 37%</span>
            </div>
          </div>
          <ul class="plan-features">
            <li class="feature-item feature-yes">✓ Không giới hạn khoá học</li>
            <li class="feature-item feature-yes">✓ AI Grading Speaking & Writing</li>
            <li class="feature-item feature-yes">✓ Flashcards SRS nâng cao</li>
            <li class="feature-item feature-yes">✓ Chứng chỉ hoàn thành</li>
            <li class="feature-item feature-yes">✓ Priority Support 24/7</li>
          </ul>
          <RouterLink to="/checkout/yearly" class="plan-cta plan-cta-gold">Đăng ký ngay ✨</RouterLink>
        </div>
      </template>
    </div>

    <!-- Feature Comparison Table -->
    <div class="comparison-section">
      <h2 class="comparison-title">So sánh chi tiết tính năng</h2>
      <div class="comparison-wrapper">
        <table class="comparison-table">
          <thead>
            <tr>
              <th class="feature-col">Tính năng</th>
              <th>Demo</th>
              <th>Tháng</th>
              <th class="col-popular">Năm ⭐</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in featureRows" :key="row.name">
              <td class="feature-name">
                <span class="feature-icon">{{ row.icon }}</span>
                {{ row.name }}
              </td>
              <td><span :class="row.free ? 'check' : 'cross'">{{ row.free ? '✓' : '✗' }}</span></td>
              <td><span :class="row.monthly ? 'check' : 'cross'">{{ row.monthly ? '✓' : '✗' }}</span></td>
              <td class="col-popular"><span :class="row.yearly ? 'check' : 'cross'">{{ row.yearly ? '✓' : '✗' }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- CTA Footer -->
    <div class="cta-footer">
      <p class="cta-footer-text">🔒 Thanh toán bảo mật qua VNPay &amp; Stripe. Hoàn tiền trong 7 ngày nếu không hài lòng.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { paymentsApi } from '@/api/payments.js'

const router = useRouter()
const plans = ref([])
const loading = ref(false)
const error = ref('')

const monthlyPlan = computed(() => plans.value.find(p => p.billing_period === 'monthly'))
const yearlyPlan  = computed(() => plans.value.find(p => p.billing_period === 'yearly'))

const featureRows = [
  { icon: '📚', name: 'Số khoá học',        free: false, monthly: true,  yearly: true  },
  { icon: '🎙️', name: 'AI Grading Speaking', free: false, monthly: true,  yearly: true  },
  { icon: '✍️',  name: 'AI Grading Writing',  free: false, monthly: true,  yearly: true  },
  { icon: '🃏', name: 'Flashcards SRS',      free: false, monthly: true,  yearly: true  },
  { icon: '🏅', name: 'Certificate',         free: false, monthly: true,  yearly: true  },
  { icon: '🎧', name: 'Priority Support',    free: false, monthly: false, yearly: true  },
  { icon: '📊', name: 'Báo cáo chi tiết',    free: false, monthly: true,  yearly: true  },
  { icon: '🔒', name: 'Bài thi đánh giá',    free: false, monthly: true,  yearly: true  },
]

async function loadPlans() {
  loading.value = true
  error.value = ''
  try {
    const res = await paymentsApi.getPlans()
    const d = res.data?.data ?? res.data
    plans.value = Array.isArray(d) ? d : (d?.results || [])
  } catch {
    error.value = 'Không thể tải gói học. Vui lòng thử lại.'
  } finally {
    loading.value = false
  }
}

function goCheckout(planId) {
  router.push(`/checkout/${planId}`)
}

onMounted(loadPlans)
</script>

<style scoped>
/* ── Page layout ─────────────────────────────────────────────────────── */
.pricing-page {
  min-height: 100vh;
  padding: 2rem 1rem 4rem;
  background: var(--color-bg, #0f1117);
  font-family: 'Inter', system-ui, sans-serif;
}

/* ── Hero ───────────────────────────────────────────────────────────── */
.pricing-hero {
  text-align: center;
  margin-bottom: 3rem;
  padding-top: 1rem;
}
.hero-badge {
  display: inline-block;
  padding: 0.35rem 1rem;
  border-radius: 999px;
  background: linear-gradient(135deg, #7c3aed22, #f59e0b22);
  border: 1px solid #f59e0b55;
  color: #fbbf24;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
}
.hero-title {
  font-size: clamp(1.8rem, 4vw, 2.8rem);
  font-weight: 800;
  color: var(--color-text-base, #f1f5f9);
  margin-bottom: 0.75rem;
  background: linear-gradient(135deg, #a78bfa, #f59e0b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-sub {
  font-size: 1rem;
  color: var(--color-text-muted, #94a3b8);
  max-width: 560px;
  margin: 0 auto;
  line-height: 1.6;
}

/* ── Plans grid ─────────────────────────────────────────────────────── */
.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  max-width: 1100px;
  margin: 0 auto 3.5rem;
}

/* ── Plan card ──────────────────────────────────────────────────────── */
.plan-card {
  position: relative;
  background: var(--color-surface-02, #1e2130);
  border: 1px solid var(--color-surface-04, #2d3348);
  border-radius: 1.25rem;
  padding: 2rem 1.75rem 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  transition: transform 0.2s, box-shadow 0.2s;
}
.plan-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 48px rgba(0,0,0,0.4);
}
.plan-card-popular {
  border: 2px solid transparent;
  background-clip: padding-box;
  position: relative;
  box-shadow: 0 0 0 2px transparent;
  background-image: linear-gradient(var(--color-surface-02, #1e2130), var(--color-surface-02, #1e2130)),
                    linear-gradient(135deg, #f59e0b, #fbbf24, #f59e0b);
  background-origin: border-box;
  background-clip: padding-box, border-box;
  border: 2px solid transparent;
}
.popular-badge {
  position: absolute;
  top: -0.9rem;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #d97706, #fbbf24);
  color: #1a1400;
  font-size: 0.72rem;
  font-weight: 800;
  padding: 0.3rem 1rem;
  border-radius: 999px;
  white-space: nowrap;
  letter-spacing: 0.04em;
}

/* ── Plan header ────────────────────────────────────────────────────── */
.plan-header { text-align: center; }
.plan-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.plan-icon-gold { filter: drop-shadow(0 0 8px #f59e0b88); }
.plan-name {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--color-text-base, #f1f5f9);
}
.plan-desc {
  font-size: 0.82rem;
  color: var(--color-text-muted, #94a3b8);
  margin-top: 0.25rem;
}

/* ── Price block ────────────────────────────────────────────────────── */
.plan-price-block { text-align: center; }
.plan-price {
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-text-base, #f1f5f9);
}
.plan-price-gold {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.plan-period {
  font-size: 0.9rem;
  color: var(--color-text-muted, #94a3b8);
  margin-left: 0.25rem;
}
.plan-original {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.35rem;
}
.strikethrough {
  font-size: 0.82rem;
  color: var(--color-text-muted, #94a3b8);
  text-decoration: line-through;
}
.saving-badge {
  font-size: 0.72rem;
  background: #16a34a22;
  color: #4ade80;
  border: 1px solid #16a34a55;
  border-radius: 999px;
  padding: 0.15rem 0.5rem;
  font-weight: 600;
}

/* ── Features list ──────────────────────────────────────────────────── */
.plan-features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}
.feature-item {
  font-size: 0.85rem;
  padding: 0.25rem 0;
}
.feature-yes { color: var(--color-text-soft, #cbd5e1); }
.feature-no  { color: var(--color-text-muted, #64748b); }

/* ── CTA buttons ───────────────────────────────────────────────────── */
.plan-cta {
  display: block;
  width: 100%;
  text-align: center;
  padding: 0.8rem 1rem;
  border-radius: 0.75rem;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  border: none;
  transition: opacity 0.15s, transform 0.15s;
}
.plan-cta:hover { opacity: 0.88; transform: scale(1.02); }
.plan-cta-ghost {
  background: var(--color-surface-04, #2d3348);
  color: var(--color-text-soft, #cbd5e1);
  border: 1px solid var(--color-surface-04, #2d3348);
}
.plan-cta-primary {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
}
.plan-cta-gold {
  background: linear-gradient(135deg, #d97706, #fbbf24);
  color: #1a1400;
}

/* ── Skeleton ───────────────────────────────────────────────────────── */
.plan-skeleton {
  height: 420px;
  border-radius: 1.25rem;
  background: var(--color-surface-02, #1e2130);
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
.animate-pulse { animation: pulse 1.5s ease-in-out infinite; }

/* ── Error state ────────────────────────────────────────────────────── */
.error-state {
  text-align: center;
  padding: 4rem 1rem;
  color: var(--color-text-muted, #94a3b8);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
.btn-retry {
  padding: 0.5rem 1.5rem;
  background: #6366f1;
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 600;
}

/* ── Comparison table ───────────────────────────────────────────────── */
.comparison-section {
  max-width: 860px;
  margin: 0 auto 2rem;
}
.comparison-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--color-text-base, #f1f5f9);
  text-align: center;
  margin-bottom: 1.5rem;
}
.comparison-wrapper {
  overflow-x: auto;
  border-radius: 1rem;
  border: 1px solid var(--color-surface-04, #2d3348);
}
.comparison-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--color-surface-02, #1e2130);
}
.comparison-table th,
.comparison-table td {
  padding: 0.85rem 1.25rem;
  text-align: center;
  border-bottom: 1px solid var(--color-surface-04, #2d3348);
  font-size: 0.88rem;
}
.comparison-table th {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--color-text-muted, #94a3b8);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--color-surface-03, #252836);
}
.feature-col { text-align: left; width: 40%; }
.feature-name {
  text-align: left;
  color: var(--color-text-soft, #cbd5e1);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.feature-icon { width: 1.2em; }
.col-popular {
  background: linear-gradient(180deg, #f59e0b0a, transparent);
  color: #fbbf24 !important;
}
.check { color: #4ade80; font-weight: 700; font-size: 1rem; }
.cross { color: #475569; font-size: 1rem; }
.comparison-table tbody tr:last-child td { border-bottom: none; }
.comparison-table tbody tr:hover td {
  background: var(--color-surface-03, #252836);
}

/* ── CTA Footer ─────────────────────────────────────────────────────── */
.cta-footer { text-align: center; margin-top: 2rem; }
.cta-footer-text {
  font-size: 0.82rem;
  color: var(--color-text-muted, #64748b);
}
</style>
