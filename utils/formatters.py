"""
utils/formatters.py
Shared formatting helpers used across analytics and dashboard layers.
"""


def fmt_currency(value: float, prefix: str = "$") -> str:
    """Format a float as a dollar string: $1,234.56"""
    return f"{prefix}{value:,.2f}"


def fmt_number(value: int) -> str:
    """Format an integer with thousands separator."""
    return f"{value:,}"


def fmt_pct(value: float, decimals: int = 1) -> str:
    """Format a float as a percentage string."""
    return f"{value:.{decimals}f}%"


def fmt_delta(current: float, previous: float) -> str:
    """Return a signed percentage string for MoM or YoY delta."""
    if previous == 0:
        return "N/A"
    delta = (current - previous) / previous * 100
    sign = "▲" if delta >= 0 else "▼"
    return f"{sign} {abs(delta):.1f}%"
