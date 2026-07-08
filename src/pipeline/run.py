
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from . import config, ingest, model


def _persist(dim: pd.DataFrame, fct: pd.DataFrame):
    import duckdb

    config.OUT_DIR.mkdir(parents=True, exist_ok=True)
    config.PARQUET_DIR.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(config.DUCKDB_PATH))

    con.register("dim_df", dim)
    con.register("fct_df", fct)

    con.execute(
        "CREATE OR REPLACE TABLE dim_vehicle AS "
        "SELECT * FROM dim_df"
    )

    con.execute(
        "CREATE OR REPLACE TABLE fct_orders AS "
        "SELECT * FROM fct_df"
    )

    con.execute(
        f"COPY (SELECT * FROM fct_orders) "
        f"TO '{config.PARQUET_DIR}/fct_orders' "
        "(FORMAT PARQUET, PARTITION_BY (market), OVERWRITE_OR_IGNORE)"
    )

    con.execute(
        f"COPY (SELECT * FROM dim_vehicle) "
        f"TO '{config.PARQUET_DIR}/dim_vehicle.parquet' "
        "(FORMAT PARQUET)"
    )

    sql = (
        Path(__file__).parent / "questions.sql"
    ).read_text(encoding="utf-8")

    con.execute(sql)

    return con


def _write_answers(con, quality: pd.DataFrame) -> None:
    marts = [
        (
            "Sales by market and month",
            "SELECT * FROM mart_sales_by_market_month",
        ),
        (
            "Top 5 models sold",
            "SELECT * FROM mart_top_models",
        ),
        (
            "Average delivery lead time by market",
            "SELECT * FROM mart_lead_time_by_market",
        ),
        (
            "Order share by channel",
            "SELECT * FROM mart_channel_share",
        ),
    ]

    parts = [
        "# Business Answers",

    ]

    for title, query in marts:
        result = con.execute(query).df().to_markdown(index=False)

        parts.extend(
            [
                "",
                f"## {title}",
                "",
                result,
            ]
        )

    parts.extend(
        [
            "",
            "## Data Quality Checks",
            "",
            "Summary of issues found during processing.",
            "",
            quality.to_markdown(index=False),
        ]
    )

    output_file = config.ROOT / "analysis" / "answers.md"
    output_file.parent.mkdir(exist_ok=True)

    output_file.write_text(
        "\n".join(parts),
        encoding="utf-8",
    )

    print(f"Wrote {output_file}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Vehicle orders analytics pipeline"
    )

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
    )

    args = parser.parse_args(argv)

    orders_csv = (
        args.data_dir / "orders.csv"
        if args.data_dir
        else None
    )

    vehicles_csv = (
        args.data_dir / "vehicles.csv"
        if args.data_dir
        else None
    )

    raw_orders = ingest.read_orders(orders_csv)
    raw_vehicles = ingest.read_vehicles(vehicles_csv)

    dim, vehicle_report = model.build_dim_vehicle(raw_vehicles)
    fct, order_report = model.build_fct_orders(raw_orders, dim)

    quality = pd.DataFrame(
        vehicle_report + order_report
    )[["check", "n", "detail"]]

    config.OUT_DIR.mkdir(parents=True, exist_ok=True)

    quality.to_csv(
        config.OUT_DIR / "quality_report.csv",
        index=False,
    )

    print(quality.to_string(index=False))

    con = None

    try:
        con = _persist(dim, fct)
        _write_answers(con, quality)

    finally:
        if con is not None:
            con.close()

    print(
        f"\ndim_vehicle: {len(dim):,} rows | "
        f"fct_orders: {len(fct):,} rows"
    )

    print(f"warehouse: {config.DUCKDB_PATH}")


if __name__ == "__main__":
    main()