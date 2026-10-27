"""Постоянные значения программы."""

ALLOWED_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
ALLOWED_KEYS = ["timestamp", "level", "source", "message"]
CRYTICAL_LEVELS = ["ERROR", "CRITICAL"]
POSITION_TOP = 5
DEFAULT_TOP_N = 5
