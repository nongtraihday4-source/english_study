<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold" style="color: var(--color-text-base)">📜 Chứng chỉ</h1>
      <p class="mt-1" style="color: var(--color-text-muted)">
        Chứng chỉ hoàn thành khoá học của bạn
      </p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-24">
      <div class="h-10 w-10 animate-spin rounded-full border-4 border-yellow-300 border-t-yellow-600" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="rounded-xl bg-red-50 dark:bg-red-900/20 p-6 text-center text-red-600 dark:text-red-400">
      {{ error }}
    </div>

    <!-- Empty state -->
    <div
      v-else-if="certificates.length === 0"
      class="flex flex-col items-center justify-center py-24 text-center"
    >
      <div class="text-7xl mb-4">🎓</div>
      <h2 class="text-xl font-semibold" style="color: var(--color-text-base)">Chưa có chứng chỉ nào</h2>
      <p class="mt-2 max-w-sm" style="color: var(--color-text-muted)">
        Hoàn thành khoá học để nhận chứng chỉ. Mỗi chứng chỉ chứng nhận trình độ của bạn!
      </p>
      <a
        href="/courses"
        class="mt-6 inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-white font-medium hover:bg-indigo-700 transition-colors"
      >
        📚 Xem khoá học
      </a>
    </div>

    <!-- Certificate grid -->
    <div v-else class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="cert in certificates"
        :key="cert.id"
        :class="[
          'relative overflow-hidden rounded-2xl p-6 shadow-lg',
          gradientFor(cert.level_name),
        ]"
      >
        <!-- Decorative circle -->
        <div class="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-white/10" />
        <div class="absolute -bottom-6 -left-6 h-24 w-24 rounded-full bg-white/10" />

        <!-- Level badge -->
        <div class="relative z-10 mb-4 inline-flex items-center gap-1.5 rounded-full bg-white/20 px-3 py-1 text-sm font-bold text-white backdrop-blur-sm">
          {{ levelEmoji(cert.level_name) }} {{ cert.level_name || 'N/A' }}
        </div>

        <!-- Course title -->
        <h3 class="relative z-10 text-xl font-bold text-white leading-tight mb-1">
          {{ cert.course_title || 'Khoá học' }}
        </h3>

        <!-- Issued date -->
        <p class="relative z-10 text-white/80 text-sm mb-4">
          Cấp ngày {{ formatDate(cert.issued_at) }}
        </p>

        <!-- Verification code -->
        <div class="relative z-10 mb-4 flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 backdrop-blur-sm">
          <span class="text-white/70 text-xs">Mã xác nhận:</span>
          <span class="font-mono text-xs font-semibold text-white tracking-wide truncate">
            {{ truncateCode(cert.verification_code) }}
          </span>
          <button
            @click="copyCode(cert.verification_code)"
            class="ml-auto text-white/70 hover:text-white transition-colors text-xs"
            title="Sao chép mã"
          >
            {{ copiedId === cert.id ? '✓' : '⎘' }}
          </button>
        </div>

        <!-- Download button -->
        <div class="relative z-10">
          <a
            v-if="cert.pdf_s3_key"
            :href="downloadUrl(cert)"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-white/20 hover:bg-white/30 px-4 py-2.5 text-sm font-semibold text-white transition-colors backdrop-blur-sm"
          >
            ⬇️ Tải chứng chỉ PDF
          </a>
          <button
            v-else
            disabled
            class="w-full cursor-not-allowed rounded-lg bg-white/10 px-4 py-2.5 text-sm font-semibold text-white/50"
          >
            PDF chưa sẵn sàng
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { gamificationApi } from '@/api/gamification'

const certificates = ref([])
const loading = ref(true)
const error = ref(null)
const copiedId = ref(null)

// Map CEFR level name to gradient class
function gradientFor(levelName) {
  const l = (levelName || '').toUpperCase()
  if (l.includes('C2')) return 'bg-gradient-to-br from-yellow-500 via-amber-500 to-orange-600'
  if (l.includes('C1')) return 'bg-gradient-to-br from-yellow-400 via-amber-400 to-yellow-600'
  if (l.includes('B2')) return 'bg-gradient-to-br from-slate-400 via-gray-400 to-slate-500'
  if (l.includes('B1')) return 'bg-gradient-to-br from-indigo-500 via-purple-500 to-indigo-700'
  if (l.includes('A2')) return 'bg-gradient-to-br from-teal-400 via-cyan-500 to-teal-600'
  return 'bg-gradient-to-br from-blue-500 via-blue-400 to-indigo-600'
}

function levelEmoji(levelName) {
  const l = (levelName || '').toUpperCase()
  if (l.includes('C2')) return '👑'
  if (l.includes('C1')) return '💎'
  if (l.includes('B2')) return '🥈'
  if (l.includes('B1')) return '🥉'
  return '🎯'
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function truncateCode(code) {
  if (!code) return '—'
  return code.length > 16 ? code.slice(0, 8) + '…' + code.slice(-6) : code
}

function downloadUrl(cert) {
  // If pdf_s3_key is a full URL use directly; otherwise treat as relative API path
  if (cert.pdf_s3_key.startsWith('http')) return cert.pdf_s3_key
  return `/api/v1/gamification/certificates/${cert.id}/download/`
}

async function copyCode(code) {
  if (!code) return
  try {
    await navigator.clipboard.writeText(code)
    copiedId.value = code
    setTimeout(() => (copiedId.value = null), 2000)
  } catch {}
}

onMounted(async () => {
  try {
    const res = await gamificationApi.getCertificates()
    const data = res.data?.data ?? res.data
    certificates.value = Array.isArray(data) ? data : []
  } catch (e) {
    error.value = 'Không thể tải danh sách chứng chỉ. Vui lòng thử lại.'
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>
