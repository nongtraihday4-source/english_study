"""
simulate_teacher_portal.py
──────────────────────────
Simulation / integration test for the Teacher Portal API.
Chạy bằng lệnh:
    cd /home/n2t/Documents/english_study/backend
    python scripts/simulate_teacher_portal.py

Script tự động:
  1. Thiết lập Django environment
  2. Tạo (hoặc tìm) teacher user + seed dữ liệu mẫu nếu DB trống
  3. Gọi từng endpoint Teacher Portal bằng DRF APIClient (không cần server)
  4. In báo cáo chi tiết mỗi endpoint
"""

import os
import sys
import json

# ── Bootstrap Django ──────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "english_study.settings.development")

import django
django.setup()

# ── Imports (after django.setup) ──────────────────────────────────────────────
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from apps.progress.models import (
    SpeakingSubmission, WritingSubmission, UserEnrollment
)
from apps.curriculum.models import Course

User = get_user_model()

# ── Colours ────────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

def ok(msg):    print(f"  {GREEN}✓{RESET} {msg}")
def fail(msg):  print(f"  {RED}✗{RESET} {msg}")
def info(msg):  print(f"  {CYAN}→{RESET} {msg}")
def warn(msg):  print(f"  {YELLOW}⚠{RESET} {msg}")
def header(msg):print(f"\n{BOLD}{CYAN}{'─'*60}{RESET}\n{BOLD}{CYAN}  {msg}{RESET}\n{DIM}{'─'*60}{RESET}")
def sep():      print(f"{DIM}{'·'*60}{RESET}")


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 1 — Chuẩn bị teacher user
# ═══════════════════════════════════════════════════════════════════════════════
header("STEP 1 — Chuẩn bị Teacher User")

TEACHER_EMAIL = "sim_teacher@english.study"
teacher, created = User.objects.get_or_create(
    email=TEACHER_EMAIL,
    defaults={
        "username": "sim_teacher",
        "first_name": "Sim", "last_name": "Teacher",
        "role": "teacher", "is_active": True, "is_deleted": False,
    }
)
if created:
    teacher.set_password("SimTeacher@2025!")
    teacher.save()
    ok(f"Đã tạo teacher user: {TEACHER_EMAIL}")
else:
    if teacher.role != "teacher":
        teacher.role = "teacher"
        teacher.save(update_fields=["role"])
        ok(f"Đã cập nhật role=teacher cho: {TEACHER_EMAIL}")
    else:
        ok(f"Dùng teacher user có sẵn: {TEACHER_EMAIL} (id={teacher.id})")

info(f"role={teacher.role}, is_active={teacher.is_active}")


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 2 — Seed dữ liệu mẫu nếu cần
# ═══════════════════════════════════════════════════════════════════════════════
header("STEP 2 — Seed dữ liệu mẫu")

# ── Student user ──────────────────────────────────────────────────────────────
STUDENT_EMAIL = "sim_student@english.study"
student, s_created = User.objects.get_or_create(
    email=STUDENT_EMAIL,
    defaults={
        "username": "sim_student",
        "first_name": "Sim", "last_name": "Student",
        "role": "student", "is_active": True, "is_deleted": False,
    }
)
if s_created:
    student.set_password("SimStudent@2025!")
    student.save()
    ok(f"Tạo student user: {STUDENT_EMAIL}")
else:
    ok(f"Student user có sẵn: {STUDENT_EMAIL} (id={student.id})")

# ── Course ────────────────────────────────────────────────────────────────────
from apps.curriculum.models import CEFRLevel

level_b1, _ = CEFRLevel.objects.get_or_create(
    code="B1",
    defaults={"name": "Intermediate", "name_vi": "Trung cấp", "order": 3, "is_active": True},
)

course, c_created = Course.objects.get_or_create(
    slug="sim-b1-general-english",
    defaults={"title": "[SIM] B1 General English", "level": level_b1, "order": 1, "is_active": True},
)
if c_created:
    ok(f"Tạo course: {course.title} (id={course.id})")
else:
    ok(f"Course có sẵn: {course.title} (id={course.id})")

# ── Enrollment ────────────────────────────────────────────────────────────────
enroll, e_created = UserEnrollment.objects.get_or_create(
    user=student, course=course,
    defaults={"status": "active", "is_deleted": False},
)
if e_created:
    ok(f"Tạo enrollment: student={student.id} → course={course.id}")
else:
    ok("Enrollment có sẵn")

# ── Speaking submission (pending) ──────────────────────────────────────────────
sp_pending = SpeakingSubmission.objects.filter(
    user=student, status="pending", is_deleted=False
).first()
if not sp_pending:
    sp_pending = SpeakingSubmission.objects.create(
        user=student, exercise_id=1,
        status="pending", is_deleted=False,
        transcript="The cat sat on the mat",
        target_sentence="The cat sat on the mat.",
    )
    ok(f"Tạo SpeakingSubmission pending (id={sp_pending.id})")
else:
    ok(f"SpeakingSubmission pending có sẵn (id={sp_pending.id})")

# ── Writing submission (pending) ───────────────────────────────────────────────
wr_pending = WritingSubmission.objects.filter(
    user=student, status="pending", is_deleted=False
).first()
if not wr_pending:
    _text = "I am learning English every day to improve my skills."
    wr_pending = WritingSubmission.objects.create(
        user=student, exercise_id=1,
        status="pending", is_deleted=False,
        content_text=_text,
        word_count=len(_text.split()),
    )
    ok(f"Tạo WritingSubmission pending (id={wr_pending.id})")
else:
    ok(f"WritingSubmission pending có sẵn (id={wr_pending.id})")


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 3 — Gọi các Endpoint qua APIClient
# ═══════════════════════════════════════════════════════════════════════════════
header("STEP 3 — Simulation các Teacher Portal Endpoint")

client = APIClient()
client.force_authenticate(user=teacher)

results = []

def call(method, url, payload=None, label=""):
    """Gọi endpoint và trả về (status_code, data, ok)."""
    fn = getattr(client, method.lower())
    r = fn(url, data=payload, format="json") if payload else fn(url)
    passed = 200 <= r.status_code < 300
    results.append({"label": label, "method": method.upper(), "url": url,
                     "status": r.status_code, "ok": passed})
    return r.status_code, r.data if hasattr(r, "data") else {}, passed

# ── 1. Dashboard ──────────────────────────────────────────────────────────────
sep()
print(f"\n{BOLD}[1/6] GET /api/v1/teacher/dashboard/{RESET}")
code, data, passed = call("get", "/api/v1/teacher/dashboard/", label="Dashboard")
if passed:
    ok(f"HTTP {code}")
    info(f"pending_grading      = {data.get('pending_grading')}")
    info(f"pending_speaking     = {data.get('pending_speaking')}")
    info(f"pending_writing      = {data.get('pending_writing')}")
    info(f"total_students       = {data.get('total_students')}")
    info(f"active_courses       = {data.get('active_courses')}")
    info(f"avg_speaking_score   = {data.get('avg_speaking_score')}")
    info(f"avg_writing_score    = {data.get('avg_writing_score')}")
    sp_dist = data.get("speaking_score_distribution", [])
    wr_dist = data.get("writing_score_distribution", [])
    info(f"speaking_dist buckets = {len(sp_dist)}, writing_dist buckets = {len(wr_dist)}")
else:
    fail(f"HTTP {code}: {data}")

# ── 2. Grading Queue — pending all ────────────────────────────────────────────
sep()
print(f"\n{BOLD}[2/6] GET /api/v1/teacher/grading-queue/?status=pending&type=all{RESET}")
code, data, passed = call("get", "/api/v1/teacher/grading-queue/?status=pending&type=all", label="GradingQueue(pending,all)")
if passed:
    ok(f"HTTP {code}")
    items = data.get("results", data) if isinstance(data, dict) else data
    count = data.get("count", len(items)) if isinstance(data, dict) else len(items)
    info(f"Total pending items  = {count}")
    for item in (items[:3] if isinstance(items, list) else []):
        info(f"  id={item.get('id')} type={item.get('type')} status={item.get('status')} student={item.get('student', {}).get('email','?')}")
else:
    fail(f"HTTP {code}: {data}")

# ── 3. Grading Queue — completed speaking ─────────────────────────────────────
sep()
print(f"\n{BOLD}[3/6] GET /api/v1/teacher/grading-queue/?status=completed&type=speaking{RESET}")
code, data, passed = call("get", "/api/v1/teacher/grading-queue/?status=completed&type=speaking", label="GradingQueue(completed,speaking)")
if passed:
    ok(f"HTTP {code}")
    items = data.get("results", data) if isinstance(data, dict) else data
    count = data.get("count", len(items)) if isinstance(data, dict) else len(items)
    info(f"Completed speaking   = {count}")
else:
    fail(f"HTTP {code}: {data}")

# ── 4. Grade Speaking ─────────────────────────────────────────────────────────
sep()
print(f"\n{BOLD}[4/6] POST /api/v1/teacher/grade/speaking/{sp_pending.id}/{RESET}")
payload = {"score": 82, "feedback": "[SIM] Phát âm tốt, cần cải thiện nhịp điệu."}
code, data, passed = call("post", f"/api/v1/teacher/grade/speaking/{sp_pending.id}/",
                           payload=payload, label=f"GradeSpeaking(id={sp_pending.id})")
if passed:
    ok(f"HTTP {code}")
    info(f"id={data.get('id')} status={data.get('status')} ai_score={data.get('ai_score')}")
    info(f"feedback_vi = {str(data.get('feedback_vi',''))[:60]}")
else:
    fail(f"HTTP {code}: {data}")

# ── 5. Grade Writing ──────────────────────────────────────────────────────────
sep()
print(f"\n{BOLD}[5/6] POST /api/v1/teacher/grade/writing/{wr_pending.id}/{RESET}")
payload = {"score": 76, "feedback": "[SIM] Ý tưởng rõ ràng, cần thêm từ nối liên kết."}
code, data, passed = call("post", f"/api/v1/teacher/grade/writing/{wr_pending.id}/",
                           payload=payload, label=f"GradeWriting(id={wr_pending.id})")
if passed:
    ok(f"HTTP {code}")
    info(f"id={data.get('id')} status={data.get('status')} ai_score={data.get('ai_score')}")
    info(f"feedback_text = {str(data.get('feedback_text',''))[:60]}")
else:
    fail(f"HTTP {code}: {data}")

# ── 6. Class list ─────────────────────────────────────────────────────────────
sep()
print(f"\n{BOLD}[6a/6] GET /api/v1/teacher/classes/{RESET}")
code, data, passed = call("get", "/api/v1/teacher/classes/", label="ClassList")
if passed:
    ok(f"HTTP {code}")
    items = data.get("results", data) if isinstance(data, dict) else data
    count = data.get("count", len(items)) if isinstance(data, dict) else len(items)
    info(f"Total courses        = {count}")
    for c in (items[:3] if isinstance(items, list) else []):
        info(f"  id={c.get('id')} title=\"{c.get('title')}\" cefr={c.get('cefr_level')} students={c.get('student_count')}")
else:
    fail(f"HTTP {code}: {data}")

sep()
print(f"\n{BOLD}[6b/6] GET /api/v1/teacher/classes/{course.id}/students/{RESET}")
code, data, passed = call("get", f"/api/v1/teacher/classes/{course.id}/students/",
                           label=f"ClassStudents(id={course.id})")
if passed:
    ok(f"HTTP {code}")
    students_list = data.get("students", [])
    info(f"Course: {data.get('course', {}).get('title')}")
    info(f"Student count: {data.get('count')}")
    for s in students_list[:3]:
        info(f"  {s.get('email')} level={s.get('current_level')} status={s.get('status')} progress={s.get('progress_percent')}%")
else:
    fail(f"HTTP {code}: {data}")


# ═══════════════════════════════════════════════════════════════════════════════
#  STEP 4 — Permission guard test (student should be denied)
# ═══════════════════════════════════════════════════════════════════════════════
header("STEP 4 — Kiểm tra Permission Guard")

student_client = APIClient()
student_client.force_authenticate(user=student)
r = student_client.get("/api/v1/teacher/dashboard/")
if r.status_code == 403:
    ok(f"Student bị từ chối đúng cách → HTTP {r.status_code} 403 Forbidden")
    results.append({"label": "PermGuard(student→403)", "method": "GET",
                     "url": "/api/v1/teacher/dashboard/", "status": r.status_code, "ok": True})
else:
    fail(f"Kỳ vọng 403, nhận {r.status_code} — có thể cần kiểm tra IsTeacher permission")
    results.append({"label": "PermGuard(student→403)", "method": "GET",
                     "url": "/api/v1/teacher/dashboard/", "status": r.status_code, "ok": False})

unauth_client = APIClient()
r2 = unauth_client.get("/api/v1/teacher/dashboard/")
if r2.status_code in (401, 403):
    ok(f"Anonymous bị từ chối → HTTP {r2.status_code}")
    results.append({"label": "PermGuard(anon→401/403)", "method": "GET",
                     "url": "/api/v1/teacher/dashboard/", "status": r2.status_code, "ok": True})
else:
    fail(f"Kỳ vọng 401/403, nhận {r2.status_code}")
    results.append({"label": "PermGuard(anon→401/403)", "method": "GET",
                     "url": "/api/v1/teacher/dashboard/", "status": r2.status_code, "ok": False})


# ─── Re-verify dashboard after grading ────────────────────────────────────────
sep()
print(f"\n  {DIM}[Verify] Dashboard sau khi chấm bài...{RESET}")
r = client.get("/api/v1/teacher/dashboard/")
if r.status_code == 200:
    d = r.data
    info(f"pending_grading (sau khi chấm) = {d.get('pending_grading')}")
    info(f"avg_speaking_score             = {d.get('avg_speaking_score')}")
    info(f"avg_writing_score              = {d.get('avg_writing_score')}")


# ═══════════════════════════════════════════════════════════════════════════════
#  FINAL REPORT
# ═══════════════════════════════════════════════════════════════════════════════
header("BÁO CÁO TỔNG HỢP")

passed_cnt = sum(1 for r in results if r["ok"])
total_cnt  = len(results)
all_pass   = passed_cnt == total_cnt

print(f"\n  {'Test':<46} {'Method':<6} {'Status':<6} {'Kết quả'}")
print(f"  {'─'*46} {'─'*6} {'─'*6} {'─'*8}")
for r in results:
    icon  = f"{GREEN}PASS{RESET}" if r["ok"] else f"{RED}FAIL{RESET}"
    color = GREEN if r["ok"] else RED
    print(f"  {r['label']:<46} {color}{r['method']:<6}{RESET} {color}{r['status']:<6}{RESET} {icon}")

print()
if all_pass:
    print(f"  {GREEN}{BOLD}🎉 Tất cả {total_cnt}/{total_cnt} test PASS{RESET}")
else:
    print(f"  {RED}{BOLD}⚠ {passed_cnt}/{total_cnt} test PASS — {total_cnt - passed_cnt} FAIL{RESET}")

print(f"\n  {DIM}Teacher Portal API simulation hoàn tất.{RESET}\n")
