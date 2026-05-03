<template>
  <footer style="background-color: var(--color-secondary); color: #e2e8f0">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">

        <!-- Brand column -->
        <div class="lg:col-span-1">
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 rounded-lg flex items-center justify-center text-white font-black text-sm"
                 style="background: var(--color-primary-500)">ES</div>
            <span class="font-black text-lg" style="font-family: var(--font-heading)">
              English<span style="color: var(--color-primary-500)">Study</span>
            </span>
          </div>
          <p class="text-sm leading-relaxed mb-5" style="color: #94a3b8">
            Nền tảng học tiếng Anh trực tuyến với AI. Chinh phục 4 kỹ năng, đạt trình độ giao tiếp thực chiến.
          </p>
          <div class="flex gap-3">
            <a v-for="s in socials" :key="s.label" :href="s.href"
               class="w-8 h-8 rounded-lg flex items-center justify-center text-sm transition hover:opacity-70"
               style="background-color: rgba(255,255,255,0.1)"
               :title="s.label">{{ s.icon }}</a>
          </div>
        </div>

        <!-- Courses -->
        <div>
          <h3 class="font-bold text-white mb-4 text-sm uppercase tracking-wider"
              style="font-family: var(--font-heading)">Khoá học</h3>
          <ul class="space-y-2">
            <li v-for="item in footerLinks.courses" :key="item.label">
              <RouterLink :to="item.to"
                class="text-sm transition hover:text-white"
                style="color: #94a3b8">{{ item.label }}</RouterLink>
            </li>
          </ul>
        </div>

        <!-- Company -->
        <div>
          <h3 class="font-bold text-white mb-4 text-sm uppercase tracking-wider"
              style="font-family: var(--font-heading)">Về chúng tôi</h3>
          <ul class="space-y-2">
            <li v-for="item in footerLinks.company" :key="item.label">
              <RouterLink :to="item.to"
                class="text-sm transition hover:text-white"
                style="color: #94a3b8">{{ item.label }}</RouterLink>
            </li>
          </ul>
        </div>

        <!-- Contact -->
        <div>
          <h3 class="font-bold text-white mb-4 text-sm uppercase tracking-wider"
              style="font-family: var(--font-heading)">Hỗ trợ</h3>
          <ul class="space-y-2.5">
            <li class="flex items-center gap-2 text-sm" style="color: #94a3b8">
              <span style="color: var(--color-primary-500)">📞</span> 1900-xxxx
            </li>
            <li class="flex items-center gap-2 text-sm" style="color: #94a3b8">
              <span style="color: var(--color-primary-500)">✉️</span> hello@englishstudy.vn
            </li>
            <li class="flex items-center gap-2 text-sm" style="color: #94a3b8">
              <span style="color: var(--color-primary-500)">📍</span> Hà Nội, Việt Nam
            </li>
            <li class="pt-1">
              <RouterLink
                to="/help/support-request"
                class="text-sm transition hover:text-white"
                style="color: #94a3b8"
              >Gửi yêu cầu hỗ trợ →</RouterLink>
            </li>
          </ul>
        </div>
      </div>

      <!-- Bottom bar -->
      <div class="mt-10 pt-6 flex flex-col sm:flex-row items-center justify-between gap-3"
           style="border-top: 1px solid rgba(255,255,255,0.1)">
        <p class="text-xs" style="color: #64748b">
          © 2026 EnglishStudy. All rights reserved. Made with
          <span style="color: var(--color-primary-500)">♥</span> in Vietnam
        </p>
        <div class="flex gap-4">
          <a href="#" class="text-xs transition hover:text-white" style="color: #64748b">Điều khoản</a>
          <a href="#" class="text-xs transition hover:text-white" style="color: #64748b">Bảo mật</a>
          <a href="#" class="text-xs transition hover:text-white" style="color: #64748b">Cookie</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { RouterLink } from 'vue-router'

const socials = [
  { label: 'Facebook',  href: '#', icon: 'f' },
  { label: 'YouTube',   href: '#', icon: '▶' },
  { label: 'Instagram', href: '#', icon: '◎' },
]

const footerLinks = {
  courses: [
    { label: 'Giao tiếp cơ bản (A1–A2)', to: '/courses' },
    { label: 'Tiếng Anh trung cấp (B1–B2)', to: '/courses' },
    { label: 'Nâng cao (C1–C2)', to: '/courses' },
    { label: 'Phát âm chuẩn', to: '/pronunciation' },
    { label: 'Flashcard từ vựng', to: '/flashcards' },
  ],
  company: [
    { label: 'Giới thiệu', to: '/about' },
    { label: 'Blog', to: '/blog' },
    { label: 'Bảng giá', to: '/pricing' },
    { label: 'Bảng xếp hạng', to: '/leaderboard' },
  ],
}
</script>
