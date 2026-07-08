"""Unit tests for the pure cleaning functions."""
from __future__ import annotations

import pandas as pd
import pytest

from src.pipeline import clean


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("30000", 30000.0),
        ("€30.000,00", 30000.0),        # EU thousands + decimal comma
        ("31,500.50", 31500.50),        # UK thousands + decimal dot
        ("EUR 30.169", 30169.0),        # EU dot = thousands (3 digits)
        ("24380.00", 24380.0),          # dot = decimal (2 digits)
        ("£27,345", 27345.0),           # comma = thousands
        ("35,5", 35.5),                 # lone comma, decimal
        ("1.234.567", 1234567.0),       # multiple dot thousands
        ("1,234,567", 1234567.0),       # multiple comma thousands
        ("-1", -1.0),                   # sentinel; excluded later as non-positive
        ("", None),
        ("n/a", None),
        (None, None),
    ],
)
def test_parse_amount(raw, expected):
    assert clean.parse_amount(raw) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("2025-03-29", pd.Timestamp("2025-03-29")),   # ISO
        ("04-30-2025", pd.Timestamp("2025-04-30")),   # dash = US MM-DD-YYYY
        ("10-03-2024", pd.Timestamp("2024-10-03")),   # dash = US -> October 3
        ("29/04/2025", pd.Timestamp("2025-04-29")),   # slash = EU DD/MM
        ("07.06.2024", pd.Timestamp("2024-06-07")),   # dot = EU day-first
        ("16 Aug 2025", pd.Timestamp("2025-08-16")),  # text
        ("", None),
        ("garbage", None),
    ],
)
def test_parse_date(raw, expected):
    assert clean.parse_date(raw) == expected


@pytest.mark.parametrize(
    "raw,value,matched",
    [("DE", "Germany", True), ("uk", "United Kingdom", True),
     ("Narnia", "Narnia", False), ("", None, True)],
)
def test_clean_market(raw, value, matched):
    assert clean.clean_market(raw) == (value, matched)


@pytest.mark.parametrize(
    "raw,value,ok",
    [("£", "GBP", True), ("eur", "EUR", True), ("€", "EUR", True),
     ("XYZ", "XYZ", False)],
)
def test_clean_currency(raw, value, ok):
    assert clean.clean_currency(raw) == (value, ok)


@pytest.mark.parametrize(
    "raw,expected",
    [("Completed", "completed"), ("DELIVERED", "completed"),
     ("canceled", "cancelled"), ("weird-status", "pending")],
)
def test_clean_status(raw, expected):
    assert clean.clean_status(raw)[0] == expected


@pytest.mark.parametrize(
    "raw,value,ok",
    [("A@X.com", "a@x.com", True), (" bad-email ", "bad-email", False),
     ("", None, False)],
)
def test_clean_email(raw, value, ok):
    assert clean.clean_email(raw) == (value, ok)
