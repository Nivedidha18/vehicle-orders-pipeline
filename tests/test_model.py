"""Tests for the silver/gold builders and the quality decisions they encode."""
from __future__ import annotations

import pandas as pd

from src.pipeline import model


def _rep(report, check):
    for r in report:
        if r["check"] == check:
            return r["n"]
    return 0


def test_dim_vehicle_dedup_and_clean(raw_vehicles):
    dim, rep = model.build_dim_vehicle(raw_vehicles)
    # bad id "x" dropped, dup id 3 collapsed -> ids {1,2,3}
    assert sorted(dim["vehicle_id"].tolist()) == [1, 2, 3]
    assert dim["vehicle_id"].is_unique
    assert _rep(rep, "vehicle.duplicate_vehicle_id") == 1
    row = dim.set_index("vehicle_id").loc[1]
    assert row["make"] == "Volkswagen" and row["fuel_type"] == "Petrol"
    # negative list price nulled
    assert pd.isna(dim.set_index("vehicle_id").loc[3, "list_price_gbp"])


def test_fct_grain_and_dedup(raw_vehicles, raw_orders):
    dim, _ = model.build_dim_vehicle(raw_vehicles)
    fct, rep = model.build_fct_orders(raw_orders, dim)
    # 8 raw -> drop bad id -> drop exact dup -> 6 orders, one row each
    assert len(fct) == 6
    assert fct["order_id"].is_unique
    assert _rep(rep, "order.exact_duplicate_rows") == 1
    assert _rep(rep, "order.order_id_unparseable") == 1


def test_fx_conversion_and_bad_delivery(raw_vehicles, raw_orders):
    dim, _ = model.build_dim_vehicle(raw_vehicles)
    fct, rep = model.build_fct_orders(raw_orders, dim)
    f = fct.set_index("order_id")

    # €30.000,00 at 0.85 -> 25500 GBP
    assert f.loc[100, "sale_amount_gbp"] == 25500.00
    # GBP order unchanged
    assert f.loc[101, "sale_amount_gbp"] == 20000.00
    # delivery before order -> nulled, no lead time
    assert pd.isna(f.loc[101, "delivery_date"])
    assert pd.isna(f.loc[101, "days_to_delivery"])
    assert _rep(rep, "order.delivery_before_order") == 1


def test_orphan_and_completed_flags(raw_vehicles, raw_orders):
    dim, _ = model.build_dim_vehicle(raw_vehicles)
    fct, rep = model.build_fct_orders(raw_orders, dim)
    f = fct.set_index("order_id")
    assert f.loc[105, "vehicle_known"] is False or f.loc[105, "vehicle_known"] == False
    assert _rep(rep, "order.orphan_vehicle_id") == 1
    # 'Delivered' counts as completed; 'cancelled'/'pending' do not
    assert f.loc[103, "is_completed"] == True
    assert f.loc[102, "is_completed"] == False
    assert f.loc[105, "is_completed"] == False
    # lead time computed correctly (2024 is a leap year: Feb15 -> Mar1 = 15)
    assert f.loc[104, "days_to_delivery"] == 15
    assert f.loc[100, "days_to_delivery"] == 15
