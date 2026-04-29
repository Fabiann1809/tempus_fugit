import datetime

DAYS_ES = ("Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom")
MONTHS_ES = (
    "Ene", "Feb", "Mar", "Abr", "May", "Jun",
    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
)


def format_hms(dt: datetime.datetime) -> str:
    return dt.strftime("%H:%M:%S")


def format_date_es(dt: datetime.datetime) -> str:
    dow = DAYS_ES[dt.weekday()].upper()
    mon = MONTHS_ES[dt.month - 1].upper()
    return f"{dow} {dt.day:02d} {mon}"


def format_year(dt: datetime.datetime) -> str:
    return str(dt.year)


def format_stopwatch(centiseconds: int) -> str:
    cs = centiseconds % 100
    total_seconds = centiseconds // 100
    secs = total_seconds % 60
    mins = total_seconds // 60
    return f"{mins:02d}:{secs:02d}.{cs:02d}"


def format_countdown(total_seconds: int) -> str:
    mins = total_seconds // 60
    secs = total_seconds % 60
    return f"{mins:02d}:{secs:02d}"
