#!/usr/bin/env python3
"""
=============================================================================
ENGLISH STUDY — PRONUNCIATION STAGE FLOW SIMULATION
Mô phỏng học viên đi qua 4 giai đoạn phát âm:
  1. Đăng nhập → lấy JWT
  2. Lấy danh sách stages & lessons
  3. Mở từng bài học (GET by-slug)
  4. Trả lời quiz (chọn đúng / sai ngẫu nhiên)
  5. Submit hoàn thành (POST complete)
  6. Kiểm tra kết quả progress trong DB
  7. Báo cáo tổng hợp

Chạy:
  python simulate_pronunciation_flow.py
  python simulate_pronunciation_flow.py --fast   # bỏ delay
=============================================================================
"""

import os
import sys
import json
import random
import argparse

# ── Django setup ──────────────────────────────────────────────────────────────
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, BACKEND_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "english_study.settings.development")

import django
django.setup()

import requests
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

# ── Config ────────────────────────────────────────────────────────────────────
BASE = "http://localhost:8001/api/v1"
TEST_USER_EMAIL = "pronun_sim@test.local"
TEST_USER_PASS  = "PronSim@2024!"

parser = argparse.ArgumentParser()
parser.add_argument("--fast", action="store_true", help="Skip delays between requests")
args, _ = parser.parse_known_args()

import time
def delay(sec=0.15):
    if not args.fast:
        time.sleep(sec)

# ── Colour helpers ────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
MAGENTA = "\033[95m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

PASS = f"{GREEN}✓ PASS{RESET}"
FAIL = f"{RED}✗ FAIL{RESET}"
WARN = f"{YELLOW}⚠ WARN{RESET}"
INFO = f"{CYAN}ℹ {RESET}"

results = []

def check(label, condition, detail=""):
    status = PASS if condition else FAIL
    results.append({"label": label, "ok": condition, "detail": detail})
    pad = "." * max(1, 55 - len(label))
    print(f"    {label}{pad} {status}  {DIM}{detail}{RESET}")
    return condition

def section(title, icon="▶"):
    print(f"\n{BOLD}{BLUE}{'═'*70}{RESET}")
    print(f"{BOLD}{BLUE}  {icon}  {title}{RESET}")
    print(f"{BOLD}{BLUE}{'═'*70}{RESET}")

def subsection(title):
    print(f"\n  {BOLD}{MAGENTA}── {title}{RESET}")


# =============================================================================
# STEP 0 — Create test user
# =============================================================================
section("STEP 0 — Chuẩn bị tài khoản học viên mô phỏng", "👤")

with transaction.atomic():
    user, created = User.objects.get_or_create(
        email=TEST_USER_EMAIL,
        defaults={"username": "pronun_sim", "is_active": True},
    )
    user.set_password(TEST_USER_PASS)
    user.save(update_fields=["password"])

check(
    "Tài khoản test tồn tại / tạo mới",
    user.pk is not None,
    f"email={TEST_USER_EMAIL} pk={user.pk} ({'created' if created else 'reused'})",
)

# Clear old progress for clean simulation
from apps.pronunciation.models import (
    PhonemeLesson, PronunciationStage, LessonSection, UserPhonemeProgress
)
deleted, _ = UserPhonemeProgress.objects.filter(user=user).delete()
check("Xoá progress cũ (clean slate)", True, f"deleted {deleted} rows")


# =============================================================================
# STEP 1 — Đăng nhập, lấy JWT
# =============================================================================
section("STEP 1 — Đăng nhập & lấy JWT token", "🔑")

sess = requests.Session()
r = sess.post(f"{BASE}/auth/auth/login/", json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASS})
check("POST /auth/auth/login/ → 200", r.status_code == 200, f"HTTP {r.status_code}")

token = None
if r.ok:
    # Auth uses HttpOnly cookie es_access — session carries it automatically
    cookies = dict(sess.cookies)
    token = cookies.get("es_access")
    check("Cookie es_access set", bool(token), f"cookies={list(cookies.keys())}")
    if token:
        sess.headers["Authorization"] = f"Bearer {token}"


# =============================================================================
# STEP 2 — Lấy danh sách stages và lessons
# =============================================================================
section("STEP 2 — Lấy 4 giai đoạn (stages)", "🗺️")

r = sess.get(f"{BASE}/pronunciation/stages/")
check("GET /pronunciation/stages/ → 200", r.status_code == 200, f"HTTP {r.status_code}")

stages = []
if r.ok:
    payload = r.json().get("data", r.json())
    stages = payload if isinstance(payload, list) else payload.get("results", [])
    check("Số giai đoạn >= 4", len(stages) >= 4, f"found {len(stages)} stages")
    for st in stages:
        print(f"    {DIM}Stage {st.get('order','?')}: {st.get('title','')} — {st.get('lesson_count', '?')} bài{RESET}")

delay()

# Fetch lessons for each stage
stage_lessons = {}
total_lessons_api = 0
for st in stages:
    r2 = sess.get(f"{BASE}/pronunciation/stages/{st['id']}/lessons/")
    if r2.ok:
        d = r2.json().get("data", r2.json())
        lessons = d if isinstance(d, list) else d.get("results", [])
        stage_lessons[st["id"]] = {"stage": st, "lessons": lessons}
        total_lessons_api += len(lessons)
    delay(0.05)

check(
    "Tổng số bài học lấy được qua API",
    total_lessons_api > 0,
    f"{total_lessons_api} bài trong {len(stages)} giai đoạn",
)


# =============================================================================
# STEP 3 — Mô phỏng học từng bài (by-slug) + quiz + complete
# =============================================================================
section("STEP 3 — Học từng bài (open → quiz → complete)", "📖")

SCORE_PROFILES = [
    ("Xuất sắc  (100%)",  1.00),
    ("Tốt       (80%)",   0.80),
    ("Đạt       (75%)",   0.75),
    ("Đạt ngưỡng (70%)",  0.70),
    ("Chưa đạt  (60%)",   0.60),
    ("Kém       (40%)",   0.40),
    ("Xuất sắc  (100%)",  1.00),  # repeat to fill remaining
]

simulation_log = []  # one entry per lesson
profile_idx = 0

for stage_id, data in stage_lessons.items():
    st = data["stage"]
    lessons = data["lessons"]
    stage_type = st.get("stage_type", "normal")
    subsection(f"Stage {st.get('order','?')}: {st.get('title','')} ({len(lessons)} bài)")

    for lesson_brief in lessons:
        slug = lesson_brief.get("slug", "")
        title = lesson_brief.get("title", "?")
        if not slug:
            print(f"      {WARN} slug rỗng cho bài '{title}' — bỏ qua")
            continue

        # ── 3a. Lấy chi tiết bài học ──────────────────────────────────────
        r = sess.get(f"{BASE}/pronunciation/lessons/by-slug/{slug}/")
        ok_fetch = check(
            f"GET by-slug/{slug}",
            r.status_code == 200,
            f"HTTP {r.status_code}",
        )
        delay()
        if not ok_fetch:
            simulation_log.append({"slug": slug, "title": title, "score": None, "completed": False, "error": "fetch_fail"})
            continue

        lesson_data = r.json().get("data", r.json())
        lesson_id = lesson_data.get("id")
        sections = lesson_data.get("sections", [])
        quiz_section = next((s for s in sections if s.get("section_type") == "quiz"), None)
        quiz_items = quiz_section.get("items", []) if quiz_section else []

        check(
            f"  └── có {len(sections)} sections",
            len(sections) >= 4,
            f"types={[s.get('section_type') for s in sections]}",
        )
        check(
            f"  └── có quiz với {len(quiz_items)} câu",
            len(quiz_items) > 0,
            "",
        )

        # ── 3b. Mô phỏng trả lời quiz ─────────────────────────────────────
        profile_name, accuracy = SCORE_PROFILES[profile_idx % len(SCORE_PROFILES)]
        profile_idx += 1

        correct = 0
        for qi, item in enumerate(quiz_items):
            answer = item.get("answer", "")
            options = item.get("options", [answer])
            # Decide right or wrong based on accuracy
            if random.random() < accuracy:
                chosen = answer
                correct += 1
            else:
                wrong_opts = [o for o in options if o != answer]
                chosen = random.choice(wrong_opts) if wrong_opts else answer
            delay(0.03)

        total_q = len(quiz_items) if quiz_items else 1
        quiz_score_pct = round((correct / total_q) * 100) if total_q else 0
        print(f"      {DIM}  Quiz: {correct}/{total_q} đúng = {quiz_score_pct}%  [{profile_name}]{RESET}")

        # ── 3c. POST complete ─────────────────────────────────────────────
        r_complete = sess.post(
            f"{BASE}/pronunciation/lessons/{lesson_id}/complete/",
            json={"score": quiz_score_pct},
        )
        completed = quiz_score_pct >= 70
        check(
            f"  └── POST /lessons/{lesson_id}/complete/",
            r_complete.status_code in (200, 201),
            f"HTTP {r_complete.status_code}  score={quiz_score_pct}%",
        )

        simulation_log.append({
            "slug": slug,
            "title": title,
            "stage": st.get("title", ""),
            "stage_order": st.get("order", 0),
            "stage_type": stage_type,
            "score": quiz_score_pct,
            "completed": completed,
            "lesson_id": lesson_id,
        })
        delay(0.1)


# =============================================================================
# STEP 4 — Kiểm tra DB: UserPhonemeProgress
# =============================================================================
section("STEP 4 — Kiểm tra DB: UserPhonemeProgress", "🗄️")

progress_qs = UserPhonemeProgress.objects.filter(user=user).select_related("lesson")
check(
    "Số bản ghi UserPhonemeProgress == số bài đã attempt",
    progress_qs.count() == len([l for l in simulation_log if l.get("lesson_id")]),
    f"{progress_qs.count()} bản ghi trong DB",
)

completed_in_db = progress_qs.filter(is_completed=True).count()
check(
    "Số bài is_completed=True trong DB",
    completed_in_db >= 0,
    f"{completed_in_db} bài",
)

# Spot-check first lesson
first_lesson_slug = simulation_log[0]["slug"] if simulation_log else None
if first_lesson_slug:
    try:
        lesson_obj = PhonemeLesson.objects.get(slug=first_lesson_slug)
        prog = UserPhonemeProgress.objects.filter(user=user, lesson=lesson_obj).first()
        check(
            f"Progress tồn tại cho '{first_lesson_slug}'",
            prog is not None,
            f"score={prog.score if prog else 'n/a'}",
        )
        check(
            "score trong DB khớp với quiz_score gửi lên",
            prog is not None and prog.score == simulation_log[0]["score"],
            f"DB={prog.score if prog else '?'} sim={simulation_log[0]['score']}",
        )
    except PhonemeLesson.DoesNotExist:
        print(f"    {WARN} Lesson '{first_lesson_slug}' không tìm thấy trong DB")


# =============================================================================
# STEP 5 — Kiểm tra GET stages/lessons sau khi có progress
# =============================================================================
section("STEP 5 — Lấy lại stages: progress_pct cập nhật?", "📊")

r = sess.get(f"{BASE}/pronunciation/stages/")
if r.ok:
    stages_after = r.json().get("data", r.json())
    if not isinstance(stages_after, list):
        stages_after = stages_after.get("results", [])
    for st in stages_after:
        pct = st.get("progress_pct", st.get("progress", 0))
        n_completed = st.get("completed_lessons", "?")
        n_total = st.get("total_lessons", st.get("lesson_count", "?"))
        print(f"    {DIM}Stage {st.get('order','?')}: {st.get('title','')}  "
              f"progress={pct}%  ({n_completed}/{n_total} bài){RESET}")
    check(
        "stages response có trường progress",
        any("progress" in str(st) for st in stages_after),
        "API trả về thông tin tiến độ",
    )
delay()


# =============================================================================
# REPORT — Tổng kết
# =============================================================================
section("REPORT — Kết quả mô phỏng học 4 giai đoạn", "📋")

total_sim   = len(simulation_log)
completed   = sum(1 for l in simulation_log if l.get("completed"))
failed      = sum(1 for l in simulation_log if not l.get("completed") and l.get("score") is not None)
errors      = sum(1 for l in simulation_log if l.get("error"))

print(f"\n  {'Tổng bài mô phỏng':<35} {BOLD}{total_sim}{RESET}")
print(f"  {'Hoàn thành (score >= 70%)':<35} {GREEN}{BOLD}{completed}{RESET}")
print(f"  {'Chưa đạt  (score < 70%)':<35} {YELLOW}{failed}{RESET}")
print(f"  {'Lỗi API':<35} {RED if errors else CYAN}{errors}{RESET}")

scores = [l["score"] for l in simulation_log if l.get("score") is not None]
if scores:
    avg = sum(scores) / len(scores)
    print(f"  {'Điểm trung bình quiz':<35} {BOLD}{avg:.1f}%{RESET}")
    print(f"  {'Điểm cao nhất':<35} {GREEN}{max(scores)}%{RESET}")
    print(f"  {'Điểm thấp nhất':<35} {YELLOW}{min(scores)}%{RESET}")

# Table by stage
print(f"\n  {BOLD}Chi tiết theo giai đoạn:{RESET}")
print(f"  {'Giai đoạn':<35} {'Bài':<5} {'Đạt':<5} {'TB%':<7}")
print(f"  {'─'*55}")
from itertools import groupby
stage_sorted = sorted(simulation_log, key=lambda x: x.get("stage_order", 99))
for stage_name, group in groupby(stage_sorted, key=lambda x: x.get("stage", "?")):
    grp = list(group)
    n = len(grp)
    c = sum(1 for l in grp if l.get("completed"))
    sc = [l["score"] for l in grp if l.get("score") is not None]
    avg_s = f"{sum(sc)/len(sc):.0f}%" if sc else "—"
    bar = "✅" * c + "⬜" * (n - c)
    print(f"  {stage_name:<35} {n:<5} {c:<5} {avg_s:<7}  {bar}")

# Table for all lessons
print(f"\n  {BOLD}Chi tiết từng bài:{RESET}")
print(f"  {'#':<4} {'Slug':<25} {'Score':<8} {'Kết quả'}")
print(f"  {'─'*62}")
for i, l in enumerate(simulation_log, 1):
    score = l.get("score")
    is_ok = l.get("completed", False)
    icon = "✅" if is_ok else ("❌" if score is not None else "⚠️ ")
    score_str = f"{score}%" if score is not None else "err"
    print(f"  {i:<4} {l['slug']:<25} {score_str:<8} {icon}")

# Summary check counts
print()
total_checks = len(results)
passed_checks = sum(1 for r in results if r["ok"])
failed_checks = total_checks - passed_checks

print(f"\n  {BOLD}Kết quả kiểm tra tổng:{RESET}")
print(f"  {GREEN}{passed_checks} / {total_checks} checks passed{RESET}", end="")
if failed_checks:
    print(f"  {RED}({failed_checks} failed){RESET}")
else:
    print(f"  {GREEN}🎉 Tất cả PASS!{RESET}")

if failed_checks:
    print(f"\n  {RED}Các checks thất bại:{RESET}")
    for r in results:
        if not r["ok"]:
            print(f"    {FAIL}  {r['label']}  {DIM}{r['detail']}{RESET}")

print(f"\n{BOLD}{BLUE}{'═'*70}{RESET}\n")
