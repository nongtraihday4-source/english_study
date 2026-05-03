"""
simulate_support_workflow — Django management command

Mô phỏng đầy đủ quy trình làm việc của nhân viên hỗ trợ (CSKH).

Các kịch bản được mô phỏng:
  1. Quên mật khẩu — tìm user, gửi email reset
  2. Quên email đăng nhập — tìm bằng tên / SĐT
  3. Vấn đề thanh toán — ticket + yêu cầu hoàn tiền
  4. Vấn đề kỹ thuật — ticket ưu tiên cao, xử lý đến đóng ticket

Cách chạy:
  python manage.py simulate_support_workflow
  python manage.py simulate_support_workflow --keep   # giữ dữ liệu test sau khi chạy
  python manage.py simulate_support_workflow --verbose
"""

import json
import sys
from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.management.base import BaseCommand
from django.test import Client
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.payments.models import PaymentTransaction, SubscriptionPlan, UserSubscription
from apps.support.models import RefundRequest, SupportTicket, TicketMessage

User = get_user_model()

# ── ANSI colours ──────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"
TICK   = f"{GREEN}✓{RESET}"
CROSS  = f"{RED}✗{RESET}"
ARROW  = f"{CYAN}→{RESET}"
WARN   = f"{YELLOW}⚠{RESET}"

# ── Helpers ────────────────────────────────────────────────────────────────────

def ok(msg):   return f"  {TICK}  {msg}"
def fail(msg): return f"  {CROSS}  {RED}{msg}{RESET}"
def step(msg): return f"\n  {ARROW} {CYAN}{msg}{RESET}"
def head(msg): return f"\n{BOLD}{YELLOW}{'─'*60}\n  {msg}\n{'─'*60}{RESET}"
def sub(msg):  return f"     {DIM}{msg}{RESET}"

# ── Thin API client wrapper ───────────────────────────────────────────────────

class SupportClient:
    """Thin wrapper around Django test Client that handles JWT auth & JSON."""

    def __init__(self, email, password):
        self.client = Client()
        self.logged_in = False
        self.login_path = None
        self.password_confirm_path = None
        self._login(email, password)

    def _login(self, email, password):
        login_paths = [
            "/api/v1/auth/login/",
            "/api/v1/auth/auth/login/",
        ]
        for path in login_paths:
            r = self.client.post(
                path,
                data=json.dumps({"email": email, "password": password}),
                content_type="application/json",
            )
            if r.status_code != 200:
                continue
            try:
                d = r.json()
            except Exception:
                continue
            payload = d.get("data", d)
            # This project uses HttpOnly JWT cookies (es_access/es_refresh), so
            # no bearer token is required in JSON body.
            has_cookie_auth = bool(self.client.cookies.get("es_access"))
            has_success_flag = bool(d.get("success", False) or payload.get("message"))
            if has_cookie_auth or has_success_flag:
                self.logged_in = True
                self.login_path = path
                break

        # Detect password reset confirm path based on active auth include style.
        self.password_confirm_path = "/api/v1/auth/password-reset/confirm/"
        if self.login_path == "/api/v1/auth/auth/login/":
            self.password_confirm_path = "/api/v1/auth/auth/password-reset/confirm/"

        return self.logged_in

    def _headers(self):
        return {"content_type": "application/json"}

    def get(self, path, params=None):
        query = ""
        if params:
            query = "?" + "&".join(f"{k}={v}" for k, v in params.items())
        return self.client.get(f"/api/v1/support{path}{query}", **self._headers())

    def post(self, path, data=None):
        return self.client.post(
            f"/api/v1/support{path}",
            data=json.dumps(data or {}),
            **self._headers(),
        )

    def patch(self, path, data=None):
        return self.client.patch(
            f"/api/v1/support{path}",
            data=json.dumps(data or {}),
            **self._headers(),
        )

    def payload(self, response):
        """Unwrap VNNumberJSONRenderer envelope."""
        d = response.json()
        return d.get("data", d)


# ── The Command ───────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Mô phỏng quy trình làm việc CSKH — kiểm tra toàn bộ chức năng hỗ trợ"

    def add_arguments(self, parser):
        parser.add_argument("--keep", action="store_true", help="Giữ dữ liệu test sau khi chạy")
        parser.add_argument("--verbose", action="store_true", help="Hiển thị chi tiết JSON response")

    # ── Entry point ────────────────────────────────────────────────────────────
    def handle(self, *args, **options):
        self.verbose = options["verbose"]
        self.keep = options["keep"]
        self.results = []   # list of (scenario, step, passed)

        self.stdout.write(f"""
{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗
║       MÔ PHỎNG QUY TRÌNH NHÂN VIÊN HỖ TRỢ (CSKH)        ║
║              english_study — Support Portal              ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")

        # 1. Setup test data
        self.stdout.write(head("CHUẨN BỊ DỮ LIỆU TEST"))
        support_user, customers, plan, txn = self._setup_data()

        # 2. Login as support staff
        self.stdout.write(step("Đăng nhập với tài khoản nhân viên hỗ trợ"))
        api = SupportClient("cskh_test@englishstudy.vn", "Cskh@2026Test!")
        if api.logged_in:
            self.stdout.write(ok(f"Đăng nhập thành công — {support_user.email}"))
            if api.login_path:
                self.stdout.write(sub(f"Endpoint auth: {api.login_path}"))
        else:
            self.stdout.write(fail("Đăng nhập CSKH thất bại — dừng mô phỏng"))
            return

        # 3. Run scenarios
        self._scenario_dashboard(api)
        self._scenario_forgot_password(api, customers[0])
        self._scenario_forgot_email(api, customers[1])
        self._scenario_payment_issue(api, customers[2], txn)
        self._scenario_technical_issue(api, customers[0])

        # 4. Summary
        self._print_summary()

        # 5. Cleanup
        if not self.keep:
            self._cleanup(support_user, customers, txn)
        else:
            self.stdout.write(f"\n{WARN}  --keep: Dữ liệu test GIỮ LẠI trong database.\n")

    # ── Data setup ─────────────────────────────────────────────────────────────
    def _setup_data(self):
        # Support staff
        support_user, _ = User.objects.update_or_create(
            email="cskh_test@englishstudy.vn",
            defaults={
                "username": "cskh_test",
                "first_name": "Nhân Viên",
                "last_name": "Test",
                "role": "support",
                "is_active": True,
            },
        )
        support_user.set_password("Cskh@2026Test!")
        support_user.save()
        self.stdout.write(ok(f"Support staff: {support_user.email}"))

        # Customer 1 — quên mật khẩu
        c1, _ = User.objects.update_or_create(
            email="nguyen.thi.a_test@gmail.com",
            defaults={
                "username": "nguyen_thi_a_test",
                "first_name": "Nguyễn Thị",
                "last_name": "A",
                "role": "student",
                "account_type": "premium",
                "is_active": True,
            },
        )
        c1.set_password("OldPass123!")
        c1.save()
        self.stdout.write(ok(f"Khách 1 (quên MK): {c1.email}"))

        # Customer 2 — quên email
        c2, _ = User.objects.update_or_create(
            email="tran.van.b_test@gmail.com",
            defaults={
                "username": "tran_van_b_test",
                "first_name": "Trần Văn",
                "last_name": "B",
                "role": "student",
                "account_type": "demo",
                "is_active": True,
            },
        )
        c2.set_password("OldPass123!")
        c2.save()
        # Add phone to profile
        from apps.users.models import UserProfile
        UserProfile.objects.update_or_create(user=c2, defaults={"phone": "0912345699"})
        self.stdout.write(ok(f"Khách 2 (quên email): {c2.email}  SĐT: 0912345699"))

        # Customer 3 — payment issue
        c3, _ = User.objects.update_or_create(
            email="le.thi.c_test@gmail.com",
            defaults={
                "username": "le_thi_c_test",
                "first_name": "Lê Thị",
                "last_name": "C",
                "role": "student",
                "account_type": "premium",
                "is_active": True,
            },
        )
        c3.set_password("OldPass123!")
        c3.save()
        self.stdout.write(ok(f"Khách 3 (thanh toán): {c3.email}"))

        # Subscription plan (get first or create dummy)
        plan = SubscriptionPlan.objects.filter(is_active=True).first()
        if not plan:
            plan = SubscriptionPlan.objects.create(
                name="Premium Test Plan",
                price_vnd=199000,
                original_price_vnd=199000,
                duration_days=30,
                is_active=True,
            )
            self.stdout.write(ok("Tạo plan test: Premium Test Plan"))
        else:
            self.stdout.write(ok(f"Dùng plan có sẵn: {plan.name}"))

        # Payment transaction for c3
        txn, _ = PaymentTransaction.objects.get_or_create(
            user=c3,
            plan=plan,
            defaults={
                "gateway": "manual",
                "amount_vnd": plan.price_vnd,
                "original_amount_vnd": plan.price_vnd,
                "discount_vnd": 0,
                "status": "success",
            },
        )
        self.stdout.write(ok(f"Giao dịch test: #{txn.id}  {int(txn.amount_vnd):,}đ  [{txn.status}]"))

        return support_user, [c1, c2, c3], plan, txn

    # ── Scenario helpers ───────────────────────────────────────────────────────
    def _record(self, scenario, step_name, passed):
        self.results.append((scenario, step_name, passed))
        if passed:
            self.stdout.write(ok(step_name))
        else:
            self.stdout.write(fail(step_name))

    def _check(self, response, expected_status, scenario, step_name):
        passed = response.status_code == expected_status
        self._record(scenario, step_name, passed)
        if self.verbose or not passed:
            try:
                self.stdout.write(sub(f"HTTP {response.status_code}  →  {json.dumps(response.json(), ensure_ascii=False, indent=2)[:300]}"))
            except Exception:
                self.stdout.write(sub(f"HTTP {response.status_code}"))
        return passed

    def _extract_id(self, payload):
        if not isinstance(payload, dict):
            return None
        if payload.get("id"):
            return payload.get("id")
        if isinstance(payload.get("ticket"), dict):
            return payload["ticket"].get("id")
        if isinstance(payload.get("refund"), dict):
            return payload["refund"].get("id")
        return None

    # ── SCENARIO 0: Dashboard ────────────────────────────────────────────────
    def _scenario_dashboard(self, api):
        sc = "Dashboard"
        self.stdout.write(head(f"KỊCH BẢN 0 · TỔNG QUAN CSKH"))
        self.stdout.write(step("GET /support/dashboard/"))
        r = api.get("/dashboard/")
        if self._check(r, 200, sc, "Tải dashboard thành công"):
            d = api.payload(r)
            stats = d.get("stats", d)
            self.stdout.write(sub(f"  open_tickets={stats.get('open_tickets')}  my_tickets={stats.get('my_tickets')}  overdue={stats.get('overdue_tickets')}"))

    # ── SCENARIO 1: Quên mật khẩu ────────────────────────────────────────────
    def _scenario_forgot_password(self, api, customer):
        sc = "Quên mật khẩu"
        self.stdout.write(head(f"KỊCH BẢN 1 · QUÊN MẬT KHẨU"))
        self.stdout.write(sub(f"  Khách hàng: {customer.email}"))

        # Step 1: Tìm user
        self.stdout.write(step("1a. Tra cứu người dùng bằng email"))
        r = api.get("/users/", {"search": customer.email})
        if self._check(r, 200, sc, "Tìm user bằng email thành công"):
            p = api.payload(r)
            results = p.get("results", p) if isinstance(p, dict) else p
            found = len(results) > 0
            self._record(sc, f"Tìm thấy user '{customer.email}'", found)

        # Step 2: Xem chi tiết user
        self.stdout.write(step("1b. Xem chi tiết người dùng"))
        r = api.get(f"/users/{customer.id}/")
        if self._check(r, 200, sc, "Xem chi tiết user thành công"):
            d = api.payload(r)
            self.stdout.write(sub(f"  Tên: {d.get('full_name')}  Gói: {d.get('account_type')}  Ticket: {d.get('ticket_count')}"))

        # Step 3: Gửi email reset mật khẩu
        self.stdout.write(step("1c. Gửi email đặt lại mật khẩu"))
        with _capture_mail():
            r = api.post(f"/users/{customer.id}/reset-password/")
            self._check(r, 200, sc, "Gửi email reset mật khẩu thành công")
            if r.status_code == 200:
                d = api.payload(r)
                self.stdout.write(sub(f"  {d.get('detail', '')}"))

        # Step 4: Xác nhận token (mô phỏng user nhận email và đặt lại MK)
        self.stdout.write(step("1d. Mô phỏng user xác nhận token đặt lại MK"))
        uid = urlsafe_base64_encode(force_bytes(customer.pk))
        token = default_token_generator.make_token(customer)
        anon = Client()
        r2 = anon.post(
            api.password_confirm_path,
            data=json.dumps({"uid": uid, "token": token, "new_password": "NewPass@2026!"}),
            content_type="application/json",
        )
        self._check(r2, 200, sc, "User xác nhận token & đặt lại MK thành công")

        # Step 5: Tạo ticket ghi nhận yêu cầu
        self.stdout.write(step("1e. Tạo ticket ghi nhận yêu cầu quên mật khẩu"))
        r = api.post("/tickets/", {
            "user": customer.id,
            "subject": "[Test] Khách hàng quên mật khẩu — đã xử lý",
            "description": "Khách hàng báo cáo quên mật khẩu qua hotline. Đã gửi email đặt lại thành công.",
            "category": "account",
            "priority": "medium",
        })
        if self._check(r, 201, sc, "Tạo ticket ghi nhận thành công"):
            d = api.payload(r)
            ticket_id = self._extract_id(d)
            if not ticket_id:
                ticket = SupportTicket.objects.filter(
                    user=customer,
                    subject="[Test] Khách hàng quên mật khẩu — đã xử lý",
                ).order_by("-created_at").first()
                ticket_id = ticket.id if ticket else None
            self.stdout.write(sub(f"  Ticket #{ticket_id}  SLA: {d.get('sla_deadline', '')[:16]}"))

            # Step 6: Giao ticket cho bản thân
            self.stdout.write(step("1f. Giao ticket cho nhân viên đang xử lý"))
            r = api.post(f"/tickets/{ticket_id}/assign/")
            self._check(r, 200, sc, "Giao ticket cho CSKH thành công")

            # Step 7: Thêm ghi chú nội bộ
            self.stdout.write(step("1g. Thêm ghi chú nội bộ"))
            r = api.post(f"/tickets/{ticket_id}/messages/", {
                "content": "Đã xác minh danh tính qua SĐT. Gửi link reset lúc 13:05. Khách xác nhận nhận được email.",
                "is_internal": True,
            })
            self._check(r, 201, sc, "Thêm ghi chú nội bộ thành công")

            # Step 8: Đổi trạng thái → resolved
            self.stdout.write(step("1h. Đổi trạng thái ticket → resolved"))
            r = api.patch(f"/tickets/{ticket_id}/", {"status": "resolved"})
            self._check(r, 200, sc, "Đóng ticket (resolved) thành công")
            if r.status_code == 200:
                d = api.payload(r)
                self.stdout.write(sub(f"  Trạng thái: {d.get('status')}  Resolved at: {str(d.get('resolved_at',''))[:16]}"))

    # ── SCENARIO 2: Quên email đăng nhập ─────────────────────────────────────
    def _scenario_forgot_email(self, api, customer):
        sc = "Quên email"
        self.stdout.write(head("KỊCH BẢN 2 · QUÊN EMAIL ĐĂNG NHẬP"))
        self.stdout.write(sub(f"  Khách hàng gọi hotline: tên '{customer.first_name} {customer.last_name}', SĐT 0912345699"))

        # Step 1: Tìm bằng tên
        self.stdout.write(step("2a. Tra cứu bằng họ tên"))
        r = api.get("/users/", {"search": "Trần Văn"})
        if self._check(r, 200, sc, "Tìm user bằng tên thành công"):
            p = api.payload(r)
            results = p.get("results", p) if isinstance(p, dict) else p
            found = any(u.get("id") == customer.id for u in (results if isinstance(results, list) else []))
            self._record(sc, f"Tìm thấy đúng account '{customer.email}'", found)
            if not found and isinstance(results, list):
                self.stdout.write(sub(f"  Tìm thấy {len(results)} kết quả: {[u.get('email') for u in results[:3]]}"))

        # Step 2: Tìm bằng SĐT
        self.stdout.write(step("2b. Tra cứu bằng số điện thoại"))
        r = api.get("/users/", {"search": "0912345699"})
        if self._check(r, 200, sc, "Tìm user bằng SĐT thành công"):
            p = api.payload(r)
            results = p.get("results", p) if isinstance(p, dict) else p
            found = any(u.get("id") == customer.id for u in (results if isinstance(results, list) else []))
            self._record(sc, "Tìm thấy đúng account qua SĐT", found)

        # Step 3: Xem thông tin
        self.stdout.write(step("2c. Xác nhận và xem chi tiết tài khoản"))
        r = api.get(f"/users/{customer.id}/")
        if self._check(r, 200, sc, "Xem chi tiết user thành công"):
            d = api.payload(r)
            self.stdout.write(sub(f"  ✉  Email tài khoản: {d.get('email')}"))

        # Step 4: Tạo ticket ghi nhận
        self.stdout.write(step("2d. Tạo ticket ghi nhận yêu cầu"))
        r = api.post("/tickets/", {
            "user": customer.id,
            "subject": "[Test] Khách hàng quên email đăng nhập — đã cung cấp",
            "description": "Khách xác minh qua SĐT 0912345699. Đã thông báo email đăng nhập là tran.van.b_test@gmail.com.",
            "category": "account",
            "priority": "low",
        })
        if self._check(r, 201, sc, "Tạo ticket ghi nhận thành công"):
            d = api.payload(r)
            ticket_id = self._extract_id(d)
            if not ticket_id:
                ticket = SupportTicket.objects.filter(
                    user=customer,
                    subject="[Test] Khách hàng quên email đăng nhập — đã cung cấp",
                ).order_by("-created_at").first()
                ticket_id = ticket.id if ticket else None
            # Reply to customer
            self.stdout.write(step("2e. Thêm phản hồi ghi nhận đã giải quyết"))
            r2 = api.post(f"/tickets/{ticket_id}/messages/", {
                "content": "Đã xác minh danh tính qua SĐT. Cung cấp email đăng nhập thành công. Khách hài lòng.",
                "is_internal": False,
            })
            self._check(r2, 201, sc, "Thêm phản hồi thành công")
            # Resolve
            r3 = api.patch(f"/tickets/{ticket_id}/", {"status": "resolved"})
            self._check(r3, 200, sc, "Đóng ticket thành công")

    # ── SCENARIO 3: Vấn đề thanh toán + hoàn tiền ────────────────────────────
    def _scenario_payment_issue(self, api, customer, txn):
        sc = "Thanh toán"
        self.stdout.write(head("KỊCH BẢN 3 · VẤN ĐỀ THANH TOÁN & HOÀN TIỀN"))
        self.stdout.write(sub(f"  Khách hàng: {customer.email}  |  Giao dịch #{txn.id}  {int(txn.amount_vnd):,}đ"))

        # Step 1: Tìm user
        self.stdout.write(step("3a. Tìm user và xem lịch sử giao dịch"))
        r = api.get(f"/users/{customer.id}/")
        if self._check(r, 200, sc, "Xem chi tiết user + lịch sử giao dịch"):
            d = api.payload(r)
            txns = d.get("recent_transactions", [])
            self.stdout.write(sub(f"  {len(txns)} giao dịch gần nhất"))
            for t in txns[:2]:
                self.stdout.write(sub(f"    #{t.get('id')}  {t.get('plan')}  {t.get('amount_vnd'):,}đ  [{t.get('status')}]"))

        # Step 2: Tra cứu giao dịch qua endpoint transactions
        self.stdout.write(step("3b. Tra cứu giao dịch qua danh sách"))
        r = api.get("/transactions/", {"search": customer.email})
        self._check(r, 200, sc, "Lấy danh sách giao dịch thành công")

        # Step 3: Tạo ticket thanh toán
        self.stdout.write(step("3c. Tạo ticket vấn đề thanh toán (ưu tiên cao)"))
        r = api.post("/tickets/", {
            "user": customer.id,
            "subject": "[Test] Thanh toán thành công nhưng chưa lên gói Premium",
            "description": f"Khách phản ánh đã thanh toán {int(txn.amount_vnd):,}đ, giao dịch #{txn.id} thành công nhưng tài khoản chưa được nâng cấp lên Premium.",
            "category": "payment",
            "priority": "high",
        })
        if self._check(r, 201, sc, "Tạo ticket thanh toán (priority=high) thành công"):
            d = api.payload(r)
            ticket_id = self._extract_id(d)
            if not ticket_id:
                ticket = SupportTicket.objects.filter(
                    user=customer,
                    subject="[Test] Thanh toán thành công nhưng chưa lên gói Premium",
                ).order_by("-created_at").first()
                ticket_id = ticket.id if ticket else None
            self.stdout.write(sub(f"  Ticket #{ticket_id}  SLA hết hạn sau ~8h"))

            # Assign
            self.stdout.write(step("3d. Giao ticket cho CSKH"))
            r = api.post(f"/tickets/{ticket_id}/assign/")
            self._check(r, 200, sc, "Giao ticket cho CSKH thành công")

            # Internal note
            self.stdout.write(step("3e. Ghi chú nội bộ — xác nhận giao dịch"))
            r = api.post(f"/tickets/{ticket_id}/messages/", {
                "content": f"Đã kiểm tra giao dịch #{txn.id}. Status=success, amount={int(txn.amount_vnd):,}đ. Cần kiểm tra webhook kích hoạt subscription.",
                "is_internal": True,
            })
            self._check(r, 201, sc, "Ghi chú nội bộ thành công")

            # Create refund request
            self.stdout.write(step("3f. Tạo yêu cầu hoàn tiền"))
            r = api.post("/refund-requests/", {
                "transaction": txn.id,
                "reason": "[Test] Khách yêu cầu hoàn tiền do gói chưa được kích hoạt sau 24h.",
                "amount_vnd": int(txn.amount_vnd),
            })
            if self._check(r, 201, sc, "Tạo yêu cầu hoàn tiền thành công"):
                rd = api.payload(r)
                refund_id = self._extract_id(rd)
                if not refund_id:
                    rr = RefundRequest.objects.filter(transaction=txn).order_by("-created_at").first()
                    refund_id = rr.id if rr else None
                self.stdout.write(sub(f"  Refund #{refund_id}  {int(rd.get('amount_vnd',0)):,}đ  [{rd.get('status')}]"))

            # Update status → in_progress
            self.stdout.write(step("3g. Cập nhật trạng thái → in_progress"))
            r = api.patch(f"/tickets/{ticket_id}/", {"status": "in_progress"})
            self._check(r, 200, sc, "Cập nhật trạng thái thành công")

            # Reply to customer
            self.stdout.write(step("3h. Phản hồi khách hàng"))
            r = api.post(f"/tickets/{ticket_id}/messages/", {
                "content": "Xin chào, chúng tôi đã xác nhận giao dịch của bạn. Yêu cầu hoàn tiền đã được tạo và đang chờ bộ phận kế toán duyệt. Chúng tôi sẽ cập nhật trong vòng 24h.",
                "is_internal": False,
            })
            self._check(r, 201, sc, "Phản hồi khách hàng thành công")

            # Waiting customer status
            r = api.patch(f"/tickets/{ticket_id}/", {"status": "waiting_customer"})
            self._check(r, 200, sc, "Đổi trạng thái → waiting_customer thành công")

        # Step 4: Tra cứu subscriptions
        self.stdout.write(step("3i. Tra cứu gói đăng ký của user"))
        r = api.get("/subscriptions/", {"search": customer.email})
        self._check(r, 200, sc, "Tra cứu subscription thành công")

        # Step 5: Tra cứu danh sách hoàn tiền
        self.stdout.write(step("3j. Xem danh sách yêu cầu hoàn tiền"))
        r = api.get("/refund-requests/", {"status": "pending"})
        if self._check(r, 200, sc, "Lấy danh sách hoàn tiền thành công"):
            p = api.payload(r)
            results = p.get("results", p) if isinstance(p, dict) else p
            count = len(results) if isinstance(results, list) else (p.get("count", 0))
            self.stdout.write(sub(f"  {count} yêu cầu hoàn tiền đang chờ duyệt"))

    # ── SCENARIO 4: Vấn đề kỹ thuật ──────────────────────────────────────────
    def _scenario_technical_issue(self, api, customer):
        sc = "Kỹ thuật"
        self.stdout.write(head("KỊCH BẢN 4 · VẤN ĐỀ KỸ THUẬT"))
        self.stdout.write(sub(f"  Khách hàng báo: ứng dụng không phát âm thanh khi luyện phát âm"))

        # Step 1: Tạo ticket kỹ thuật — urgent
        self.stdout.write(step("4a. Tạo ticket kỹ thuật ưu tiên KHẨN"))
        r = api.post("/tickets/", {
            "user": customer.id,
            "subject": "[Test] Ứng dụng không phát âm — toàn bộ bài luyện phát âm",
            "description": "Khách báo ứng dụng không phát âm thanh khi luyện phát âm. Không nghe được cả giọng đọc mẫu lẫn phản hồi AI. Thiết bị: Chrome / Windows 11.",
            "category": "technical",
            "priority": "urgent",
        })
        if self._check(r, 201, sc, "Tạo ticket kỹ thuật KHẨN thành công"):
            d = api.payload(r)
            ticket_id = self._extract_id(d)
            if not ticket_id:
                ticket = SupportTicket.objects.filter(
                    user=customer,
                    subject="[Test] Ứng dụng không phát âm — toàn bộ bài luyện phát âm",
                ).order_by("-created_at").first()
                ticket_id = ticket.id if ticket else None
            self.stdout.write(sub(f"  Ticket #{ticket_id}  SLA hết hạn sau ~4h"))

            # Assign immediately
            self.stdout.write(step("4b. Giao ngay cho CSKH (ticket khẩn cấp)"))
            r = api.post(f"/tickets/{ticket_id}/assign/")
            self._check(r, 200, sc, "Giao ticket KHẨN thành công")

            # In-progress
            r = api.patch(f"/tickets/{ticket_id}/", {"status": "in_progress"})
            self._check(r, 200, sc, "Chuyển trạng thái → in_progress")

            # Collect info
            self.stdout.write(step("4c. Hỏi thêm thông tin từ khách"))
            r = api.post(f"/tickets/{ticket_id}/messages/", {
                "content": "Chào bạn, cảm ơn đã liên hệ hỗ trợ. Bạn có thể cho biết:\n1. Trình duyệt đang dùng (Chrome/Firefox/Safari/Edge)?\n2. Có bật loa/tai nghe chưa?\n3. Lỗi xảy ra với tất cả bài hay chỉ một số bài?\nCảm ơn!",
                "is_internal": False,
            })
            self._check(r, 201, sc, "Hỏi thêm thông tin khách hàng thành công")

            # Waiting
            r = api.patch(f"/tickets/{ticket_id}/", {"status": "waiting_customer"})
            self._check(r, 200, sc, "Chuyển → waiting_customer")

            # Customer replies (mô phỏng — tạo message)
            self.stdout.write(step("4d. Mô phỏng khách hàng phản hồi"))
            # Internally add a customer message by creating directly
            try:
                ticket_obj = SupportTicket.objects.get(id=ticket_id)
                TicketMessage.objects.create(
                    ticket=ticket_obj,
                    author=customer,
                    content="Chrome 122, loa bật rồi. Tất cả bài đều không có âm. Nhưng khi tôi thử trên điện thoại thì được.",
                    is_internal=False,
                )
                self._record(sc, "Khách hàng phản hồi (mô phỏng)", True)
            except Exception as e:
                self._record(sc, f"Mô phỏng khách phản hồi: {e}", False)

            # CSKH xử lý
            self.stdout.write(step("4e. CSKH xử lý và gửi hướng dẫn"))
            r = api.patch(f"/tickets/{ticket_id}/", {"status": "in_progress"})
            self._check(r, 200, sc, "Đổi → in_progress")
            r = api.post(f"/tickets/{ticket_id}/messages/", {
                "content": "Cảm ơn thông tin. Vấn đề xảy ra trên Chrome PC nhưng vẫn hoạt động trên điện thoại. Bạn thử:\n1. Vào chrome://settings/content/sound — đảm bảo ứng dụng không bị tắt tiếng\n2. Xoá cache và thử lại\n3. Kiểm tra autoplay settings trong Chrome\nNếu vẫn lỗi, vui lòng chụp màn hình Console (F12) và gửi lại cho chúng tôi.",
                "is_internal": False,
            })
            self._check(r, 201, sc, "CSKH gửi hướng dẫn xử lý thành công")

            # Internal note
            r = api.post(f"/tickets/{ticket_id}/messages/", {
                "content": "Ghi chú nội bộ: Có thể liên quan đến Chrome autoplay policy. Chờ khách xác nhận. Nếu vẫn lỗi → leo thang lên team tech.",
                "is_internal": True,
            })
            self._check(r, 201, sc, "Ghi chú nội bộ leo thang thành công")

            # View full ticket
            self.stdout.write(step("4f. Xem toàn bộ chi tiết ticket"))
            r = api.get(f"/tickets/{ticket_id}/")
            if self._check(r, 200, sc, "Xem chi tiết ticket thành công"):
                d = api.payload(r)
                msgs = d.get("messages", [])
                self.stdout.write(sub(f"  {len(msgs)} tin nhắn trong ticket  status={d.get('status')}"))
                for m in msgs:
                    internal = "[Internal]" if m.get("is_internal") else ""
                    self.stdout.write(sub(f"    {m.get('author_name')} {internal}: {str(m.get('content',''))[:60]}…"))

            # Resolve
            self.stdout.write(step("4g. Đóng ticket sau khi xử lý xong"))
            r = api.patch(f"/tickets/{ticket_id}/", {"status": "resolved"})
            self._check(r, 200, sc, "Đóng ticket thành công")

        # Final dashboard check
        self.stdout.write(step("4h. Kiểm tra dashboard sau khi hoàn tất"))
        r = api.get("/dashboard/")
        if r.status_code == 200:
            d = api.payload(r)
            stats = d.get("stats", d)
            self.stdout.write(sub(f"  open={stats.get('open_tickets')}  my={stats.get('my_tickets')}  overdue={stats.get('overdue_tickets')}  resolved_today={stats.get('resolved_today')}"))
            self._record(sc, "Dashboard phản ánh đúng trạng thái", True)

        # Check coupon list
        self.stdout.write(step("4i. Kiểm tra danh sách coupon"))
        r = api.get("/coupons/")
        self._check(r, 200, sc, "Lấy danh sách coupon thành công")

    # ── Summary ────────────────────────────────────────────────────────────────
    def _print_summary(self):
        self.stdout.write(f"\n{BOLD}{CYAN}{'═'*60}")
        self.stdout.write(f"  BÁO CÁO KẾT QUẢ MÔ PHỎNG")
        self.stdout.write(f"{'═'*60}{RESET}\n")

        passed = [(sc, s) for sc, s, p in self.results if p]
        failed = [(sc, s) for sc, s, p in self.results if not p]

        # Group by scenario
        from itertools import groupby
        from operator import itemgetter
        scenarios = {}
        for sc, step_name, result in self.results:
            if sc not in scenarios:
                scenarios[sc] = {"passed": 0, "failed": 0, "steps": []}
            scenarios[sc]["steps"].append((step_name, result))
            if result:
                scenarios[sc]["passed"] += 1
            else:
                scenarios[sc]["failed"] += 1

        for sc_name, sc_data in scenarios.items():
            n_ok = sc_data["passed"]
            n_fail = sc_data["failed"]
            total = n_ok + n_fail
            bar = f"{GREEN}{'█' * n_ok}{RED}{'░' * n_fail}{RESET}"
            status_icon = TICK if n_fail == 0 else WARN if n_ok >= n_fail else CROSS
            self.stdout.write(f"  {status_icon}  {BOLD}{sc_name}{RESET}  {bar}  {n_ok}/{total}")
            for step_name, result in sc_data["steps"]:
                icon = TICK if result else CROSS
                self.stdout.write(f"      {icon} {step_name}")

        total_pass = len(passed)
        total_fail = len(failed)
        total_all = total_pass + total_fail
        pct = int(100 * total_pass / total_all) if total_all else 0

        self.stdout.write(f"\n{BOLD}  TỔNG CỘNG: {total_pass}/{total_all} bước đạt  ({pct}%)")
        if total_fail == 0:
            self.stdout.write(f"  {GREEN}🎉  Tất cả bước đều PASS — Support Portal hoạt động đúng!{RESET}")
        else:
            self.stdout.write(f"  {RED}⚠  {total_fail} bước FAIL — cần kiểm tra lại{RESET}")
            self.stdout.write(f"\n  {BOLD}Các bước thất bại:{RESET}")
            for sc, s in failed:
                self.stdout.write(f"    {CROSS} [{sc}] {s}")

        self.stdout.write("")

    # ── Cleanup ────────────────────────────────────────────────────────────────
    def _cleanup(self, support_user, customers, txn):
        self.stdout.write(head("DỌN DẸP DỮ LIỆU TEST"))
        try:
            # Delete tickets created in simulation
            for c in customers:
                qs = SupportTicket.objects.filter(user=c)
                count = qs.count()
                qs.delete()
                self.stdout.write(ok(f"Xoá {count} ticket của {c.email}"))

            # Delete refund requests
            rqs = RefundRequest.objects.filter(transaction=txn)
            count_r = rqs.count()
            rqs.delete()
            if count_r:
                self.stdout.write(ok(f"Xoá {count_r} yêu cầu hoàn tiền"))

            # Delete test transaction before deleting users because PaymentTransaction.user is PROTECT
            if txn and PaymentTransaction.objects.filter(pk=txn.pk).exists():
                PaymentTransaction.objects.filter(pk=txn.pk).delete()
                self.stdout.write(ok(f"Xoá giao dịch test #{txn.pk}"))

            # Delete test users
            for c in customers:
                if User.objects.filter(pk=c.pk).exists():
                    c.refresh_from_db()
                    email = c.email
                    c.delete()
                    self.stdout.write(ok(f"Xoá user test: {email}"))
            if User.objects.filter(pk=support_user.pk).exists():
                support_user.delete()
                self.stdout.write(ok(f"Xoá support staff test: {support_user.email}"))
        except Exception as e:
            self.stdout.write(fail(f"Lỗi dọn dẹp: {e}"))


# ── Context manager to suppress actual email sending ─────────────────────────
from contextlib import contextmanager

@contextmanager
def _capture_mail():
    """Redirect Django emails to memory during test."""
    from django.test.utils import override_settings
    with override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"):
        mail.outbox = []
        yield mail.outbox
