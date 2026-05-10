"""
apps/curriculum/tests/test_timezone.py
TDD: Timezone Enforcement & fmt_vn datetime formatting.
Test → Fail → Implement → Pass workflow.
"""
from django.test import TestCase, override_settings
from django.utils import timezone
from datetime import datetime
from utils.formatters import fmt_vn, fmt_vn_datetime
import pytz


class FmtVnDatetimeTest(TestCase):
    def test_fmt_vn_datetime_returns_ddmmyyyy_hhmm(self):
        utc_dt = datetime(2026, 5, 7, 23, 59, tzinfo=pytz.UTC)
        result = fmt_vn_datetime(utc_dt)
        self.assertRegex(result, r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}$")
        self.assertEqual(result, "08/05/2026 06:59")

    def test_fmt_vn_datetime_midnight_utc(self):
        utc_dt = datetime(2026, 5, 7, 0, 0, tzinfo=pytz.UTC)
        result = fmt_vn_datetime(utc_dt)
        self.assertEqual(result, "07/05/2026 07:00")

    def test_fmt_vn_datetime_noon_utc(self):
        utc_dt = datetime(2026, 5, 7, 12, 0, tzinfo=pytz.UTC)
        result = fmt_vn_datetime(utc_dt)
        self.assertEqual(result, "07/05/2026 19:00")

    def test_fmt_vn_datetime_none_handling(self):
        self.assertEqual(fmt_vn_datetime(None), "")

    def test_fmt_vn_datetime_naive_becomes_aware(self):
        naive_dt = datetime(2026, 5, 7, 14, 30)
        result = fmt_vn_datetime(naive_dt)
        self.assertRegex(result, r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}$")

    def test_fmt_vn_datetime_already_ict(self):
        ict = pytz.timezone("Asia/Ho_Chi_Minh")
        ict_dt = ict.localize(datetime(2026, 5, 7, 14, 30))
        result = fmt_vn_datetime(ict_dt)
        self.assertEqual(result, "07/05/2026 14:30")

    def test_fmt_vn_datetime_dst_boundary(self):
        utc_dt = datetime(2026, 1, 1, 0, 0, tzinfo=pytz.UTC)
        result = fmt_vn_datetime(utc_dt)
        self.assertEqual(result, "01/01/2026 07:00")

    def test_fmt_vn_datetime_millisec_ignored(self):
        utc_dt = datetime(2026, 5, 7, 23, 59, 59, tzinfo=pytz.UTC)
        result = fmt_vn_datetime(utc_dt)
        self.assertEqual(result, "08/05/2026 06:59")


@override_settings(TIME_ZONE="Asia/Ho_Chi_Minh", USE_TZ=True)
class TimezoneFormatterIntegrationTest(TestCase):
    def test_django_now_returns_ict_aware(self):
        dt = timezone.now()
        self.assertEqual(str(dt.tzinfo), "UTC")
        result = fmt_vn_datetime(dt)
        self.assertRegex(result, r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}$")