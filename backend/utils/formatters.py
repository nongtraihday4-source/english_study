"""
VN Number Formatting Utilities
Định dạng số kiểu Việt Nam: 1.234.567 (dấu chấm ngàn, dấu phẩy thập phân)
"""


def fmt_vn(number) -> str:
    """
    Format số nguyên / thập phân theo chuẩn vi-VN.
    Ví dụ: 1234567 → '1.234.567' | 199000.5 → '199.000,5'
    """
    if number is None:
        return "0"
    try:
        if isinstance(number, float):
            # Separate integer and decimal parts
            int_part = int(number)
            dec_part = f"{number:.2f}".split(".")[1].rstrip("0")
            formatted_int = f"{int_part:,}".replace(",", ".")
            return f"{formatted_int},{dec_part}" if dec_part else formatted_int
        return f"{int(number):,}".replace(",", ".")
    except (ValueError, TypeError):
        return str(number)


def fmt_vnd(amount) -> str:
    """Format VND currency: 199000 → '199.000 ₫'"""
    return f"{fmt_vn(amount)} ₫"


def fmt_percent(value, decimals: int = 2) -> str:
    """Format percentage: 75.5 → '75,50%'"""
    if value is None:
        return "0%"
    try:
        formatted = f"{float(value):.{decimals}f}".replace(".", ",")
        return f"{formatted}%"
    except (ValueError, TypeError):
        return "0%"


def fmt_score(score, total: int = 100) -> str:
    """Format score: 85 out of 100 → '85/100'"""
    return f"{score}/{total}"
