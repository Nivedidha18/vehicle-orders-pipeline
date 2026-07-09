from __future__ import annotations
from pathlib import Path
import pytest
from src.pipeline import model

duckdb = pytest.importorskip("duckdb")

SQL = (Path(__file__).resolve().parents[1] / "src" / "pipeline" / "questions.sql").read_text()

@pytest.fixture
def con(raw_vehicles, raw_orders):
    dim, _ = model.build_dim_vehicle(raw_vehicles)
    fct, _ = model.build_fct_orders(raw_orders, dim)
    c = duckdb.connect()
    c.register("dim_df", dim)
    c.register("fct_df", fct)
    c.execute("CREATE TABLE dim_vehicle AS SELECT * FROM dim_df")
    c.execute("CREATE TABLE fct_orders AS SELECT * FROM fct_df")
    c.execute(SQL)
    yield c
    c.close()


def test_q1_sales_by_market_month(con):
    df = con.execute(
        "SELECT * FROM mart_sales_by_market_month "
        "ORDER BY market, order_month"
    ).df()
    got = {(r.market, r.order_month): r.completed_sales_gbp for r in df.itertuples()}
    assert got[("France", "2024-03")] == 38250.00
    assert got[("Germany", "2024-01")] == 25500.00
    assert got[("United Kingdom", "2024-02")] == 20000.00
    assert ("Germany", "2024-01") in got and len(df) == 4


def test_q2_top_models(con):
    df = con.execute("SELECT * FROM mart_top_models").df()
    top = df.iloc[0]
    assert (top["make"], top["model"], top["units_sold"]) == ("BMW", "I4", 2)
    assert "99" not in df["model"].astype(str).tolist()


def test_q3_lead_time(con):
    df = con.execute("SELECT * FROM mart_lead_time_by_market").df()
    d = {r.market: r.avg_days_order_to_delivery for r in df.itertuples()}
    assert d["Germany"] == 15.0
    assert d["France"] == 10.0


def test_q4_channel_share(con):
    df = con.execute("SELECT * FROM mart_channel_share").df()
    share = {r.channel: r.pct_of_orders for r in df.itertuples()}
    assert share["Online"] == 50.0
    assert round(share["Dealer"], 2) == 33.33
    assert round(sum(share.values()), 0) == 100
