# Admin Panel — Lộ trình triển khai đầy đủ

> Quy mô: 1000–10000 người dùng | 2–5 nhân viên vận hành

---

## Hiện trạng

> Cập nhật: **28/03/2026** — Tất cả module đã triển khai xong.

| Module | Trạng thái | Ghi chú |
|--------|-----------|---------|
| Dashboard (KPI 6 chỉ số) | ✅ Hoạt động | Bug fix isoformat + try/except |
| Người dùng (search, ban, edit role) | ✅ Hoạt động | — |
| Nội dung (CRUD Khoá học / Chương / Bài) | ✅ Hoạt động | — |
| Thanh toán / Mã giảm giá | ✅ Hoàn thành | Plans, Coupons, Transactions, Subscriptions |
| Bài thi / Ngân hàng câu hỏi | ✅ Hoàn thành | ExamSets + Exercise browser |
| Giám sát AI Grading | ✅ Hoàn thành | Stats, Job queue, Retry, Submissions |
| Gamification (Badges, XP, Certificates) | ✅ Hoàn thành | Achievements CRUD, XP grant, Certificates |
| Thông báo (Templates + Bulk Send) | ✅ Hoàn thành | Templates, Broadcast, History |
| Phân quyền nhân viên (Staff RBAC) | ✅ Hoàn thành | Backend done; tab tích hợp vào Users |
| Nhật ký hoạt động (Audit Log) | ✅ Hoàn thành | Filter by action/model/admin |
| Cài đặt hệ thống (System Settings) | ✅ Hoàn thành | 18 settings seeded, inline edit |

---

## Phase 0 — Sửa lỗi (Ngay)

- [x] Fix Dashboard API bug (try/except + better error logging)
- [x] Thêm `apps.admin_portal` vào `INSTALLED_APPS`
- [x] Fix timezone-aware sort trong activity feed

**Chạy sau Phase 0:**
```bash
python manage.py makemigrations admin_portal
python manage.py migrate
python manage.py create_default_settings  # (management command tạo sẵn)
```

---

## Phase 1 — Nghiệp vụ cốt lõi (Cao nhất)

### 1A. Quản lý Thanh toán & Mã giảm giá
**Route:** `/admin/payments`

| Tab | Chức năng |
|-----|-----------|
| Gói thuê bao | CRUD SubscriptionPlan (name, price, features, is_active) |
| Mã giảm giá | CRUD Coupon (code, type, value, max_uses, valid_from/until) |
| Giao dịch | Xem PaymentTransaction (read-only, filter by status/gateway/date) |
| Thuê bao | Xem UserSubscription (filter by status, gia hạn thủ công) |

**Backend endpoints mới:**
```
GET/POST    /admin-portal/plans/
GET/PATCH/DEL /admin-portal/plans/<pk>/
GET/POST    /admin-portal/coupons/
GET/PATCH/DEL /admin-portal/coupons/<pk>/
GET         /admin-portal/transactions/          (filter: status, gateway, user, date)
GET         /admin-portal/subscriptions/         (filter: status, plan)
POST        /admin-portal/subscriptions/<pk>/extend/   (gia hạn N ngày)
```

### 1B. Bài thi & Ngân hàng câu hỏi
**Route:** `/admin/assessments`

| Tab | Chức năng |
|-----|-----------|
| Bài thi | CRUD ExamSet (title, type, skill, level, time, passing_score) |
| Bài tập | Xem 4 loại exercise (Listening/Speaking/Reading/Writing) theo cấp độ |

**Backend endpoints mới:**
```
GET/POST    /admin-portal/exam-sets/
GET/PATCH/DEL /admin-portal/exam-sets/<pk>/
GET         /admin-portal/exercises/?type=listening&level=B1
```

### 1C. Giám sát AI Grading
**Route:** `/admin/grading`

| Section | Chức năng |
|---------|-----------|
| KPI     | Pending / Processing / Completed / Failed job counts, avg grading time, tokens used |
| Job Queue | DataTable AIGradingJob (filter by type/status/date) |
| Retry | POST retry failed jobs (single hoặc bulk retry all failed) |
| Submissions | Xem chi tiết Speaking/Writing submission + AI output |

**Backend endpoints mới:**
```
GET  /admin-portal/grading/stats/
GET  /admin-portal/grading/jobs/        (filter: type, status, date)
POST /admin-portal/grading/jobs/<pk>/retry/
GET  /admin-portal/grading/submissions/speaking/
GET  /admin-portal/grading/submissions/speaking/<pk>/
GET  /admin-portal/grading/submissions/writing/
GET  /admin-portal/grading/submissions/writing/<pk>/
```

---

## Phase 2 — Quản trị nội dung mở rộng

### 2A. Gamification
**Route:** `/admin/gamification`

| Section | Chức năng |
|---------|-----------|
| Huy hiệu | CRUD Achievement (name, category, condition, threshold, xp_reward, is_active) |
| Chứng chỉ | Xem Certificate list + verify code |
| Leaderboard | Xem LeaderboardSnapshot (weekly/monthly) |
| XP Log | Xem XPLog (filter by user/source/date), cấp XP thủ công |

**Backend endpoints mới:**
```
GET/POST    /admin-portal/achievements/
GET/PATCH   /admin-portal/achievements/<pk>/
GET         /admin-portal/certificates/
GET         /admin-portal/xp-log/
POST        /admin-portal/xp-log/grant/     (cấp XP thủ công)
GET         /admin-portal/leaderboard/
```

### 2B. Thông báo
**Route:** `/admin/notifications`

| Section | Chức năng |
|---------|-----------|
| Templates | CRUD NotificationTemplate (edit title/message/push_enabled) |
| Gửi hàng loạt | Chọn loại/đối tượng → POST broadcast |
| Lịch sử | Xem Notification list (filter by type/user/date) |

**Backend endpoints mới:**
```
GET/PATCH   /admin-portal/notification-templates/
GET         /admin-portal/notification-templates/<type>/
POST        /admin-portal/notifications/broadcast/
GET         /admin-portal/notifications/history/   (filter: type, user, date)
```

---

## Phase 3 — Phân quyền & Kiểm soát hệ thống

### 3A. Phân quyền nhân viên (Staff RBAC)
**Route:** Tích hợp vào `/admin/users` (tab "Nhân viên")

**Model mới:** `StaffPermission` (trong `apps/admin_portal/models.py`)
```
manage_users, manage_content, manage_payments,
manage_assessments, manage_notifications,
manage_gamification, view_analytics,
manage_settings, view_audit_log
```

**Permission decorator mới:** `HasStaffPermission('manage_payments')`

**Backend endpoints mới:**
```
GET/PATCH /admin-portal/staff/<pk>/permissions/
```

### 3B. Nhật ký hoạt động (Audit Log)
**Route:** `/admin/audit-log`

**Model mới:** `AuditLog` (trong `apps/admin_portal/models.py`)
```
admin_user (FK), action, model_name, object_id,
description, changes_json, ip_address, created_at
```

- Auto-log qua `AuditLogMixin` (mixin cho APIView)
- DataTable filter by admin/action/model/daterange
- Export CSV

**Backend endpoints mới:**
```
GET /admin-portal/audit-log/    (filter: admin, action, date)
```

### 3C. Cài đặt hệ thống (System Settings)
**Route:** `/admin/settings`

**Model mới:** `SystemSetting` (trong `apps/admin_portal/models.py`)
```
key (unique), value, value_type (str/int/bool/json),
category (general/payment/ai_grading/email/security),
is_editable, description, updated_at, updated_by
```

**Default settings được seed khi migrate:**
```
maintenance_mode = false
ai_grading_enabled = true
ai_max_retry_count = 3
speaking_cost_per_job_vnd = 500
welcome_email_enabled = true
leaderboard_reset_day = monday
max_login_attempts = 5
```

**Backend endpoints mới:**
```
GET         /admin-portal/settings/
PATCH       /admin-portal/settings/<key>/
POST        /admin-portal/settings/seed/   (idempotent seed defaults)
```

---

## Cấu trúc sidebar sau nâng cấp

```
🛡️ Admin Panel
├── 📊 Tổng quan         /admin
├── 👥 Người dùng        /admin/users
├── 📚 Nội dung          /admin/content
├── 💳 Thanh toán        /admin/payments    ← MỚI
├── 📝 Bài thi           /admin/assessments ← MỚI
├── 🤖 AI Grading        /admin/grading     ← MỚI
├── 🏆 Gamification      /admin/gamification← MỚI
├── 🔔 Thông báo         /admin/notifications← MỚI
├── 📋 Nhật ký           /admin/audit-log   ← MỚI
├── ⚙️  Cài đặt           /admin/settings    ← MỚI
└── 🏠 Trang chủ         /dashboard
```

---

## Files cần tạo/sửa

### Backend
| File | Thao tác |
|------|----------|
| `apps/admin_portal/models.py` | TẠO MỚI — AuditLog, SystemSetting, StaffPermission |
| `apps/admin_portal/serializers.py` | MỞ RỘNG |
| `apps/admin_portal/views.py` | MỞ RỘNG |
| `apps/admin_portal/urls.py` | MỞ RỘNG |
| `english_study/settings/base.py` | Thêm `apps.admin_portal` |

**Sau khi sửa models:**
```bash
cd backend
python manage.py makemigrations admin_portal
python manage.py migrate
```

### Frontend
| File | Thao tác |
|------|----------|
| `src/api/admin.js` | MỞ RỘNG (~40 methods) |
| `src/views/admin/AdminLayout.vue` | CẬP NHẬT sidebar |
| `src/views/admin/AdminDashboardView.vue` | FIX bug |
| `src/views/admin/AdminPaymentsView.vue` | TẠO MỚI |
| `src/views/admin/AdminAssessmentsView.vue` | TẠO MỚI |
| `src/views/admin/AdminGradingView.vue` | TẠO MỚI |
| `src/views/admin/AdminGamificationView.vue` | TẠO MỚI |
| `src/views/admin/AdminNotificationsView.vue` | TẠO MỚI |
| `src/views/admin/AdminSettingsView.vue` | TẠO MỚI |
| `src/views/admin/AdminAuditLogView.vue` | TẠO MỚI |
| `src/router/index.js` | CẬP NHẬT routes |

---

## Tiến độ triển khai

- [x] Phase 0 — Bug fixes (dashboard, INSTALLED_APPS) 
- [x] Phase 1A — Payments & Coupons (backend + frontend)
- [x] Phase 1B — Assessments (backend + frontend)
- [x] Phase 1C — AI Grading Monitor (backend + frontend)
- [x] Phase 2A — Gamification (backend + frontend)
- [x] Phase 2B — Notifications (backend + frontend)
- [x] Phase 3A — Staff RBAC (backend + frontend backend endpoint)
- [x] Phase 3B — Audit Log (backend + frontend)
- [x] Phase 3C — System Settings (backend + frontend)
- [x] Phase 4A — Staff RBAC tab in AdminUsersView (phân quyền từng nhân viên)
- [x] Phase 4B — Export CSV cho Audit Log
- [x] Phase 4C — AuditLogMixin tự động ghi log (decorator)
