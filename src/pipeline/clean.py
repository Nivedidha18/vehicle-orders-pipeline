from __future__ import annotations
import re
from datetime import datetime
import numpy as np
import pandas as pd
from . import config

# Normalise whitespace.
_WS = re.compile(r"\s+")


def norm_text(value) -> str | None:
    """Trim text and convert empty values to None."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    s = _WS.sub(" ", str(value)).strip()
    if s == "" or s.lower() in {"na", "n/a", "nan", "null", "none", "-"}:
        return None
    return s


def _canon(value, aliases: dict[str, str], *, title_default: bool = True):
    s = norm_text(value)
    if s is None:
        return None, True
    key = s.lower()
    if key in aliases:
        return aliases[key], True
    return (s.title() if title_default else s), False


def clean_market(value):
    return _canon(value, config.MARKET_ALIASES)

def clean_channel(value):
    return _canon(value, config.CHANNEL_ALIASES)

def clean_fuel(value):
    return _canon(value, config.FUEL_ALIASES)

def clean_make(value):
    return _canon(value, config.MAKE_ALIASES)

def clean_status(value):
    s = norm_text(value)
    if s is None:
        return None, True
    key = s.lower()
    if key in config.STATUS_ALIASES:
        return config.STATUS_ALIASES[key], True
    return "pending", False


def clean_currency(value):
    s = norm_text(value)
    if s is None:
        return None, True
    low = s.lower()
    for symbol, code in config.CURRENCY_SYMBOLS.items():
        if symbol in low:
            s = code
            break
    code = s.upper()
    return code, code in config.FX_RATES_TO_GBP


_NUM_KEEP = re.compile(r"[^0-9,.\-]")

def parse_amount(value) -> float | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = _NUM_KEEP.sub("", str(value)).strip()
    if s in {"", "-", ".", ","}:
        return None
    has_dot = "." in s
    has_comma = "," in s
    # Use the rightmost separator as the decimal point
    if has_dot and has_comma:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif has_comma:
        if s.count(",") > 1 or len(s.split(",")[-1]) == 3:
            s = s.replace(",", "")
        else:
            s = s.replace(",", ".")
    elif has_dot:
        if s.count(".") > 1 or len(s.split(".")[-1]) == 3:
            s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


_ISO_RE = re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$")
_DASH_RE = re.compile(r"^\d{1,2}-\d{1,2}-\d{4}$")
_SLASH_RE = re.compile(r"^\d{1,2}[/.]\d{1,2}[/.]\d{4}$")

def _try(s: str, fmt: str) -> pd.Timestamp | None:
    try:
        return pd.Timestamp(datetime.strptime(s, fmt))
    except ValueError:
        return None


def parse_date(value) -> pd.Timestamp | None:
    s = norm_text(value)
    if s is None:
        return None
    if _ISO_RE.match(s):
        return _try(s, "%Y-%m-%d")
    # Most dash dates in the source are MM-DD-YYYY.
    if _DASH_RE.match(s):
        return _try(s, "%m-%d-%Y") or _try(s, "%d-%m-%Y")
    # Most slash dates are DD/MM/YYYY.
    if _SLASH_RE.match(s):
        s = s.replace(".", "/")
        return _try(s, "%d/%m/%Y") or _try(s, "%m/%d/%Y")
    for fmt in ("%d %b %Y", "%d %B %Y"):
        ts = _try(s, fmt)
        if ts is not None:
            return ts
    ts = pd.to_datetime(s, dayfirst=True, errors="coerce")
    return None if pd.isna(ts) else ts
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean_email(value):
    s = norm_text(value)
    if s is None:
        return None, False
    s = s.lower()
    return s, bool(_EMAIL.match(s))

def apply_pair(series: pd.Series, fn):
    out = series.map(fn)
    values = out.map(lambda x: x[0])
    flags = out.map(lambda x: x[1])
    return values, flags