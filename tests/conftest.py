"""Shared fixtures: tiny, deliberately-messy synthetic frames whose correct
answers are known by hand, so mart numbers can be asserted exactly."""
from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def raw_vehicles() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "vehicle_id": ["1", "2", "3", "3", "x"],          # dup id + bad id
            "make": ["VW", "bmw", "Mercedes", "Mercedes", "Kia"],
            "model": ["Golf", "I4", "A-Class", "A-Class", "Niro"],
            "segment": ["c", "d", "c", "c", "b"],
            "fuel_type": ["petrol", "EV", "Diesel", "Diesel", "hybrid"],
            "list_price_gbp": ["25000", "50000", "-1", "-1", "30000"],
        }
    )


@pytest.fixture
def raw_orders() -> pd.DataFrame:
    # 8 source rows -> after cleaning: 6 orders (1 exact dup, 1 bad id dropped)
    return pd.DataFrame(
        {
            "order_id":       ["100", "101", "102", "103", "104", "104", "105", "bad"],
            "vehicle_id":     ["1",   "2",   "1",   "3",   "2",   "2",   "99",  "1"],
            "market":         ["DE",  "uk",  "Germany", "FR", "de", "de", "uk", "de"],
            "currency":       ["EUR", "£",   "eur",  "EUR", "EUR", "EUR", "GBP", "EUR"],
            "channel":        ["online", "Dealer", "web", "phone", "online", "online", "dealership", "online"],
            "order_date":     ["2024-01-05", "05/02/2024", "2024-01-20", "10/03/2024", "2024-02-15", "2024-02-15", "01/01/2024", "2024-01-01"],
            "delivery_date":  ["2024-01-20", "01/01/2024", "", "20/03/2024", "2024-03-01", "2024-03-01", "10/01/2024", ""],
            "order_status":   ["Completed", "completed", "cancelled", "Delivered", "completed", "completed", "pending", "completed"],
            "sale_amount":    ["€30.000,00", "20000", "35,000", "45000", "31,500.50", "31,500.50", "18000", "10000"],
            "customer_email": ["a@x.com", "B@X.COM", "bad-email", "c@y.io", "d@z.com", "d@z.com", "e@z.com", "f@z.com"],
        }
    )
