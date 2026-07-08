# Business Answers

## Sales by market and month

| market         | order_month   |   completed_sales_gbp |   completed_orders |
|:---------------|:--------------|----------------------:|-------------------:|
| France         | 2025-01       |              364084   |                 10 |
| France         | 2025-02       |              341902   |                 10 |
| France         | 2025-03       |              402176   |                 13 |
| France         | 2025-04       |              496943   |                 14 |
| France         | 2025-05       |              481600   |                 14 |
| France         | 2025-06       |              394447   |                 11 |
| France         | 2025-07       |              140432   |                  4 |
| Germany        | 2025-01       |              146024   |                  4 |
| Germany        | 2025-02       |              204853   |                  6 |
| Germany        | 2025-03       |              279191   |                  9 |
| Germany        | 2025-04       |              206598   |                  6 |
| Germany        | 2025-05       |              215178   |                  8 |
| Germany        | 2025-06       |              303141   |                  8 |
| Germany        | 2025-07       |              323029   |                 10 |
| Netherlands    | 2025-01       |              110588   |                  4 |
| Netherlands    | 2025-02       |              209965   |                  6 |
| Netherlands    | 2025-03       |               68976.6 |                  2 |
| Netherlands    | 2025-04       |              189067   |                  6 |
| Netherlands    | 2025-05       |              199740   |                  5 |
| Netherlands    | 2025-06       |              266794   |                  8 |
| Netherlands    | 2025-07       |              111977   |                  3 |
| United Kingdom | 2025-01       |              423023   |                 13 |
| United Kingdom | 2025-02       |              224372   |                  6 |
| United Kingdom | 2025-03       |              403184   |                 12 |
| United Kingdom | 2025-04       |              417633   |                 13 |
| United Kingdom | 2025-05       |              380691   |                 12 |
| United Kingdom | 2025-06       |              344655   |                 12 |
| United Kingdom | 2025-07       |              194145   |                  7 |

## Top 5 models sold

| make    | model   |   units_sold |
|:--------|:--------|-------------:|
| Jeep    | Avenger |           22 |
| Volvo   | XC40    |           18 |
| Citroen | e-C4    |           17 |
| Peugeot | 2008    |           17 |
| Peugeot | 308     |           16 |

## Average delivery lead time by market

| market         |   avg_days_order_to_delivery |   delivered_orders |
|:---------------|-----------------------------:|-------------------:|
| France         |                         32   |                114 |
| Germany        |                         32.2 |                 82 |
| Netherlands    |                         32.1 |                 53 |
| United Kingdom |                         30.6 |                110 |

## Order share by channel

| channel      |   orders |   pct_of_orders |
|:-------------|---------:|----------------:|
| Online       |      159 |           47.32 |
| Subscription |       91 |           27.08 |
| Dealer       |       86 |           25.6  |

## Data Quality Checks

Summary of issues found during processing.

| check                         |   n | detail                        |
|:------------------------------|----:|:------------------------------|
| vehicle.duplicate_vehicle_id  |   1 | kept first occurrence         |
| order.exact_duplicate_rows    |   1 | dropped                       |
| order.duplicate_order_id      |   1 | kept last occurrence          |
| order.missing_channel         |  89 | kept null                     |
| order.future_order_date       |   1 | flagged                       |
| order.delivery_before_order   |  14 | delivery date removed         |
| order.nonpositive_sale_amount |  10 | excluded from revenue metrics |
| order.orphan_vehicle_id       |   4 | kept in fact table            |
| order.rows_in                 | 427 | raw rows read                 |
| order.rows_out                | 425 | rows in fact table            |