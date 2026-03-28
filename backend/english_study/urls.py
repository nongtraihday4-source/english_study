from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

API = "api/v1"

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # ── Auth & Users ─────────────────────────────────────────────
    path(f"{API}/auth/", include("apps.users.urls")),

    # ── Curriculum ───────────────────────────────────────────────
    path(f"{API}/curriculum/", include("apps.curriculum.urls")),

    # ── Exercises ────────────────────────────────────────────────
    path(f"{API}/exercises/", include("apps.exercises.urls")),

    # ── Progress & Submissions ───────────────────────────────────
    path(f"{API}/progress/", include("apps.progress.urls")),

    # ── Vocabulary & Flashcards ──────────────────────────────────
    path(f"{API}/vocabulary/", include("apps.vocabulary.urls")),

    # ── Gamification ─────────────────────────────────────────────
    path(f"{API}/gamification/", include("apps.gamification.urls")),

    # ── Payments ─────────────────────────────────────────────────
    path(f"{API}/payments/", include("apps.payments.urls")),

    # ── Notifications ────────────────────────────────────────────
    path(f"{API}/notifications/", include("apps.notifications.urls")),

    # ── Grammar ──────────────────────────────────────────────────
    path(f"{API}/grammar/", include("apps.grammar.urls")),
    # ── Pronunciation ─────────────────────────────────────
    path(f"{API}/pronunciation/", include("apps.pronunciation.urls")),

    # ── Teacher Portal ────────────────────────────────────
    path(f"{API}/teacher/", include("apps.teacher.urls")),

    # ── Admin Portal ──────────────────────────────────────
    path(f"{API}/admin-portal/", include("apps.admin_portal.urls")),

    # ── Support Portal ────────────────────────────────────
    path(f"{API}/support/", include("apps.support.urls")),

    # ── API Schema & Docs ────────────────────────────────────────
    path(f"{API}/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(f"{API}/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path(f"{API}/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
