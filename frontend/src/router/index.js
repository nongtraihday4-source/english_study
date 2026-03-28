import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ── Public routes ────────────────────────────────────────────────────────
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { public: true, guestOnly: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { public: true, guestOnly: true },
    },
    {
      path: '/pricing',
      name: 'pricing',
      component: () => import('@/views/PricingView.vue'),
      meta: { public: true, title: 'Bảng giá' },
    },
    {
      path: '/checkout/:planId',
      name: 'checkout',
      component: () => import('@/views/CheckoutView.vue'),
      meta: { public: true, title: 'Thanh toán' },
    },
    {
      path: '/payment/success',
      name: 'payment-success',
      component: () => import('@/views/PaymentSuccessView.vue'),
      meta: { public: true, title: 'Thanh toán thành công' },
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: () => import('@/views/ResetPasswordView.vue'),
      meta: { public: true, title: 'Đặt lại mật khẩu' },
    },
    {
      path: '/help/support-request',
      name: 'public-support-request',
      component: () => import('@/views/PublicSupportRequestView.vue'),
      meta: { public: true, title: 'Gửi yêu cầu hỗ trợ' },
    },

    // ── Authenticated routes (inside AppLayout) ────────────────────────────
    {
      path: '/',
      component: () => import('@/components/layout/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          redirect: '/dashboard',
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue'),
          meta: { title: 'Dashboard' },
        },
        {
          path: 'courses',
          name: 'courses',
          component: () => import('@/views/CoursesView.vue'),
          meta: { title: 'Khoá học' },
        },
        {
          path: 'courses/:id',
          name: 'course-detail',
          component: () => import('@/views/CourseDetailView.vue'),
          meta: { title: 'Chi tiết khoá học' },
        },
        {
          path: 'learn/listening/:id',
          name: 'learn-listening',
          component: () => import('@/views/exercise/ListeningView.vue'),
          meta: { title: 'Luyện Nghe' },
        },
        {
          path: 'learn/speaking/:id',
          name: 'learn-speaking',
          component: () => import('@/views/exercise/SpeakingView.vue'),
          meta: { title: 'Luyện Nói' },
        },
        {
          path: 'learn/reading/:id',
          name: 'learn-reading',
          component: () => import('@/views/exercise/ReadingView.vue'),
          meta: { title: 'Luyện Đọc' },
        },
        {
          path: 'learn/writing/:id',
          name: 'learn-writing',
          component: () => import('@/views/exercise/WritingView.vue'),
          meta: { title: 'Luyện Viết' },
        },
        {
          path: 'learn/result/:submissionId',
          name: 'learn-result',
          component: () => import('@/views/exercise/ExerciseResultView.vue'),
          meta: { title: 'Kết quả bài tập' },
        },
        {
          path: 'grammar',
          name: 'grammar',
          component: () => import('@/views/GrammarView.vue'),
          meta: { title: 'Ngữ pháp' },
        },
        {
          path: 'grammar/:slug',
          name: 'grammar-detail',
          component: () => import('@/views/GrammarDetailView.vue'),
          meta: { title: 'Chi tiết ngữ pháp' },
        },
        {
          path: 'vocabulary',
          name: 'vocabulary',
          component: () => import('@/views/VocabularyView.vue'),
          meta: { title: 'Từ vựng' },
        },
        {
          path: 'flashcards',
          name: 'flashcard-decks',
          component: () => import('@/views/FlashcardDecksView.vue'),
          meta: { title: 'Flashcards' },
        },
        {
          path: 'flashcards/quiz',
          name: 'flashcard-quiz-multi',
          component: () => import('@/views/FlashcardQuizView.vue'),
          meta: { title: 'Kiểm tra tổng hợp' },
        },
        {
          path: 'flashcards/:deckId/words',
          name: 'deck-words',
          component: () => import('@/views/DeckWordsView.vue'),
          meta: { title: 'Tất cả từ trong deck' },
        },
        {
          path: 'flashcards/:deckId/study',
          name: 'flashcard-study',
          component: () => import('@/views/FlashcardStudyView.vue'),
          meta: { title: 'Phiên học Flashcard' },
        },
        {
          path: 'flashcards/:deckId/quiz',
          name: 'flashcard-quiz',
          component: () => import('@/views/FlashcardQuizView.vue'),
          meta: { title: 'Kiểm tra Flashcard' },
        },
        {
          path: 'assessments',
          name: 'assessment-list',
          component: () => import('@/views/assessment/ExamListView.vue'),
          meta: { title: 'Bài thi đánh giá' },
        },
        {
          path: 'assessments/:id',
          name: 'assessment-detail',
          component: () => import('@/views/assessment/ExamView.vue'),
          meta: { title: 'Làm bài thi' },
        },
        {
          path: 'pronunciation',
          name: 'pronunciation',
          component: () => import('@/views/PronunciationView.vue'),
          meta: { title: 'Phát âm' },
        },
        {
          path: 'pronunciation/lessons/:slug',
          name: 'pronunciation-lesson',
          component: () => import('@/views/PronunciationLessonView.vue'),
          meta: { title: 'Bài học phát âm' },
        },
        {
          path: 'leaderboard',
          name: 'leaderboard',
          component: () => import('@/views/LeaderboardView.vue'),
          meta: { title: 'Bảng xếp hạng' },
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/ProfileView.vue'),
          meta: { title: 'Hồ sơ' },
        },
        {
          path: 'achievements',
          name: 'achievements',
          component: () => import('@/views/AchievementsView.vue'),
          meta: { title: 'Thành tựu' },
        },
        {
          path: 'certificates',
          name: 'certificates',
          component: () => import('@/views/CertificatesView.vue'),
          meta: { title: 'Chứng chỉ' },
        },
      ],
    },

    // ── Admin Portal ────────────────────────────────────────────────────────────
    {
      path: '/admin',
      component: () => import('@/views/admin/AdminLayout.vue'),
      meta: { requiresAuth: true, roles: ['admin'] },
      children: [
        {
          path: '',
          name: 'admin-dashboard',
          component: () => import('@/views/admin/AdminDashboardView.vue'),
          meta: { title: 'Admin — Tổng quan' },
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('@/views/admin/AdminUsersView.vue'),
          meta: { title: 'Admin — Người dùng' },
        },
        {
          path: 'content',
          name: 'admin-content',
          component: () => import('@/views/admin/AdminContentView.vue'),
          meta: { title: 'Admin — Nội dung' },
        },
        {
          path: 'payments',
          name: 'admin-payments',
          component: () => import('@/views/admin/AdminPaymentsView.vue'),
          meta: { title: 'Admin — Thanh toán' },
        },
        {
          path: 'assessments',
          name: 'admin-assessments',
          component: () => import('@/views/admin/AdminAssessmentsView.vue'),
          meta: { title: 'Admin — Bài thi' },
        },
        {
          path: 'grading',
          name: 'admin-grading',
          component: () => import('@/views/admin/AdminGradingView.vue'),
          meta: { title: 'Admin — AI Grading' },
        },
        {
          path: 'gamification',
          name: 'admin-gamification',
          component: () => import('@/views/admin/AdminGamificationView.vue'),
          meta: { title: 'Admin — Gamification' },
        },
        {
          path: 'notifications',
          name: 'admin-notifications',
          component: () => import('@/views/admin/AdminNotificationsView.vue'),
          meta: { title: 'Admin — Thông báo' },
        },
        {
          path: 'audit-log',
          name: 'admin-audit-log',
          component: () => import('@/views/admin/AdminAuditLogView.vue'),
          meta: { title: 'Admin — Nhật ký' },
        },
        {
          path: 'settings',
          name: 'admin-settings',
          component: () => import('@/views/admin/AdminSettingsView.vue'),
          meta: { title: 'Admin — Cài đặt' },
        },
      ],
    },

    // ── Teacher Portal ─────────────────────────────────────────────────────────
    {
      path: '/teacher',
      component: () => import('@/views/teacher/TeacherLayout.vue'),
      meta: { requiresAuth: true, roles: ['teacher', 'admin'] },
      children: [
        {
          path: '',
          name: 'teacher-dashboard',
          component: () => import('@/views/teacher/TeacherDashboardView.vue'),
          meta: { title: 'Tổng quan giáo viên' },
        },
        {
          path: 'grading',
          name: 'teacher-grading',
          component: () => import('@/views/teacher/TeacherGradingView.vue'),
          meta: { title: 'Chấm bài' },
        },
        {
          path: 'classes',
          name: 'teacher-classes',
          component: () => import('@/views/teacher/TeacherClassView.vue'),
          meta: { title: 'Lớp học' },
        },
      ],
    },

    // ── Support Portal ─────────────────────────────────────────────────────────
    {
      path: '/support',
      component: () => import('@/views/support/SupportLayout.vue'),
      meta: { requiresAuth: true, roles: ['support', 'admin'] },
      children: [
        {
          path: '',
          name: 'support-dashboard',
          component: () => import('@/views/support/SupportDashboardView.vue'),
          meta: { title: 'Hỗ trợ — Tổng quan' },
        },
        {
          path: 'users',
          name: 'support-users',
          component: () => import('@/views/support/SupportUserLookupView.vue'),
          meta: { title: 'Hỗ trợ — Tra cứu người dùng' },
        },
        {
          path: 'users/:id',
          name: 'support-user-detail',
          component: () => import('@/views/support/SupportUserDetailView.vue'),
          meta: { title: 'Hỗ trợ — Chi tiết người dùng' },
        },
        {
          path: 'tickets',
          name: 'support-tickets',
          component: () => import('@/views/support/SupportTicketListView.vue'),
          meta: { title: 'Hỗ trợ — Tickets' },
        },
        {
          path: 'public-requests',
          name: 'support-public-requests',
          component: () => import('@/views/support/SupportPublicRequestsView.vue'),
          meta: { title: 'Hỗ trợ — Yêu cầu công khai' },
        },
        {
          path: 'tickets/:id',
          name: 'support-ticket-detail',
          component: () => import('@/views/support/SupportTicketDetailView.vue'),
          meta: { title: 'Hỗ trợ — Chi tiết ticket' },
        },
        {
          path: 'payments',
          name: 'support-payments',
          component: () => import('@/views/support/SupportPaymentsView.vue'),
          meta: { title: 'Hỗ trợ — Thanh toán' },
        },
        {
          path: 'coupons',
          name: 'support-coupons',
          component: () => import('@/views/support/SupportCouponsView.vue'),
          meta: { title: 'Hỗ trợ — Ưu đãi' },
        },
        {
          path: 'refunds',
          name: 'support-refunds',
          component: () => import('@/views/support/SupportRefundsView.vue'),
          meta: { title: 'Hỗ trợ — Hoàn tiền' },
        },
      ],
    },

    // ── Catch-all ────────────────────────────────────────────────────────────
    {
      path: '/:pathMatch(.*)*',
      redirect: '/dashboard',
    },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

// ── Auth Guard ────────────────────────────────────────────────────────────────
router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  // Init auth state once (re-hydrate from server cookie)
  if (!auth.initialized) {
    await auth.init()
  }

  // Route requires login — redirect to /login if not authenticated
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  // Role-restricted routes
  if (to.meta.roles && auth.isLoggedIn) {
    const userRole = auth.user?.role
    if (!to.meta.roles.includes(userRole)) {
      return next({ name: 'dashboard' })
    }
  }

  // Guest-only routes (login, register) — redirect logged-in users to their portal
  if (to.meta.guestOnly && auth.isLoggedIn) {
    const role = auth.user?.role
    if (role === 'support') return next({ path: '/support' })
    return next({ name: 'dashboard' })
  }

  // Update page title
  if (to.meta.title) {
    document.title = `${to.meta.title} — English Study`
  }

  next()
})

export default router
