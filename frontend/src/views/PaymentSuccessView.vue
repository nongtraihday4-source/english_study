<template>
  <div class="success-page">
    <!-- Confetti canvas -->
    <canvas ref="confettiCanvas" class="confetti-canvas" aria-hidden="true"></canvas>

    <!-- Card -->
    <div class="success-card" :class="{ 'card-visible': visible }">
      <!-- Trophy animation -->
      <div class="trophy-wrap">
        <div class="trophy-ring ring-1"></div>
        <div class="trophy-ring ring-2"></div>
        <div class="trophy-ring ring-3"></div>
        <div class="trophy-emoji">🎉</div>
      </div>

      <div class="success-content">
        <div class="badge-premium">✨ Tài khoản Premium</div>
        <h1 class="success-title">Thanh toán thành công!</h1>
        <p class="success-sub">
          Tài khoản của bạn đã được nâng cấp lên <strong class="highlight">Premium</strong>.
          Toàn bộ khoá học, AI Grading và Flashcards đã được mở khoá!
        </p>

        <!-- Divider -->
        <div class="features-unlocked">
          <div class="unlock-item" v-for="feat in unlockedFeatures" :key="feat.label">
            <span class="unlock-icon">{{ feat.icon }}</span>
            <span class="unlock-label">{{ feat.label }}</span>
          </div>
        </div>

        <!-- Loading state while refreshing user -->
        <div v-if="refreshing" class="refreshing-row">
          <span class="spinner-sm"></span>
          <span class="refreshing-text">Đang cập nhật tài khoản...</span>
        </div>

        <!-- Actions -->
        <div v-else class="action-row">
          <RouterLink to="/courses" class="btn-start">
            🚀 Bắt đầu học ngay
          </RouterLink>
          <RouterLink to="/dashboard" class="btn-dash">
            Xem Dashboard
          </RouterLink>
        </div>

        <p class="receipt-note">
          Biên lai đã được gửi đến email của bạn. Có thắc mắc? <a href="mailto:support@english-study.vn" class="link-email">Liên hệ hỗ trợ</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'

const auth = useAuthStore()
const confettiCanvas = ref(null)
const visible = ref(false)
const refreshing = ref(true)
let animFrame = null
let confettiParticles = []

const unlockedFeatures = [
  { icon: '🎙️', label: 'AI Grading Speaking' },
  { icon: '✍️',  label: 'AI Grading Writing' },
  { icon: '🃏',  label: 'Flashcards SRS' },
  { icon: '🏅',  label: 'Chứng chỉ' },
  { icon: '🎧',  label: 'Priority Support' },
]

// ── Confetti ───────────────────────────────────────────────────────────
const COLORS = ['#6366f1', '#8b5cf6', '#f59e0b', '#fbbf24', '#4ade80', '#f472b6', '#38bdf8']

function randomBetween(min, max) { return Math.random() * (max - min) + min }

function initParticle(canvas) {
  return {
    x: randomBetween(0, canvas.width),
    y: randomBetween(-100, -10),
    w: randomBetween(6, 14),
    h: randomBetween(8, 18),
    color: COLORS[Math.floor(Math.random() * COLORS.length)],
    rotation: randomBetween(0, Math.PI * 2),
    rotationSpeed: randomBetween(-0.08, 0.08),
    speedX: randomBetween(-2, 2),
    speedY: randomBetween(2.5, 6),
    alpha: 1,
    shape: Math.random() > 0.5 ? 'rect' : 'circle',
  }
}

function startConfetti() {
  const canvas = confettiCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  canvas.width  = window.innerWidth
  canvas.height = window.innerHeight

  confettiParticles = Array.from({ length: 160 }, () => initParticle(canvas))

  let frame = 0
  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    confettiParticles.forEach((p, i) => {
      p.x += p.speedX
      p.y += p.speedY
      p.rotation += p.rotationSpeed
      if (frame > 160) p.alpha = Math.max(0, p.alpha - 0.008)

      ctx.save()
      ctx.globalAlpha = p.alpha
      ctx.translate(p.x, p.y)
      ctx.rotate(p.rotation)
      ctx.fillStyle = p.color
      if (p.shape === 'rect') {
        ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h)
      } else {
        ctx.beginPath()
        ctx.arc(0, 0, p.w / 2, 0, Math.PI * 2)
        ctx.fill()
      }
      ctx.restore()

      // Recycle
      if (p.y > canvas.height + 20 && frame < 200) {
        confettiParticles[i] = initParticle(canvas)
      }
    })
    frame++
    if (frame < 350) animFrame = requestAnimationFrame(draw)
    else ctx.clearRect(0, 0, canvas.width, canvas.height)
  }
  draw()
}

// ── Lifecycle ──────────────────────────────────────────────────────────
onMounted(async () => {
  // Refresh user session to get updated account_type
  try {
    await auth.refreshUser()
  } finally {
    refreshing.value = false
  }

  // Trigger card entrance
  requestAnimationFrame(() => { visible.value = true })

  // Start confetti after short delay
  setTimeout(startConfetti, 300)
})

onUnmounted(() => {
  if (animFrame) cancelAnimationFrame(animFrame)
})
</script>

<style scoped>
/* ── Page ────────────────────────────────────────────────────────────── */
.success-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  background: var(--color-bg, #0f1117);
  font-family: 'Inter', system-ui, sans-serif;
  position: relative;
  overflow: hidden;
}

/* ── Confetti canvas ─────────────────────────────────────────────────── */
.confetti-canvas {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

/* ── Card ────────────────────────────────────────────────────────────── */
.success-card {
  position: relative;
  z-index: 1;
  background: var(--color-surface-02, #1e2130);
  border: 1px solid var(--color-surface-04, #2d3348);
  border-radius: 1.75rem;
  padding: 2.5rem 2rem;
  max-width: 520px;
  width: 100%;
  text-align: center;
  box-shadow: 0 32px 80px rgba(99, 102, 241, 0.2);
  opacity: 0;
  transform: scale(0.9) translateY(20px);
  transition: opacity 0.5s ease, transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.card-visible {
  opacity: 1;
  transform: scale(1) translateY(0);
}

/* ── Trophy animation ────────────────────────────────────────────────── */
.trophy-wrap {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.trophy-ring {
  position: absolute;
  border-radius: 50%;
  border: 2px solid;
  animation: ripple 2s ease-out infinite;
}
.ring-1 {
  width: 100px;
  height: 100px;
  border-color: #6366f155;
  animation-delay: 0s;
}
.ring-2 {
  width: 80px;
  height: 80px;
  border-color: #6366f188;
  animation-delay: 0.3s;
}
.ring-3 {
  width: 60px;
  height: 60px;
  border-color: #6366f1bb;
  animation-delay: 0.6s;
}
@keyframes ripple {
  0%  { transform: scale(0.8); opacity: 1; }
  100%{ transform: scale(1.4); opacity: 0; }
}
.trophy-emoji {
  font-size: 3rem;
  z-index: 1;
  animation: bounce 1s cubic-bezier(0.34, 1.56, 0.64, 1) 0.4s both;
}
@keyframes bounce {
  from { transform: scale(0.5) rotate(-10deg); opacity: 0; }
  to   { transform: scale(1) rotate(0deg); opacity: 1; }
}

/* ── Content ─────────────────────────────────────────────────────────── */
.success-content { display: flex; flex-direction: column; align-items: center; gap: 1rem; }

.badge-premium {
  display: inline-block;
  padding: 0.3rem 1rem;
  border-radius: 999px;
  background: linear-gradient(135deg, #f59e0b22, #fbbf2422);
  border: 1px solid #f59e0b55;
  color: #fbbf24;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}
.success-title {
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: 800;
  background: linear-gradient(135deg, #a78bfa, #f59e0b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
}
.success-sub {
  font-size: 0.95rem;
  color: var(--color-text-soft, #cbd5e1);
  line-height: 1.65;
  max-width: 400px;
}
.highlight {
  color: #fbbf24;
  font-weight: 700;
}

/* ── Unlocked features ───────────────────────────────────────────────── */
.features-unlocked {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  justify-content: center;
  background: var(--color-surface-03, #252836);
  border-radius: 1rem;
  padding: 1rem 1.25rem;
  width: 100%;
}
.unlock-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.82rem;
  color: var(--color-text-soft, #cbd5e1);
  background: var(--color-surface-04, #2d3348);
  border-radius: 999px;
  padding: 0.3rem 0.8rem;
}
.unlock-icon { font-size: 0.95rem; }

/* ── Refreshing row ──────────────────────────────────────────────────── */
.refreshing-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: var(--color-text-muted, #94a3b8);
  font-size: 0.85rem;
}
.spinner-sm {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(99,102,241,0.25);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Actions ─────────────────────────────────────────────────────────── */
.action-row {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: center;
  width: 100%;
}
.btn-start,
.btn-dash {
  padding: 0.8rem 1.5rem;
  border-radius: 0.75rem;
  font-size: 0.95rem;
  font-weight: 700;
  text-decoration: none;
  transition: opacity 0.15s, transform 0.15s;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}
.btn-start:hover, .btn-dash:hover { opacity: 0.88; transform: translateY(-2px); }
.btn-start {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
}
.btn-dash {
  background: var(--color-surface-03, #252836);
  color: var(--color-text-soft, #cbd5e1);
  border: 1px solid var(--color-surface-04, #2d3348);
}

/* ── Receipt note ────────────────────────────────────────────────────── */
.receipt-note {
  font-size: 0.78rem;
  color: var(--color-text-muted, #64748b);
  line-height: 1.5;
}
.link-email {
  color: #818cf8;
  text-decoration: underline;
  text-underline-offset: 2px;
}
</style>
