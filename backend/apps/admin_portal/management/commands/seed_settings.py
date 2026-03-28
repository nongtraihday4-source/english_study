"""Management command: seed default SystemSetting values (idempotent)."""
from django.core.management.base import BaseCommand
from apps.admin_portal.models import SystemSetting

DEFAULTS = [
    # General
    ("maintenance_mode", "false", "bool", "general", "Bật/tắt chế độ bảo trì", True),
    ("site_name", "English Study", "str", "general", "Tên hiển thị của trang web", True),
    # AI Grading
    ("ai_grading_enabled", "true", "bool", "ai_grading", "Bật/tắt tính năng chấm bài AI", True),
    ("ai_max_retry_count", "3", "int", "ai_grading", "Số lần thử lại tối đa khi AI lỗi", True),
    ("speaking_cost_per_job_vnd", "500", "int", "ai_grading", "Chi phí ước tính (VNĐ) mỗi bài nói AI", True),
    ("writing_cost_per_job_vnd", "800", "int", "ai_grading", "Chi phí ước tính (VNĐ) mỗi bài viết AI", True),
    # Payment
    ("free_trial_days", "7", "int", "payment", "Số ngày dùng thử miễn phí khi đăng ký", True),
    ("invoice_prefix", "ES", "str", "payment", "Tiền tố mã giao dịch", True),
    # Email
    ("welcome_email_enabled", "true", "bool", "email", "Gửi email chào mừng khi đăng ký", True),
    ("grading_done_email_enabled", "true", "bool", "email", "Email thông báo khi chấm bài xong", True),
    # Security
    ("max_login_attempts", "5", "int", "security", "Số lần đăng nhập sai tối đa trước khi tạm khoá", True),
    ("session_timeout_hours", "24", "int", "security", "Thời gian hết hạn phiên đăng nhập (giờ)", True),
    ("require_2fa_admin", "false", "bool", "security", "Bắt buộc 2FA cho tài khoản Admin", True),
    # Gamification
    ("leaderboard_reset_day", "monday", "str", "gamification", "Ngày reset bảng xếp hạng tuần", True),
    ("xp_exercise_complete", "10", "int", "gamification", "XP khi hoàn thành 1 bài tập", True),
    ("xp_perfect_score", "25", "int", "gamification", "XP khi đạt 100 điểm", True),
    ("xp_streak_7_days", "50", "int", "gamification", "XP khi streak 7 ngày", True),
    ("xp_chapter_complete", "100", "int", "gamification", "XP khi hoàn thành 1 chương", True),
]


class Command(BaseCommand):
    help = "Seed default SystemSetting values (idempotent — skip if key exists)"

    def handle(self, *args, **options):
        created = 0
        for key, value, vtype, category, desc, editable in DEFAULTS:
            _, was_created = SystemSetting.objects.get_or_create(
                key=key,
                defaults={
                    "value": value,
                    "value_type": vtype,
                    "category": category,
                    "description": desc,
                    "is_editable": editable,
                },
            )
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created {created} new settings, skipped {len(DEFAULTS) - created} existing."
            )
        )
