-- Sales value by market and month
CREATE OR REPLACE VIEW mart_sales_by_market_month AS
SELECT
    market,
    order_month,
    ROUND(SUM(sale_amount_gbp), 2) AS completed_sales_gbp,
    COUNT(*) AS completed_orders
FROM fct_orders
WHERE is_completed
  AND sale_amount_gbp IS NOT NULL
  AND order_month IS NOT NULL
GROUP BY market, order_month
ORDER BY market, order_month;


-- Top 5 selling vehicle models
CREATE OR REPLACE VIEW mart_top_models AS
SELECT
    v.make,
    v.model,
    COUNT(*) AS units_sold
FROM fct_orders f
JOIN dim_vehicle v USING (vehicle_id)
WHERE f.is_completed
GROUP BY v.make, v.model
ORDER BY units_sold DESC, v.make, v.model
LIMIT 5;

-- Average delivery time by market
CREATE OR REPLACE VIEW mart_lead_time_by_market AS
SELECT
    market,
    ROUND(AVG(days_to_delivery), 1) AS avg_days_order_to_delivery,
    COUNT(*) AS delivered_orders
FROM fct_orders
WHERE days_to_delivery IS NOT NULL
GROUP BY market
ORDER BY market;

-- Order share by sales channel
CREATE OR REPLACE VIEW mart_channel_share AS
SELECT
    channel,
    COUNT(*) AS orders,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS pct_of_orders
FROM fct_orders
WHERE channel IS NOT NULL
GROUP BY channel
ORDER BY orders DESC;