from __future__ import annotations
import pandas as pd
from . import clean, config

def _report(rows: list[dict], check: str, n: int, detail: str = "") -> None:
    if n:
        rows.append(
            {
                "check": check,
                "n": int(n),
                "detail": detail,
            }
        )

def build_dim_vehicle(
    raw: pd.DataFrame,
) -> tuple[pd.DataFrame, list[dict]]:
    report: list[dict] = []
    df = raw.copy()

    df["vehicle_id"] = (
        pd.to_numeric(df["vehicle_id"], errors="coerce")
        .astype("Int64")
    )

    _report(
        report,
        "vehicle.vehicle_id_unparseable",
        df["vehicle_id"].isna().sum(),
        "dropped",
    )

    df = df.dropna(subset=["vehicle_id"])

    duplicate_ids = df["vehicle_id"].duplicated(keep="first").sum()

    _report(
        report,
        "vehicle.duplicate_vehicle_id",
        duplicate_ids,
        "kept first occurrence",
    )

    df = df.drop_duplicates(
        subset=["vehicle_id"],
        keep="first",
    )

    df["make"], _ = clean.apply_pair(
        df["make"],
        clean.clean_make,
    )

    # Don't title-case model codes like XC40 or Mach-E
    df["model"] = df["model"].map(clean.norm_text)

    df["segment"] = (
        df["segment"]
        .map(clean.norm_text)
        .map(lambda x: x.upper() if isinstance(x, str) else x)
    )

    fuel_type, fuel_ok = clean.apply_pair(
        df["fuel_type"],
        clean.clean_fuel,
    )

    df["fuel_type"] = fuel_type

    _report(
        report,
        "vehicle.unmapped_fuel_type",
        (~fuel_ok).sum(),
        "kept as provided",
    )

    price = df["list_price_gbp"].map(clean.parse_amount)

    invalid_price = price.notna() & (price <= 0)

    _report(
        report,
        "vehicle.nonpositive_list_price",
        invalid_price.sum(),
        "nulled",
    )

    df["list_price_gbp"] = price.mask(invalid_price)

    _report(
        report,
        "vehicle.missing_segment",
        df["segment"].isna().sum(),
        "kept null",
    )

    dim = df[
        [
            "vehicle_id",
            "make",
            "model",
            "segment",
            "fuel_type",
            "list_price_gbp",
        ]
    ].reset_index(drop=True)

    return dim, report


def build_fct_orders(
    raw: pd.DataFrame,
    dim_vehicle: pd.DataFrame,
) -> tuple[pd.DataFrame, list[dict]]:
    report: list[dict] = []

    df = raw.copy()
    rows_in = len(df)

    df["order_id"] = (
        pd.to_numeric(df["order_id"], errors="coerce")
        .astype("Int64")
    )

    _report(
        report,
        "order.order_id_unparseable",
        df["order_id"].isna().sum(),
        "dropped",
    )

    df = df.dropna(subset=["order_id"])

    duplicate_rows = df.duplicated(keep="first").sum()

    _report(
        report,
        "order.exact_duplicate_rows",
        duplicate_rows,
        "dropped",
    )

    df = df.drop_duplicates(keep="first")

    duplicate_orders = (
        df["order_id"]
        .duplicated(keep="last")
        .sum()
    )

    # Keep the latest version of a corrected order
    _report(
        report,
        "order.duplicate_order_id",
        duplicate_orders,
        "kept last occurrence",
    )

    df = df.drop_duplicates(
        subset=["order_id"],
        keep="last",
    )

    df["vehicle_id"] = (
        pd.to_numeric(df["vehicle_id"], errors="coerce")
        .astype("Int64")
    )

    df["market"], market_ok = clean.apply_pair(
        df["market"],
        clean.clean_market,
    )

    _report(
        report,
        "order.unmapped_market",
        (~market_ok).sum(),
        "kept as provided",
    )

    df["channel"], channel_ok = clean.apply_pair(
        df["channel"],
        clean.clean_channel,
    )

    _report(
        report,
        "order.unmapped_channel",
        (~channel_ok & df["channel"].notna()).sum(),
        "kept as provided",
    )

    _report(
        report,
        "order.missing_channel",
        df["channel"].isna().sum(),
        "kept null",
    )

    df["order_status"], _ = clean.apply_pair(
        df["order_status"],
        clean.clean_status,
    )

    df["currency"], currency_ok = clean.apply_pair(
        df["currency"],
        clean.clean_currency,
    )

    _report(
        report,
        "order.unknown_currency",
        (~currency_ok & df["currency"].notna()).sum(),
        "sale_amount_gbp will be null",
    )

    # Keep the supplied currency just flag mismatches
    expected_currency = df["market"].map(
        config.MARKET_DEFAULT_CURRENCY
    )

    currency_mismatch = (
        df["currency"].notna()
        & expected_currency.notna()
        & (df["currency"] != expected_currency)
    )

    _report(
        report,
        "order.currency_market_mismatch",
        currency_mismatch.sum(),
        "flagged",
    )

    df["order_date"] = df["order_date"].map(clean.parse_date)
    df["delivery_date"] = df["delivery_date"].map(clean.parse_date)

    _report(
        report,
        "order.order_date_unparseable",
        df["order_date"].isna().sum(),
        "kept row",
    )

    future_orders = (
        df["order_date"].notna()
        & (df["order_date"] > pd.Timestamp.now())
    )

    _report(
        report,
        "order.future_order_date",
        future_orders.sum(),
        "flagged",
    )

    invalid_delivery = (
        df["order_date"].notna()
        & df["delivery_date"].notna()
        & (df["delivery_date"] < df["order_date"])
    )

    _report(
        report,
        "order.delivery_before_order",
        invalid_delivery.sum(),
        "delivery date removed",
    )

    # Invalid lead times become unknown
    df.loc[invalid_delivery, "delivery_date"] = pd.NaT

    df["sale_amount_raw"] = (
        df["sale_amount"]
        .map(clean.parse_amount)
    )

    non_positive_sales = (
        df["sale_amount_raw"].notna()
        & (df["sale_amount_raw"] <= 0)
    )

    _report(
        report,
        "order.nonpositive_sale_amount",
        non_positive_sales.sum(),
        "excluded from revenue metrics",
    )

    df["sale_amount_raw"] = (
        df["sale_amount_raw"]
        .mask(non_positive_sales)
    )

    fx_rate = df["currency"].map(
        config.FX_RATES_TO_GBP
    )

    df["sale_amount_gbp"] = (
        df["sale_amount_raw"] * fx_rate
    ).round(2)

    email, email_ok = clean.apply_pair(
        df["customer_email"],
        clean.clean_email,
    )

    df["customer_email"] = email

    _report(
        report,
        "order.invalid_email",
        (~email_ok & email.notna()).sum(),
        "flagged",
    )

    valid_vehicle_ids = set(
        dim_vehicle["vehicle_id"]
        .dropna()
        .tolist()
    )

    orphan_vehicle = (
        df["vehicle_id"].notna()
        & ~df["vehicle_id"].isin(valid_vehicle_ids)
    )

    _report(
        report,
        "order.orphan_vehicle_id",
        orphan_vehicle.sum(),
        "kept in fact table",
    )

    # Keep orphan orders for sales totals
    df["vehicle_known"] = (
        df["vehicle_id"]
        .isin(valid_vehicle_ids)
    )

    # Fields used by the marts
    df["is_completed"] = (
        df["order_status"]
        .isin(config.COMPLETED_STATUSES)
    )

    df["order_month"] = (
        df["order_date"]
        .dt.to_period("M")
        .astype("string")
    )

    df["days_to_delivery"] = (
        df["delivery_date"] - df["order_date"]
    ).dt.days.astype("Int64")

    _report(
        report,
        "order.rows_in",
        rows_in,
        "raw rows read",
    )

    _report(
        report,
        "order.rows_out",
        len(df),
        "rows in fact table",
    )

    fct = df[
        [
            "order_id",
            "vehicle_id",
            "vehicle_known",
            "market",
            "currency",
            "channel",
            "order_date",
            "delivery_date",
            "order_month",
            "order_status",
            "is_completed",
            "sale_amount_raw",
            "sale_amount_gbp",
            "days_to_delivery",
            "customer_email",
        ]
    ].reset_index(drop=True)

    return fct, report