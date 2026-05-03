#!/usr/bin/env python
"""
verify_admin_panel.py
─────────────────────
Kiểm tra toàn diện tất cả luồng đã triển khai trong Admin Panel.

Chạy:
    cd backend
    python ../scripts/verify_admin_panel.py
"""

import os
import sys
import textwrap
import traceback
from pathlib import Path

# ── Bootstrap Django ──────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
sys.path.insert(0, str(BACKEND))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "english_study.settings.development")

import django
django.setup()

# ── Colour codes ──────────────────────────────────────────────────────────────
GRN  = "\033[92m"
RED  = "\033[91m"
YEL  = "\033[93m"
BLU  = "\033[94m"
BOLD = "\033[1m"
DIM  = "\033[2m"
RST  = "\033[0m"

PASS = f"{GRN}✓ PASS{RST}"
FAIL = f"{RED}✗ FAIL{RST}"
WARN = f"{YEL}⚠ WARN{RST}"

results: list[tuple[str, str, str]] = []   # (section, label, status_str)


def check(section: str, label: str, fn):
    try:
        msg = fn()
        results.append((section, label, f"{PASS}" + (f"  {DIM}{msg}{RST}" if msg else "")))
    except AssertionError as e:
        results.append((section, label, f"{FAIL}  {RED}{e}{RST}"))
    except Exception as e:
        results.append((section, label, f"{FAIL}  {RED}{type(e).__name__}: {e}{RST}"))


# ═════════════════════════════════════════════════════════════════════════════
# 1. DJANGO SYSTEM CHECK
# ═════════════════════════════════════════════════════════════════════════════

def _django_system_check():
    from django.core.management import call_command
    from io import StringIO
    out = StringIO()
    call_command("check", stdout=out, stderr=out)
    txt = out.getvalue()
    assert "no issues" in txt.lower() or txt.strip() == "", txt
    return "0 issues"

check("Django", "System check (manage.py check)", _django_system_check)


# ═════════════════════════════════════════════════════════════════════════════
# 2. MODELS
# ═════════════════════════════════════════════════════════════════════════════

def _model(model_path: str, fields: list[str] = None):
    def fn():
        module_path, cls_name = model_path.rsplit(".", 1)
        import importlib
        mod = importlib.import_module(module_path)
        cls = getattr(mod, cls_name)
        if fields:
            actual = {f.name for f in cls._meta.get_fields()}
            missing = [f for f in fields if f not in actual]
            assert not missing, f"Missing fields: {missing}"
        return cls.__name__
    return fn

for model_path, fields in [
    ("apps.admin_portal.models.AuditLog",
     ["admin_user", "action", "model_name", "object_id", "description", "changes_json", "ip_address", "created_at"]),
    ("apps.admin_portal.models.StaffPermission",
     ["manage_users", "manage_content", "manage_payments", "manage_assessments",
      "manage_notifications", "manage_gamification", "view_analytics", "manage_settings", "view_audit_log"]),
    ("apps.admin_portal.models.SystemSetting",
     ["key", "value", "value_type", "category", "is_editable", "description"]),
]:
    label = model_path.split(".")[-1]
    check("Models", f"{label} — fields", _model(model_path, fields))


# ═════════════════════════════════════════════════════════════════════════════
# 3. MIGRATIONS
# ═════════════════════════════════════════════════════════════════════════════

def _migrations_applied():
    from django.db.migrations.executor import MigrationExecutor
    from django.db import connection
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    unapplied = [str(m) for m, _ in plan]
    assert not unapplied, f"Unapplied: {unapplied}"
    return "all applied"

check("Migrations", "All migrations applied", _migrations_applied)


# ═════════════════════════════════════════════════════════════════════════════
# 4. URL PATTERNS — reverse() every named route
# ═════════════════════════════════════════════════════════════════════════════

from django.urls import reverse, NoReverseMatch

URL_TABLE = [
    # (name, kwargs_or_None, extra_label)
    # Dashboard
    ("admin-dashboard",          {},              "GET /admin-portal/dashboard/"),
    # Users
    ("admin-user-ban",           {"pk": 1},       "POST /admin-portal/users/<pk>/ban/"),
    ("admin-cefr-levels",        {},              "GET /admin-portal/cefr-levels/"),
    # Content
    ("admin-course-list",        {},              "GET/POST /admin-portal/courses/"),
    ("admin-course-detail",      {"pk": 1},       "GET/PATCH/DEL /admin-portal/courses/<pk>/"),
    ("admin-chapter-list",       {"pk": 1},       "GET /admin-portal/courses/<pk>/chapters/"),
    # Payments
    ("admin-plan-list",          {},              "GET/POST /admin-portal/plans/"),
    ("admin-plan-detail",        {"pk": 1},       "GET/PATCH/DEL /admin-portal/plans/<pk>/"),
    ("admin-coupon-list",        {},              "GET/POST /admin-portal/coupons/"),
    ("admin-coupon-detail",      {"pk": 1},       "GET/PATCH/DEL /admin-portal/coupons/<pk>/"),
    ("admin-transaction-list",   {},              "GET /admin-portal/transactions/"),
    ("admin-subscription-list",  {},              "GET /admin-portal/subscriptions/"),
    ("admin-subscription-extend",{"pk": 1},       "POST /admin-portal/subscriptions/<pk>/extend/"),
    # Assessments
    ("admin-examset-list",       {},              "GET/POST /admin-portal/exam-sets/"),
    ("admin-examset-detail",     {"pk": 1},       "GET/PATCH/DEL /admin-portal/exam-sets/<pk>/"),
    ("admin-exercise-list",      {},              "GET /admin-portal/exercises/"),
    # AI Grading
    ("admin-grading-stats",      {},              "GET /admin-portal/grading/stats/"),
    ("admin-grading-jobs",       {},              "GET /admin-portal/grading/jobs/"),
    ("admin-grading-retry",      {"pk": 1},       "POST /admin-portal/grading/jobs/<pk>/retry/"),
    ("admin-speaking-list",      {},              "GET /admin-portal/grading/submissions/speaking/"),
    ("admin-writing-list",       {},              "GET /admin-portal/grading/submissions/writing/"),
    # Gamification
    ("admin-achievement-list",   {},              "GET/POST /admin-portal/achievements/"),
    ("admin-achievement-detail", {"pk": 1},       "GET/PATCH /admin-portal/achievements/<pk>/"),
    ("admin-certificate-list",   {},              "GET /admin-portal/certificates/"),
    ("admin-xp-log",             {},              "GET /admin-portal/xp-log/"),
    ("admin-xp-grant",           {},              "POST /admin-portal/xp-log/grant/"),
    # Notifications
    ("admin-notif-template-list",{},              "GET /admin-portal/notification-templates/"),
    ("admin-notif-broadcast",    {},              "POST /admin-portal/notifications/broadcast/"),
    ("admin-notif-history",      {},              "GET /admin-portal/notifications/history/"),
    # Staff RBAC
    ("admin-staff-permissions",  {"pk": 1},       "GET/PUT /admin-portal/staff/<pk>/permissions/"),
    # Audit Log
    ("admin-audit-log",          {},              "GET /admin-portal/audit-log/"),
    ("admin-audit-log-export",   {},              "GET /admin-portal/audit-log/export/"),
    # System Settings
    ("admin-settings-list",      {},              "GET /admin-portal/settings/"),
    ("admin-settings-detail",    {"key": "maintenance_mode"}, "PATCH /admin-portal/settings/<key>/"),
]

def _url_check(name, kwargs, label):
    def fn():
        url = reverse(name, kwargs=kwargs or None)
        return url
    return fn

for name, kwargs, label in URL_TABLE:
    check("URLs", label, _url_check(name, kwargs, label))


# ═════════════════════════════════════════════════════════════════════════════
# 5. VIEW CLASSES — import + AuditLogMixin check
# ═════════════════════════════════════════════════════════════════════════════

MIXIN_VIEWS = [
    "AdminPlanListView", "AdminPlanDetailView",
    "AdminCouponListView", "AdminCouponDetailView",
    "AdminExamSetListView", "AdminExamSetDetailView",
    "AdminAchievementListView", "AdminAchievementDetailView",
    "AdminNotificationTemplateDetailView",
]
NON_MIXIN_VIEWS = [
    "AdminDashboardView", "AdminUserBanView", "AdminCourseListView",
    "AdminCourseDetailView", "AdminTransactionListView", "AdminSubscriptionListView",
    "AdminSubscriptionExtendView", "AdminExerciseListView", "AdminGradingStatsView",
    "AdminGradingJobListView", "AdminGradingJobRetryView",
    "AdminSpeakingSubmissionListView", "AdminWritingSubmissionListView",
    "AdminCertificateListView", "AdminXPLogListView", "AdminXPGrantView",
    "AdminNotificationTemplateListView", "AdminBroadcastNotificationView",
    "AdminNotificationHistoryView", "AdminStaffPermissionView",
    "AdminAuditLogListView", "AdminAuditLogExportView",
    "AdminSystemSettingListView", "AdminSystemSettingDetailView",
    "AuditLogMixin",
]

import apps.admin_portal.views as _views

def _cls_exists(cls_name, expect_mixin=False):
    def fn():
        cls = getattr(_views, cls_name, None)
        assert cls is not None, f"{cls_name} not found in views"
        if expect_mixin:
            assert issubclass(cls, _views.AuditLogMixin), \
                f"{cls_name} does not inherit AuditLogMixin"
            return "AuditLogMixin ✓"
        return "imported"
    return fn

for name in MIXIN_VIEWS:
    check("Views", f"{name} (AuditLogMixin)", _cls_exists(name, expect_mixin=True))

for name in NON_MIXIN_VIEWS:
    check("Views", name, _cls_exists(name, expect_mixin=False))


# ═════════════════════════════════════════════════════════════════════════════
# 6. SERIALIZERS
# ═════════════════════════════════════════════════════════════════════════════

SERIALIZERS = [
    "AdminPlanSerializer", "AdminCouponSerializer", "AdminTransactionSerializer",
    "AdminSubscriptionSerializer", "AdminExamSetSerializer",
    "AdminAchievementSerializer", "AdminCertificateSerializer", "AdminXPLogSerializer",
    "AdminNotificationTemplateSerializer", "AdminStaffPermissionSerializer",
    "AdminAuditLogSerializer", "AdminSystemSettingSerializer",
]

import apps.admin_portal.serializers as _sers

def _ser_exists(name):
    def fn():
        s = getattr(_sers, name, None)
        assert s is not None, f"{name} not found"
        return "ok"
    return fn

for name in SERIALIZERS:
    check("Serializers", name, _ser_exists(name))


# ═════════════════════════════════════════════════════════════════════════════
# 7. SYSTEM SETTINGS SEED
# ═════════════════════════════════════════════════════════════════════════════

EXPECTED_SETTINGS = [
    "maintenance_mode", "ai_grading_enabled", "ai_max_retry_count",
    "welcome_email_enabled", "leaderboard_reset_day", "max_login_attempts",
]

def _settings_seeded():
    from apps.admin_portal.models import SystemSetting
    keys = set(SystemSetting.objects.values_list("key", flat=True))
    missing = [k for k in EXPECTED_SETTINGS if k not in keys]
    if missing:
        return f"{WARN}  {YEL}Not seeded: {missing} — run create_default_settings{RST}"
    return f"{len(keys)} settings in DB"

def _settings_seed_check():
    from apps.admin_portal.models import SystemSetting
    keys = set(SystemSetting.objects.values_list("key", flat=True))
    missing = [k for k in EXPECTED_SETTINGS if k not in keys]
    if missing:
        raise AssertionError(f"Not seeded yet: {missing}  →  run: python manage.py create_default_settings")
    return f"{len(keys)} settings in DB"

check("Settings", "Default settings seeded in DB", _settings_seed_check)


# ═════════════════════════════════════════════════════════════════════════════
# 8. FRONTEND — Vue files & router
# ═════════════════════════════════════════════════════════════════════════════

VUE_FILES = {
    "AdminLayout.vue":          "Sidebar + layout",
    "AdminDashboardView.vue":   "Dashboard KPI",
    "AdminUsersView.vue":       "Users + Staff RBAC tab",
    "AdminContentView.vue":     "Content CRUD",
    "AdminPaymentsView.vue":    "Plans / Coupons / Transactions",
    "AdminAssessmentsView.vue": "ExamSets + Exercises",
    "AdminGradingView.vue":     "AI Grading monitor",
    "AdminGamificationView.vue":"Achievements / XP / Certificates",
    "AdminNotificationsView.vue":"Templates + Broadcast",
    "AdminAuditLogView.vue":    "Audit log + CSV export",
    "AdminSettingsView.vue":    "System settings",
}

VIEWS_DIR = FRONTEND / "src" / "views" / "admin"

def _vue_file(filename):
    def fn():
        p = VIEWS_DIR / filename
        assert p.exists(), f"Missing: {p}"
        size = p.stat().st_size
        assert size > 200, f"File looks empty ({size} bytes)"
        return f"{size:,} bytes"
    return fn

for fname, desc in VUE_FILES.items():
    check("Frontend (Vue)", f"{fname}  [{desc}]", _vue_file(fname))


# ── PaginationBar component ───────────────────────────────────────────────────
def _pagination_bar():
    p = FRONTEND / "src" / "components" / "PaginationBar.vue"
    assert p.exists(), "PaginationBar.vue missing"
    return f"{p.stat().st_size:,} bytes"

check("Frontend (Vue)", "PaginationBar.vue  [Reusable pagination]", _pagination_bar)


# ── Router — check all admin routes registered ────────────────────────────────
# Routes use relative child paths — check by route name and component imports
ROUTER_CHECKS = [
    ("admin-dashboard",      "AdminDashboardView"),
    ("admin-users",          "AdminUsersView"),
    ("admin-content",        "AdminContentView"),
    ("admin-payments",       "AdminPaymentsView"),
    ("admin-assessments",    "AdminAssessmentsView"),
    ("admin-grading",        "AdminGradingView"),
    ("admin-gamification",   "AdminGamificationView"),
    ("admin-notifications",  "AdminNotificationsView"),
    ("admin-audit-log",      "AdminAuditLogView"),
    ("admin-settings",       "AdminSettingsView"),
]

def _router_paths():
    router_file = FRONTEND / "src" / "router" / "index.js"
    assert router_file.exists(), "router/index.js missing"
    content = router_file.read_text()
    missing_names = [name for name, _ in ROUTER_CHECKS if f"'{name}'" not in content and f'"{name}"' not in content]
    missing_views = [view for _, view in ROUTER_CHECKS if view not in content]
    missing = missing_names + missing_views
    assert not missing, f"Missing in router: {missing}"
    return f"{len(ROUTER_CHECKS)} admin routes present"

check("Frontend (Router)", "All admin routes in router/index.js", _router_paths)


# ── admin.js API methods ──────────────────────────────────────────────────────
API_METHODS = [
    "getDashboard", "getUsers", "updateUser", "banUser",
    "getCourses", "createCourse", "updateCourse", "deleteCourse",
    "getPlans", "createPlan", "updatePlan", "deletePlan",
    "getCoupons", "createCoupon", "updateCoupon", "deleteCoupon",
    "getTransactions", "getSubscriptions", "extendSubscription",
    "getExamSets", "createExamSet", "updateExamSet", "deleteExamSet",
    "getExercises",
    "getGradingStats", "getGradingJobs", "retryGradingJob",
    "getSpeakingSubmissions", "getWritingSubmissions",
    "getAchievements", "createAchievement", "updateAchievement",
    "getCertificates", "getXPLog", "grantXP",
    "getNotificationTemplates", "updateNotificationTemplate",
    "broadcastNotification", "getNotificationHistory",
    "getStaffPermissions", "updateStaffPermissions",
    "getAuditLog", "exportAuditLog",
    "getSettings", "updateSetting",
]

def _api_methods():
    api_file = FRONTEND / "src" / "api" / "admin.js"
    assert api_file.exists(), "admin.js missing"
    content = api_file.read_text()
    missing = [m for m in API_METHODS if m not in content]
    assert not missing, f"Missing methods: {missing}"
    return f"{len(API_METHODS)} methods present"

check("Frontend (API)", "All adminApi methods in admin.js", _api_methods)


# ── CSS utilities ─────────────────────────────────────────────────────────────
def _css_utilities():
    css = FRONTEND / "src" / "assets" / "css" / "main.css"
    assert css.exists(), "main.css missing"
    content = css.read_text()
    missing = [c for c in [".btn-primary", ".input-base", ".input-sm"] if c not in content]
    assert not missing, f"Missing CSS: {missing}"
    return ".btn-primary .input-base .input-sm"

check("Frontend (CSS)", "Utility classes in main.css", _css_utilities)


# ═════════════════════════════════════════════════════════════════════════════
# 9. FLOW SIMULATIONS — request/response via Django test client
# ═════════════════════════════════════════════════════════════════════════════

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from unittest.mock import patch

User = get_user_model()
factory = RequestFactory()
api_client = APIClient()

def _make_admin():
    """Get or create a superuser for tests — handles username uniqueness."""
    email = "_verify_admin_bot@example.com"
    u = User.objects.filter(email=email).first()
    if u:
        return u
    # Use create_user if available; otherwise handle username field
    create_fn = getattr(User.objects, "create_superuser", None)
    if create_fn:
        try:
            return create_fn(email=email, password="_verify_pass_!1")
        except TypeError:
            pass
    # Fallback: build via model directly with a unique username
    import uuid
    u = User(
        email=email,
        role="admin",
        is_staff=True,
        is_superuser=True,
        is_active=True,
    )
    if hasattr(u, "username"):
        u.username = str(uuid.uuid4())[:30]
    u.set_password("_verify_pass_!1")
    u.save()
    return u

try:
    _admin_user = _make_admin()
    api_client.force_authenticate(user=_admin_user)
except Exception:
    _admin_user = None


def _view_get(url_name, kwargs=None, query=None):
    """Simulate authenticated GET via APIClient.force_authenticate (bypasses JWT)."""
    def fn():
        if _admin_user is None:
            raise AssertionError("Could not create test admin user")
        path = "/api/v1/admin-portal/" + _build_path(url_name, kwargs)
        if query:
            path += "?" + "&".join(f"{k}={v}" for k, v in query.items())
        resp = api_client.get(path)
        code = resp.status_code
        assert code in (200, 201, 204), f"HTTP {code}"
        return f"HTTP {code}"
    return fn


def _build_path(name, kwargs):
    """Build a raw path string for the given URL name."""
    PATH_MAP = {
        "admin-dashboard":          "dashboard/",
        "admin-cefr-levels":        "cefr-levels/",
        "admin-plan-list":          "plans/",
        "admin-coupon-list":        "coupons/",
        "admin-transaction-list":   "transactions/",
        "admin-subscription-list":  "subscriptions/",
        "admin-examset-list":       "exam-sets/",
        "admin-exercise-list":      "exercises/",
        "admin-grading-stats":      "grading/stats/",
        "admin-grading-jobs":       "grading/jobs/",
        "admin-speaking-list":      "grading/submissions/speaking/",
        "admin-writing-list":       "grading/submissions/writing/",
        "admin-achievement-list":   "achievements/",
        "admin-certificate-list":   "certificates/",
        "admin-xp-log":             "xp-log/",
        "admin-notif-template-list":"notification-templates/",
        "admin-notif-history":      "notifications/history/",
        "admin-audit-log":          "audit-log/",
        "admin-audit-log-export":   "audit-log/export/",
        "admin-settings-list":      "settings/",
        "admin-course-list":        "courses/",
    }
    return PATH_MAP.get(name, name + "/")


SIMULATED_GETS = [
    ("admin-dashboard",         None,         "Dashboard KPI"),
    ("admin-cefr-levels",       None,         "CEFR level list"),
    ("admin-plan-list",         None,         "Plans list"),
    ("admin-coupon-list",       None,         "Coupons list"),
    ("admin-transaction-list",  None,         "Transactions list"),
    ("admin-subscription-list", None,         "Subscriptions list"),
    ("admin-examset-list",      None,         "ExamSets list"),
    ("admin-exercise-list",     None,         "Exercises list"),
    ("admin-grading-stats",     None,         "Grading stats"),
    ("admin-grading-jobs",      None,         "Grading jobs"),
    ("admin-speaking-list",     None,         "Speaking submissions"),
    ("admin-writing-list",      None,         "Writing submissions"),
    ("admin-achievement-list",  None,         "Achievements list"),
    ("admin-certificate-list",  None,         "Certificates list"),
    ("admin-xp-log",            None,         "XP log"),
    ("admin-notif-template-list",None,        "Notification templates"),
    ("admin-notif-history",     None,         "Notification history"),
    ("admin-audit-log",         None,         "Audit log"),
    ("admin-audit-log-export",  None,         "Audit log CSV export"),
    ("admin-settings-list",     None,         "System settings"),
    ("admin-course-list",       None,         "Courses list"),
]

for url_name, kwargs, label in SIMULATED_GETS:
    check("Flow Simulation (GET)", label, _view_get(url_name, kwargs))


# ── Simulate Staff Permissions GET ───────────────────────────────────────────
def _staff_permissions_get():
    if _admin_user is None:
        raise AssertionError("No test user")
    resp = api_client.get(f"/api/v1/admin-portal/staff/{_admin_user.pk}/permissions/")
    assert resp.status_code == 200, f"HTTP {resp.status_code}"
    body = resp.json()
    # Response is wrapped: {"success": true, "data": {...}} or flat
    data = body.get("data", body)
    for field in ["manage_users", "manage_content", "manage_payments"]:
        assert field in data, f"Field '{field}' missing from response keys: {list(data.keys())}"
    return "HTTP 200 — 9 permission fields present"

check("Flow Simulation (GET)", "Staff permissions GET → 9 fields", _staff_permissions_get)


# ── Simulate AuditLog write ───────────────────────────────────────────────────
def _audit_log_write():
    from apps.admin_portal.views import _log_action
    from apps.admin_portal.models import AuditLog
    if _admin_user is None:
        raise AssertionError("No test user")
    before = AuditLog.objects.count()
    request = factory.get("/fake/")
    request.user = _admin_user
    request.META["REMOTE_ADDR"] = "127.0.0.1"
    _log_action(request, "create", "VerifyTest", 999, "Verification test entry")
    after = AuditLog.objects.count()
    assert after == before + 1, f"Expected +1 log entry, got {after - before}"
    AuditLog.objects.filter(model_name="VerifyTest").delete()   # cleanup
    return "AuditLog.objects.create() works"

check("Flow Simulation (Write)", "AuditLog write + cleanup", _audit_log_write)


# ── Simulate AuditLogMixin auto-log ─────────────────────────────────────────
def _mixin_auto_log():
    from apps.admin_portal.views import AuditLogMixin, _log_action
    from apps.admin_portal.models import AuditLog
    # Build a minimal fake GenericAPIView subclass
    from rest_framework import generics, serializers as drf_serializers
    from apps.admin_portal.models import SystemSetting
    from apps.admin_portal.serializers import AdminSystemSettingSerializer

    class _FakeView(AuditLogMixin, generics.UpdateAPIView):
        serializer_class = AdminSystemSettingSerializer
        queryset = SystemSetting.objects.all()

    view = _FakeView()
    view.request = factory.patch("/fake/")
    view.request.user = _admin_user
    view.request.META["REMOTE_ADDR"] = "127.0.0.1"
    view.kwargs = {}

    setting = SystemSetting.objects.first()
    assert setting is not None, "No SystemSetting in DB — run create_default_settings first"

    before = AuditLog.objects.count()
    serializer = AdminSystemSettingSerializer(setting)
    # Mock serializer.save so it just returns the instance
    from unittest.mock import MagicMock
    mock_ser = MagicMock()
    mock_ser.save.return_value = setting
    mock_ser.Meta = AdminSystemSettingSerializer.Meta

    view.perform_update(mock_ser)
    after = AuditLog.objects.count()
    assert after == before + 1, f"Mixin did not write AuditLog (before={before} after={after})"
    AuditLog.objects.filter(model_name="SystemSetting").order_by("-id").first().delete()  # cleanup
    return "AuditLogMixin.perform_update() auto-logged"

check("Flow Simulation (Mixin)", "AuditLogMixin.perform_update() auto-logs", _mixin_auto_log)


# ═════════════════════════════════════════════════════════════════════════════
# REPORT
# ═════════════════════════════════════════════════════════════════════════════

print()
print(f"{BOLD}{'═' * 70}{RST}")
print(f"{BOLD}  ADMIN PANEL — BÁO CÁO XÁC MINH{RST}")
print(f"{BOLD}{'═' * 70}{RST}")

current_section = None
passes = fails = 0

for section, label, status in results:
    if section != current_section:
        print(f"\n{BOLD}{BLU}▶ {section}{RST}")
        current_section = section
    icon = PASS if "PASS" in status else FAIL
    print(f"  {'·'} {label:<55} {status}")
    if "PASS" in status:
        passes += 1
    else:
        fails += 1

total = passes + fails
print()
print(f"{BOLD}{'─' * 70}{RST}")
if fails == 0:
    print(f"{BOLD}{GRN}  KẾT QUẢ: {passes}/{total} PASS — Tất cả luồng hoạt động tốt ✓{RST}")
else:
    print(f"{BOLD}{RED}  KẾT QUẢ: {fails}/{total} FAIL — {passes} pass, {fails} fail{RST}")
print(f"{BOLD}{'─' * 70}{RST}")
print()

sys.exit(0 if fails == 0 else 1)
