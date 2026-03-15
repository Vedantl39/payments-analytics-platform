-- =========================================
-- Revenue Analytics
-- =========================================

CREATE VIEW monthly_revenue_summary AS
SELECT
    DATE_TRUNC('month', payment_date) AS revenue_month,
    SUM(total_price) AS total_revenue,
    COUNT(DISTINCT payment_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    AVG(total_price) AS average_order_value
FROM fact_payments
GROUP BY 1
ORDER BY 1;


-- =========================================
-- Top Products by Revenue
-- =========================================

SELECT
    p.product_name,
    SUM(f.total_price) AS product_revenue,
    SUM(f.quantity) AS total_units_sold
FROM fact_payments f
JOIN dim_products p
ON f.product_id = p.product_id
GROUP BY p.product_name
ORDER BY product_revenue DESC
LIMIT 10;


-- =========================================
-- Top Customers by Spending
-- =========================================

SELECT
    customer_id,
    COUNT(DISTINCT payment_id) AS total_orders,
    SUM(total_price) AS total_spent
FROM fact_payments
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 10;


-- =========================================
-- Revenue by Country
-- =========================================

SELECT
    country,
    SUM(total_price) AS revenue,
    COUNT(DISTINCT customer_id) AS customers
FROM fact_payments
GROUP BY country
ORDER BY revenue DESC;
