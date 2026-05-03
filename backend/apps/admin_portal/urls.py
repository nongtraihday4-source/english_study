"""
apps/admin_portal/urls.py
"""
from django.urls import path

from .views import (
    AdminCEFRLevelListView,
    AdminChapterListView,
    AdminChapterDetailView,
    AdminCourseDetailView,
    AdminCourseListView,
    AdminDashboardView,
    AdminLessonListView,
    AdminLessonDetailView,
    AdminLessonExerciseListView,
    AdminLessonExerciseDetailView,
    AdminExerciseTypeListView,
    AdminExerciseTypeDetailView,
    AdminGrammarChapterListView,
    AdminGrammarChapterDetailView,
    AdminGrammarTopicListView,
    AdminGrammarTopicDetailView,
    AdminGrammarRuleListView,
    AdminGrammarRuleDetailView,
    AdminGrammarExampleListView,
    AdminGrammarExampleDetailView,
    AdminUserBanView,
    # Payments
    AdminPlanListView,
    AdminPlanDetailView,
    AdminCouponListView,
    AdminCouponDetailView,
    AdminTransactionListView,
    AdminSubscriptionListView,
    AdminSubscriptionExtendView,
    # Assessments
    AdminExamSetListView,
    AdminExamSetDetailView,
    AdminQuestionListView,
    AdminQuestionDetailView,
    AdminExerciseListView,
    # Source Files
    AdminSourceFileListView,
    AdminSourceFileDetailView,
    # AI Grading
    AdminGradingStatsView,
    AdminGradingJobListView,
    AdminGradingJobRetryView,
    AdminSpeakingSubmissionListView,
    AdminWritingSubmissionListView,
    # Gamification
    AdminAchievementListView,
    AdminAchievementDetailView,
    AdminCertificateListView,
    AdminXPLogListView,
    AdminXPGrantView,
    # Notifications
    AdminNotificationTemplateListView,
    AdminNotificationTemplateDetailView,
    AdminBroadcastNotificationView,
    AdminNotificationHistoryView,
    # Staff RBAC
    AdminStaffPermissionView,
    # Audit Log
    AdminAuditLogListView,
    AdminAuditLogExportView,
    # System Settings
    AdminSystemSettingListView,
    AdminSystemSettingDetailView,
    # Refund requests
    AdminRefundRequestListView,
    AdminRefundReviewView,
    # Vocabulary
    AdminVocabularyListView,
    AdminVocabularyDetailView,
    AdminVocabularyImportView,
)

urlpatterns = [
    # ── Core ─────────────────────────────────────────────────────────────────
    path("dashboard/",                    AdminDashboardView.as_view(),      name="admin-dashboard"),
    path("users/<int:pk>/ban/",           AdminUserBanView.as_view(),        name="admin-user-ban"),
    path("cefr-levels/",                  AdminCEFRLevelListView.as_view(),  name="admin-cefr-levels"),

    # ── Content ───────────────────────────────────────────────────────────────
    path("courses/",                          AdminCourseListView.as_view(),   name="admin-course-list"),
    path("courses/<int:pk>/",                 AdminCourseDetailView.as_view(), name="admin-course-detail"),
    path("courses/<int:pk>/chapters/",        AdminChapterListView.as_view(),  name="admin-chapter-list"),
    path("courses/<int:course_pk>/chapters/<int:pk>/",
                                              AdminChapterDetailView.as_view(), name="admin-chapter-detail"),
    path("courses/<int:pk>/chapters/<int:cpk>/lessons/",
                                              AdminLessonListView.as_view(),   name="admin-lesson-list"),
    path("lessons/<int:pk>/",                 AdminLessonDetailView.as_view(), name="admin-lesson-detail"),
    path("lessons/<int:pk>/exercises/",       AdminLessonExerciseListView.as_view(),  name="admin-lesson-exercise-list"),
    path("lessons/<int:lesson_pk>/exercises/<int:pk>/",
                                              AdminLessonExerciseDetailView.as_view(), name="admin-lesson-exercise-detail"),
    path("lessons/<int:pk>/files/",           AdminSourceFileListView.as_view(),  name="admin-lesson-files"),
    path("lessons/<int:pk>/files/<int:fpk>/", AdminSourceFileDetailView.as_view(), name="admin-lesson-file-detail"),
    # ── Exercise CRUD ─────────────────────────────────────────────────────────
    path("exercises/<str:exercise_type>/",            AdminExerciseTypeListView.as_view(),   name="admin-exercise-type-list"),
    path("exercises/<str:exercise_type>/<int:pk>/",   AdminExerciseTypeDetailView.as_view(), name="admin-exercise-type-detail"),
    # ── Grammar admin CRUD ────────────────────────────────────────────────────
    path("grammar/chapters/",                                      AdminGrammarChapterListView.as_view(),  name="admin-grammar-chapter-list"),
    path("grammar/chapters/<int:pk>/",                             AdminGrammarChapterDetailView.as_view(), name="admin-grammar-chapter-detail"),
    path("grammar/topics/",                                        AdminGrammarTopicListView.as_view(),    name="admin-grammar-topic-list"),
    path("grammar/topics/<int:pk>/",                               AdminGrammarTopicDetailView.as_view(),  name="admin-grammar-topic-detail"),
    path("grammar/topics/<int:topic_pk>/rules/",                   AdminGrammarRuleListView.as_view(),     name="admin-grammar-rule-list"),
    path("grammar/topics/<int:topic_pk>/rules/<int:pk>/",          AdminGrammarRuleDetailView.as_view(),   name="admin-grammar-rule-detail"),
    path("grammar/rules/<int:rule_pk>/examples/",                  AdminGrammarExampleListView.as_view(),  name="admin-grammar-example-list"),
    path("grammar/rules/<int:rule_pk>/examples/<int:pk>/",         AdminGrammarExampleDetailView.as_view(), name="admin-grammar-example-detail"),

    # ── Payments ─────────────────────────────────────────────────────────────
    path("plans/",                            AdminPlanListView.as_view(),          name="admin-plan-list"),
    path("plans/<int:pk>/",                   AdminPlanDetailView.as_view(),        name="admin-plan-detail"),
    path("coupons/",                          AdminCouponListView.as_view(),        name="admin-coupon-list"),
    path("coupons/<int:pk>/",                 AdminCouponDetailView.as_view(),      name="admin-coupon-detail"),
    path("transactions/",                     AdminTransactionListView.as_view(),   name="admin-transaction-list"),
    path("subscriptions/",                    AdminSubscriptionListView.as_view(),  name="admin-subscription-list"),
    path("subscriptions/<int:pk>/extend/",    AdminSubscriptionExtendView.as_view(), name="admin-subscription-extend"),

    # ── Assessments ───────────────────────────────────────────────────────────
    path("exam-sets/",                        AdminExamSetListView.as_view(),   name="admin-examset-list"),
    path("exam-sets/<int:pk>/",               AdminExamSetDetailView.as_view(), name="admin-examset-detail"),
    path("questions/",                        AdminQuestionListView.as_view(),  name="admin-question-list"),
    path("questions/<int:pk>/",               AdminQuestionDetailView.as_view(), name="admin-question-detail"),
    path("exercises/",                        AdminExerciseListView.as_view(),  name="admin-exercise-list"),

    # ── AI Grading ────────────────────────────────────────────────────────────
    path("grading/stats/",                        AdminGradingStatsView.as_view(),             name="admin-grading-stats"),
    path("grading/jobs/",                         AdminGradingJobListView.as_view(),           name="admin-grading-jobs"),
    path("grading/jobs/<int:pk>/retry/",          AdminGradingJobRetryView.as_view(),          name="admin-grading-retry"),
    path("grading/submissions/speaking/",         AdminSpeakingSubmissionListView.as_view(),   name="admin-speaking-list"),
    path("grading/submissions/writing/",          AdminWritingSubmissionListView.as_view(),    name="admin-writing-list"),

    # ── Gamification ──────────────────────────────────────────────────────────
    path("achievements/",                         AdminAchievementListView.as_view(),   name="admin-achievement-list"),
    path("achievements/<int:pk>/",                AdminAchievementDetailView.as_view(), name="admin-achievement-detail"),
    path("certificates/",                         AdminCertificateListView.as_view(),   name="admin-certificate-list"),
    path("xp-log/",                               AdminXPLogListView.as_view(),         name="admin-xp-log"),
    path("xp-log/grant/",                         AdminXPGrantView.as_view(),           name="admin-xp-grant"),

    # ── Notifications ─────────────────────────────────────────────────────────
    path("notification-templates/",               AdminNotificationTemplateListView.as_view(),   name="admin-notif-template-list"),
    path("notification-templates/<str:notification_type>/",
                                                  AdminNotificationTemplateDetailView.as_view(), name="admin-notif-template-detail"),
    path("notifications/broadcast/",              AdminBroadcastNotificationView.as_view(),      name="admin-notif-broadcast"),
    path("notifications/history/",                AdminNotificationHistoryView.as_view(),        name="admin-notif-history"),

    # ── Staff RBAC ────────────────────────────────────────────────────────────
    path("staff/<int:pk>/permissions/",           AdminStaffPermissionView.as_view(),  name="admin-staff-permissions"),

    # ── Audit Log ─────────────────────────────────────────────────────────────
    path("audit-log/export/",                     AdminAuditLogExportView.as_view(),   name="admin-audit-log-export"),
    path("audit-log/",                            AdminAuditLogListView.as_view(),     name="admin-audit-log"),

    # ── System Settings ───────────────────────────────────────────────────────
    path("settings/",                             AdminSystemSettingListView.as_view(),   name="admin-settings-list"),
    path("settings/<str:key>/",                   AdminSystemSettingDetailView.as_view(), name="admin-settings-detail"),

    # ── Refund Requests (created by support staff, reviewed by admin) ─────────
    path("refund-requests/",                      AdminRefundRequestListView.as_view(),   name="admin-refund-request-list"),
    path("refund-requests/<int:pk>/review/",      AdminRefundReviewView.as_view(),        name="admin-refund-request-review"),

    # ── Vocabulary ────────────────────────────────────────────────────────────
    path("vocabulary/",           AdminVocabularyListView.as_view(),   name="admin-vocabulary-list"),
    path("vocabulary/import/",    AdminVocabularyImportView.as_view(), name="admin-vocabulary-import"),
    path("vocabulary/<int:pk>/",  AdminVocabularyDetailView.as_view(), name="admin-vocabulary-detail"),
]
