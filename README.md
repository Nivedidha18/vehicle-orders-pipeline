# Vehicle Orders Analytics Pipeline

## Overview

This project builds a small analytics pipeline for vehicle order data.
The pipeline takes two raw CSV files:

- `orders.csv`
- `vehicles.csv`

and transforms them into cleaned analytical tables that can be queried for reporting.

The main tools used are:

- **Python + pandas** for cleaning and validation
- **DuckDB + SQL** for modelling and analytical queries

The pipeline runs locally and creates a small warehouse containing cleaned data, reporting marts, and a quality report showing the issues found during processing.

## Running the Pipeline

```bash
pip install -r requirements.txt

Place input files in:
data/
├── orders.csv
└── vehicles.csv

#Run:
python -m src.pipeline.run

#Generated files:

build/warehouse.duckdb
build/quality_report.csv
analysis/answers.md

Running Tests

The project uses pytest.

#Run:
pytest -q

#Tests cover:

cleaning functions
data quality rules
vehicle and order transformations
DuckDB marts
SQL outputs


## Layout

src/pipeline/
config.py # configuration, FX rates, and mappings
ingest.py # loads raw CSV files and checks the input format
clean.py # handles cleaning and standardising data
model.py # creates the vehicle and order tables
questions.sql # SQL queries for the reporting tables
run.py # runs the complete pipeline

tests/ # pipeline tests and reporting checks

## Assumptions & trade-offs

- Duplicate order IDs are treated as corrections, so the latest record is kept.
- Invalid delivery dates are removed, but the order remains in the dataset.
- Orders with unknown vehicle references are kept and flagged for tracking
- FX conversion uses a fixed lookup table suitable for this exercise.
- Date formats are interpreted based on the formats found in the source data.

## Discussion

- Use incremental processing with a watermark and upsert logic to handle daily updates without duplicates.
- Partition large order tables by date to improve query performance
- Define business metrics in one place so reports use consistent definitions.
- Add automated data quality checks and alerts for failures or unusual changes.
- Validate source schema changes before processing new data.
- Protect customer data by limiting access and anonymising personal information where possible.


```
