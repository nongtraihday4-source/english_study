<template>
  <!-- ══════════════════════════════════════════════════
       HERO SECTION
  ══════════════════════════════════════════════════ -->
  <section class="relative overflow-hidden" style="background-color: var(--color-surface)">
    <!-- Decorative blobs -->
    <div class="blob blob-1 pointer-events-none" aria-hidden="true"></div>
    <div class="blob blob-2 pointer-events-none" aria-hidden="true"></div>

    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-28">
      <div class="grid lg:grid-cols-2 gap-12 items-center">
        <!-- Left: Copy -->
        <div>
          <!-- Badge -->
          <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold mb-6"
               style="background-color: var(--color-primary-50); color: var(--color-primary-600); border: 1px solid var(--color-primary-200)">
            🚀 Nền tảng học tiếng Anh AI số 1 Việt Nam
          </div>

          <h1 class="text-4xl md:text-5xl xl:text-6xl font-black leading-tight mb-6"
              style="font-family: var(--font-heading); color: var(--color-secondary); letter-spacing: -0.02em">
            Từ <span class="highlight">"Ấp Úng"</span><br>
            Đến <span class="highlight">"Bắn"</span><br>
            Tiếng Anh Như Gió.
          </h1>

          <p class="text-base md:text-lg leading-relaxed mb-8 max-w-lg"
             style="color: var(--color-text-muted)">
            Bạn giỏi ngữ pháp nhưng sợ giao tiếp? Phương pháp AI độc quyền của chúng tôi giúp bạn luyện 4 kỹ năng — <strong style="color: var(--color-text-base)">phản xạ tức thì, phát âm chuẩn, từ vựng thực chiến</strong> — ngay từ bài học đầu tiên.
          </p>

          <div class="flex flex-col sm:flex-row gap-3 mb-8">
            <RouterLink
              to="/register"
              class="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-bold text-white text-sm transition hover:opacity-90 shadow-lg"
              style="background-color: var(--color-primary-500); box-shadow: 0 8px 24px rgba(244,124,38,0.35); font-family: var(--font-heading)"
            >🚀 HỌC THỬ MIỄN PHÍ NGAY</RouterLink>
            <RouterLink
              to="/register"
              class="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-semibold text-sm transition hover:opacity-80"
              style="color: var(--color-secondary); border: 2px solid var(--color-surface-04); background-color: var(--color-surface-02)"
            >📋 Kiểm tra trình độ</RouterLink>
          </div>

          <!-- Trust badges -->
          <div class="flex flex-wrap items-center gap-4">
            <div class="flex items-center gap-1.5">
              <span class="flex">⭐⭐⭐⭐⭐</span>
              <span class="text-xs font-medium" style="color: var(--color-text-muted)">
                <strong style="color: var(--color-text-base)">10,000+</strong> học viên
              </span>
            </div>
            <div class="w-px h-4" style="background-color: var(--color-surface-04)"></div>
            <div class="flex items-center gap-1.5 text-xs" style="color: var(--color-text-muted)">
              ✅ Không cần thẻ tín dụng
            </div>
            <div class="w-px h-4" style="background-color: var(--color-surface-04)"></div>
            <div class="flex items-center gap-1.5 text-xs" style="color: var(--color-text-muted)">
              🔒 Hủy bất cứ lúc nào
            </div>
          </div>
        </div>

        <!-- Right: Illustration -->
        <div class="relative flex items-center justify-center">
          <div class="hero-card w-full max-w-sm mx-auto">
            <!-- Mock app UI card -->
            <div class="rounded-2xl p-6 shadow-2xl"
                 style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)">
              <!-- Header bar -->
              <div class="flex items-center justify-between mb-5">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-black"
                       style="background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-600))">ES</div>
                  <div>
                    <p class="text-xs font-semibold" style="color: var(--color-text-base)">Bài học hôm nay</p>
                    <p class="text-xs" style="color: var(--color-text-muted)">Unit 3 · Giao tiếp công sở</p>
                  </div>
                </div>
                <span class="text-xs px-2 py-0.5 rounded-full font-bold" style="background-color: var(--color-primary-50); color: var(--color-primary-600)">B1</span>
              </div>

              <!-- Progress bar -->
              <div class="mb-5">
                <div class="flex justify-between text-xs mb-1.5" style="color: var(--color-text-muted)">
                  <span>Tiến độ khoá học</span>
                  <span style="color: var(--color-primary-500)">68%</span>
                </div>
                <div class="h-2 rounded-full overflow-hidden" style="background-color: var(--color-surface-03)">
                  <div class="h-full rounded-full transition-all"
                       style="width: 68%; background: linear-gradient(90deg, var(--color-primary-500), var(--color-primary-400))"></div>
                </div>
              </div>

              <!-- Skill chips -->
              <div class="grid grid-cols-2 gap-2 mb-5">
                <div v-for="skill in mockSkills" :key="skill.name"
                     class="flex items-center gap-2 p-2.5 rounded-xl"
                     style="background-color: var(--color-surface-03)">
                  <span class="text-base">{{ skill.icon }}</span>
                  <div>
                    <p class="text-xs font-semibold" style="color: var(--color-text-base)">{{ skill.name }}</p>
                    <div class="h-1 rounded-full mt-0.5" style="width: 40px; background-color: var(--color-surface-04)">
                      <div class="h-full rounded-full" :style="`width: ${skill.pct}%; background-color: var(--color-primary-500)`"></div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- XP toast -->
              <div class="flex items-center gap-3 p-3 rounded-xl"
                   style="background: linear-gradient(135deg, rgba(244,124,38,0.12), rgba(244,124,38,0.06)); border: 1px solid rgba(244,124,38,0.25)">
                <span class="text-xl">🔥</span>
                <div>
                  <p class="text-xs font-bold" style="color: var(--color-primary-500)">Chuỗi 7 ngày liên tiếp!</p>
                  <p class="text-xs" style="color: var(--color-text-muted)">+50 XP • Còn 3 bài để lên B2</p>
                </div>
              </div>
            </div>

            <!-- Floating badges -->
            <div class="absolute -top-4 -right-4 px-3 py-2 rounded-2xl shadow-lg text-xs font-bold animate-float"
                 style="background-color: var(--color-success); color: #fff">
              ✓ Phát âm đúng 95%
            </div>
            <div class="absolute -bottom-4 -left-4 px-3 py-2 rounded-2xl shadow-lg text-xs font-bold animate-float-delay"
                 style="background-color: var(--color-surface-02); color: var(--color-primary-500); border: 2px solid var(--color-primary-200)">
              🏆 Top 12 tuần này
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ══════════════════════════════════════════════════
       STATS BAR
  ══════════════════════════════════════════════════ -->
  <section style="background-color: var(--color-secondary)">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
        <div v-for="stat in stats" :key="stat.label" class="group">
          <p class="text-3xl md:text-4xl font-black text-white mb-1"
             style="font-family: var(--font-heading)">{{ stat.value }}</p>
          <p class="text-xs font-medium uppercase tracking-wider" style="color: rgba(255,255,255,0.6)">{{ stat.label }}</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ══════════════════════════════════════════════════
       FEATURES SECTION
  ══════════════════════════════════════════════════ -->
  <section class="py-20 lg:py-24" style="background-color: var(--color-surface)">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-14">
        <p class="text-xs font-bold uppercase tracking-widest mb-3" style="color: var(--color-primary-500)">Tại sao chọn chúng tôi?</p>
        <h2 class="text-3xl md:text-4xl font-black mb-4"
            style="font-family: var(--font-heading); color: var(--color-secondary); letter-spacing: -0.02em">
          Học theo phương pháp<br><span style="color: var(--color-primary-500)">AI thực chiến</span>
        </h2>
        <p class="text-base max-w-2xl mx-auto" style="color: var(--color-text-muted)">
          Không chỉ học ngữ pháp. Chúng tôi xây dựng phản xạ ngôn ngữ thực sự thông qua AI chấm bài, phoneme tương tác và gamification kéo dài thói quen học tập.
        </p>
      </div>

      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="feature in features"
          :key="feature.title"
          class="feature-card group rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1"
          style="background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)"
        >
          <div class="w-12 h-12 rounded-2xl flex items-center justify-center text-2xl mb-4 transition"
               style="background-color: var(--color-primary-50)">
            {{ feature.icon }}
          </div>
          <h3 class="font-bold mb-2" style="font-family: var(--font-heading); color: var(--color-secondary)">{{ feature.title }}</h3>
          <p class="text-sm leading-relaxed" style="color: var(--color-text-muted)">{{ feature.desc }}</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ══════════════════════════════════════════════════
       HOW IT WORKS
  ══════════════════════════════════════════════════ -->
  <section class="py-20 lg:py-24" style="background-color: var(--color-surface-02)">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-14">
        <p class="text-xs font-bold uppercase tracking-widest mb-3" style="color: var(--color-primary-500)">Phương pháp học tập</p>
        <h2 class="text-3xl md:text-4xl font-black"
            style="font-family: var(--font-heading); color: var(--color-secondary); letter-spacing: -0.02em">
          3 bước đơn giản để bắt đầu
        </h2>
      </div>

      <div class="space-y-16">
        <div
          v-for="(step, idx) in steps"
          :key="step.title"
          class="grid lg:grid-cols-2 gap-10 items-center"
          :class="idx % 2 === 1 ? 'lg:[direction:rtl]' : ''"
        >
          <!-- Text -->
          <div :class="idx % 2 === 1 ? 'lg:[direction:ltr]' : ''">
            <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold mb-4"
                 style="background-color: var(--color-primary-500); color: #fff">
              Bước {{ idx + 1 }}
            </div>
            <h3 class="text-2xl font-black mb-4"
                style="font-family: var(--font-heading); color: var(--color-secondary)">{{ step.title }}</h3>
            <p class="text-base leading-relaxed mb-5" style="color: var(--color-text-muted)">{{ step.desc }}</p>
            <ul class="space-y-2">
              <li v-for="pt in step.points" :key="pt" class="flex items-start gap-2 text-sm" style="color: var(--color-text-muted)">
                <span style="color: var(--color-primary-500); margin-top: 2px">✓</span> {{ pt }}
              </li>
            </ul>
          </div>

          <!-- Visual card -->
          <div :class="idx % 2 === 1 ? 'lg:[direction:ltr]' : ''">
            <div class="rounded-2xl p-8 flex flex-col items-center justify-center min-h-48 text-center shadow-sm"
                 style="background: linear-gradient(135deg, var(--color-primary-50), var(--color-surface-03)); border: 1px solid var(--color-surface-04)">
              <span class="text-6xl mb-4">{{ step.emoji }}</span>
              <p class="font-bold text-sm" style="color: var(--color-secondary)">{{ step.visual }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ══════════════════════════════════════════════════
       PRICING PREVIEW
  ══════════════════════════════════════════════════ -->
  <section class="py-20 lg:py-24" style="background-color: var(--color-surface)">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-14">
        <p class="text-xs font-bold uppercase tracking-widest mb-3" style="color: var(--color-primary-500)">Bảng giá minh bạch</p>
        <h2 class="text-3xl md:text-4xl font-black mb-4"
            style="font-family: var(--font-heading); color: var(--color-secondary); letter-spacing: -0.02em">
          Bắt đầu miễn phí, nâng cấp khi sẵn sàng
        </h2>
        <p class="text-base" style="color: var(--color-text-muted)">Không ẩn phí. Không bị ép buộc.</p>
      </div>

      <div class="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
        <div
          v-for="plan in plans"
          :key="plan.name"
          class="rounded-2xl p-6 flex flex-col transition-all duration-300 hover:-translate-y-1"
          :style="plan.highlight
            ? 'background-color: var(--color-primary-500); color: #fff; box-shadow: 0 16px 40px rgba(244,124,38,0.3)'
            : 'background-color: var(--color-surface-02); border: 1px solid var(--color-surface-04)'"
        >
          <div v-if="plan.badge" class="text-xs font-bold px-2 py-0.5 rounded-full self-start mb-3"
               style="background-color: rgba(255,255,255,0.25); color: #fff">
            {{ plan.badge }}
          </div>
          <h3 class="font-black text-lg mb-1"
              :style="plan.highlight ? 'color: #fff; font-family: var(--font-heading)' : 'color: var(--color-secondary); font-family: var(--font-heading)'">
            {{ plan.name }}
          </h3>
          <p class="text-3xl font-black mb-1"
             :style="plan.highlight ? 'color: #fff' : 'color: var(--color-secondary)'">
            {{ plan.price }}
            <span class="text-sm font-normal" :style="plan.highlight ? 'color: rgba(255,255,255,0.8)' : 'color: var(--color-text-muted)'">{{ plan.period }}</span>
          </p>
          <p class="text-sm mb-5 flex-1" :style="plan.highlight ? 'color: rgba(255,255,255,0.85)' : 'color: var(--color-text-muted)'">{{ plan.desc }}</p>
          <ul class="space-y-2 mb-6">
            <li v-for="f in plan.features" :key="f"
                class="flex items-start gap-2 text-xs"
                :style="plan.highlight ? 'color: rgba(255,255,255,0.9)' : 'color: var(--color-text-muted)'">
              <span :style="plan.highlight ? 'color: rgba(255,255,255,0.9)' : 'color: var(--color-primary-500)'">✓</span> {{ f }}
            </li>
          </ul>
          <RouterLink
            to="/register"
            class="text-center py-2.5 rounded-xl font-bold text-sm transition"
            :style="plan.highlight
              ? 'background-color: rgba(255,255,255,0.2); color: #fff; border: 2px solid rgba(255,255,255,0.4)'
              : 'background-color: var(--color-primary-500); color: #fff'"
          >{{ plan.cta }}</RouterLink>
        </div>
      </div>

      <div class="text-center mt-6">
        <RouterLink to="/pricing" class="text-sm font-semibold transition hover:opacity-80"
                    style="color: var(--color-primary-500)">Xem chi tiết bảng giá →</RouterLink>
      </div>
    </div>
  </section>

  <!-- ══════════════════════════════════════════════════
       TESTIMONIALS
  ══════════════════════════════════════════════════ -->
  <section class="py-20 lg:py-24" style="background-color: var(--color-surface-02)">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-14">
        <p class="text-xs font-bold uppercase tracking-widest mb-3" style="color: var(--color-primary-500)">Học viên nói gì?</p>
        <h2 class="text-3xl md:text-4xl font-black"
            style="font-family: var(--font-heading); color: var(--color-secondary); letter-spacing: -0.02em">
          Hơn 10,000 học viên<br>đã thay đổi cuộc sống
        </h2>
      </div>

      <div class="grid md:grid-cols-3 gap-6">
        <div
          v-for="t in testimonials"
          :key="t.name"
          class="rounded-2xl p-6 flex flex-col"
          style="background-color: var(--color-surface); border: 1px solid var(--color-surface-04)"
        >
          <div class="flex mb-3">
            <span v-for="i in 5" :key="i" style="color: #f59e0b" class="text-sm">⭐</span>
          </div>
          <p class="text-sm leading-relaxed flex-1 mb-5 italic" style="color: var(--color-text-muted)">"{{ t.quote }}"</p>
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0"
                 :style="`background: ${t.color}`">{{ t.initial }}</div>
            <div>
              <p class="text-sm font-bold" style="color: var(--color-secondary)">{{ t.name }}</p>
              <p class="text-xs" style="color: var(--color-text-muted)">{{ t.role }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ══════════════════════════════════════════════════
       FINAL CTA
  ══════════════════════════════════════════════════ -->
  <section class="py-20 lg:py-28 relative overflow-hidden"
           style="background: linear-gradient(135deg, var(--color-primary-500) 0%, #E8670F 100%)">
    <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
      <div class="absolute top-0 right-0 w-96 h-96 rounded-full opacity-20"
           style="background: radial-gradient(circle, rgba(255,255,255,0.4) 0%, transparent 70%); transform: translate(30%, -30%)"></div>
      <div class="absolute bottom-0 left-0 w-64 h-64 rounded-full opacity-15"
           style="background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%); transform: translate(-30%, 30%)"></div>
    </div>
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative">
      <p class="text-sm font-bold uppercase tracking-widest mb-4" style="color: rgba(255,255,255,0.8)">Sẵn sàng thay đổi chưa?</p>
      <h2 class="text-3xl md:text-5xl font-black text-white mb-6 leading-tight"
          style="font-family: var(--font-heading); letter-spacing: -0.02em">
        Bắt đầu hành trình<br>chinh phục tiếng Anh ngay!
      </h2>
      <p class="text-base mb-10 max-w-xl mx-auto" style="color: rgba(255,255,255,0.88)">
        Tham gia cùng 10,000+ học viên đang học hiệu quả mỗi ngày. Miễn phí để bắt đầu — không cần thẻ tín dụng.
      </p>
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <RouterLink
          to="/register"
          class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl font-bold text-base transition hover:opacity-90 shadow-xl"
          style="background-color: #fff; color: var(--color-primary-500); font-family: var(--font-heading)"
        >🚀 ĐĂNG KÝ MIỄN PHÍ</RouterLink>
        <RouterLink
          to="/register"
          class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl font-semibold text-base transition hover:bg-white hover:text-orange-500"
          style="color: #fff; border: 2px solid rgba(255,255,255,0.5)"
        >📋 Kiểm tra trình độ</RouterLink>
      </div>
      <p class="mt-6 text-xs" style="color: rgba(255,255,255,0.65)">
        🔒 Không cần thẻ tín dụng &nbsp;•&nbsp; Hủy bất cứ lúc nào &nbsp;•&nbsp; Hỗ trợ 24/7
      </p>
    </div>
  </section>
</template>

<script setup>
import { RouterLink } from 'vue-router'

const mockSkills = [
  { name: 'Nghe',  icon: '🎧', pct: 82 },
  { name: 'Nói',   icon: '🎙️', pct: 65 },
  { name: 'Đọc',   icon: '📖', pct: 90 },
  { name: 'Viết',  icon: '✍️', pct: 71 },
]

const stats = [
  { value: '10K+',  label: 'Học viên' },
  { value: '120+',  label: 'Khoá học' },
  { value: '2,400+',label: 'Bài học' },
  { value: '4.9 ★', label: 'Đánh giá' },
]

const features = [
  {
    icon: '🤖',
    title: 'AI Chấm Bài Tự Động',
    desc: 'GPT-4o + Whisper đánh giá phát âm, ngữ pháp, từ vựng và độ mạch lạc theo thời gian thực. Không phải chờ giáo viên.',
  },
  {
    icon: '🎯',
    title: '4 Kỹ Năng Toàn Diện',
    desc: 'Nghe – Nói – Đọc – Viết trong ngữ cảnh thực tế. Bài học kết cấu split-pane, không mỏi mắt khi học lâu.',
  },
  {
    icon: '🗣️',
    title: 'Phát Âm Chuẩn IPA',
    desc: 'Biểu đồ phoneme tương tác với 44 âm tiếng Anh, minimal pairs, shadowing karaoke với waveform thực.',
  },
  {
    icon: '🏆',
    title: 'Gamification Thực Sự',
    desc: 'XP, streak days, leaderboard, achievements, daily challenges — hệ thống kéo dài thói quen học tập hàng ngày.',
  },
  {
    icon: '🃏',
    title: 'Flashcard Thông Minh',
    desc: 'Thuật toán SM-2 spaced repetition với từ vựng Oxford 3000/5000. Từ có IPA, âm thanh UK/US, ví dụ ngữ cảnh.',
  },
  {
    icon: '🌳',
    title: 'Lộ Trình Skill Tree',
    desc: 'Hệ thống khoá bài theo điểm tối thiểu. Không thể bỏ qua nền tảng — tiến độ minh bạch từng cấp độ A1→C1.',
  },
]

const steps = [
  {
    title: 'Làm bài test đầu vào',
    desc: 'Đánh giá chính xác trình độ hiện tại qua bài test thông minh 4 kỹ năng. Chỉ 15 phút để biết bạn ở đâu và cần học gì.',
    emoji: '📊',
    visual: 'Kết quả chi tiết ngay lập tức',
    points: ['Test toàn diện 4 kỹ năng Nghe/Nói/Đọc/Viết', 'Xếp loại chuẩn CEFR (A1 → C1)', 'Hoàn toàn miễn phí, không cần đăng ký'],
  },
  {
    title: 'Nhận lộ trình cá nhân hoá',
    desc: 'AI phân tích điểm mạnh/yếu và xây dựng skill tree riêng cho bạn. Mỗi bài học được sắp xếp để tối ưu việc tiếp thu.',
    emoji: '🗺️',
    visual: 'AI thiết kế lộ trình riêng cho bạn',
    points: ['Lộ trình phù hợp mục tiêu cụ thể', 'Điều chỉnh linh hoạt theo tiến độ thực tế', 'Unlock bài tiếp theo khi đạt điểm chuẩn'],
  },
  {
    title: 'Luyện tập và nhận chứng chỉ',
    desc: 'Học tập đều đặn với bài tập gamified, nhận phản hồi tức thì từ AI và chứng chỉ hoàn thành khoá học.',
    emoji: '🎓',
    visual: 'Chứng chỉ được công nhận',
    points: ['Bài tập tương tác & gamification hấp dẫn', 'Phản hồi chi tiết từ AI sau mỗi bài nộp', 'Chứng chỉ CEFR khi hoàn thành khoá học'],
  },
]

const plans = [
  {
    name: 'Miễn phí',
    price: '0đ',
    period: '/tháng',
    desc: 'Khám phá nền tảng, làm quen với 3 bài học mỗi cấp.',
    highlight: false,
    features: ['3 bài học/cấp độ (demo)', 'Flashcard cơ bản', 'Biểu đồ phoneme', 'Leaderboard công khai'],
    cta: 'Bắt đầu miễn phí',
  },
  {
    name: 'Premium',
    price: '199K',
    period: '/tháng',
    desc: 'Truy cập toàn bộ nội dung, AI grading không giới hạn.',
    highlight: true,
    badge: '⭐ Phổ biến nhất',
    features: ['Toàn bộ khoá học A1→C1', 'AI chấm bài không giới hạn', 'Phát âm shadowing + waveform', 'Flashcard SM-2 đầy đủ', 'Chứng chỉ hoàn thành'],
    cta: 'Dùng thử 7 ngày',
  },
  {
    name: 'Premium Năm',
    price: '1.49M',
    period: '/năm',
    desc: 'Tiết kiệm 37% so với tháng. Cam kết học dài hạn.',
    highlight: false,
    features: ['Tất cả tính năng Premium', 'Tiết kiệm 37% (≈124K/tháng)', 'Ưu tiên hỗ trợ 24/7', 'Chứng chỉ đặc biệt yearly'],
    cta: 'Chọn gói năm',
  },
]

const testimonials = [
  {
    quote: 'Sau 3 tháng dùng EnglishStudy, tôi đã có thể họp với đối tác nước ngoài tự tin hơn hẳn. Phần phát âm IPA giúp tôi sửa được lỗi cơ bản từ lâu không biết.',
    name: 'Nguyễn Minh Tú',
    role: 'Product Manager tại Start-up',
    initial: 'T',
    color: 'linear-gradient(135deg, #F47C26, #E8670F)',
  },
  {
    quote: 'Streak 45 ngày liên tiếp — tôi chưa bao giờ duy trì được lâu như vậy với bất kỳ app nào. Gamification thực sự hiệu quả không chỉ là hình thức.',
    name: 'Trần Phương Linh',
    role: 'Sinh viên năm 3 ĐHKT',
    initial: 'L',
    color: 'linear-gradient(135deg, #183B56, #2a5880)',
  },
  {
    quote: 'AI feedback chi tiết đến mức tôi biết chính xác từ nào mình đang phát âm sai và tại sao. Không app nào làm được điều này rõ ràng như vậy.',
    name: 'Lê Hoàng Nam',
    role: 'Kỹ sư phần mềm, TP.HCM',
    initial: 'N',
    color: 'linear-gradient(135deg, #2ECC71, #27ae60)',
  },
]
</script>

<style scoped>
/* Decorative blobs for hero */
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.35;
  pointer-events: none;
}
.blob-1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, var(--color-primary-200), transparent);
  top: -200px; right: -100px;
}
.blob-2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, #b3cfec, transparent);
  bottom: -100px; left: -150px;
}

/* Orange text highlight */
.highlight {
  color: var(--color-primary-500);
  position: relative;
}

/* Hero card */
.hero-card { position: relative; }

/* Floating animation */
@keyframes float {
  0%,100% { transform: translateY(0); }
  50%      { transform: translateY(-8px); }
}
@keyframes floatDelay {
  0%,100% { transform: translateY(0); }
  50%      { transform: translateY(-6px); }
}
.animate-float       { animation: float 3.2s ease-in-out infinite; }
.animate-float-delay { animation: floatDelay 3.8s ease-in-out 1s infinite; }

/* Feature card hover shadow */
.feature-card:hover {
  box-shadow: 0 12px 32px rgba(244, 124, 38, 0.12);
  border-color: var(--color-primary-200) !important;
}
</style>
