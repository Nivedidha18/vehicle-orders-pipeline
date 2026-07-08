from __future__ import annotations
from pathlib import Path
import pandas as pd
from . import config

ORDER_COLUMNS = [
    "order_id",
    "vehicle_id",
    "market",
    "currency",
    "channel",
    "order_date",
    "delivery_date",
    "order_status",
    "sale_amount",
    "customer_email",
]

VEHICLE_COLUMNS = [
    "vehicle_id",
    "make",
    "model",
    "segment",
    "fuel_type",
    "list_price_gbp",
]

def _read(path: Path, expected: list[str]) -> pd.DataFrame:
    # Keep everything as strings. Type conversion happens later.
    df = pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        na_values=[""],
    )

    df.columns = [col.strip().lower() for col in df.columns]
    missing = set(expected) - set(df.columns)
    if missing:
        raise ValueError(
            f"{path.name}: missing columns {sorted(missing)}"
        )
    return df


def read_orders(path: Path | None = None) -> pd.DataFrame:
    return _read(
        path or config.ORDERS_CSV,
        ORDER_COLUMNS,
    )


def read_vehicles(path: Path | None = None) -> pd.DataFrame:
    return _read(
        path or config.VEHICLES_CSV,
        VEHICLE_COLUMNS,
    )