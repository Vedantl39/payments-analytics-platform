### Revenue Analytics
CREATE VIEWS monthly_revenue_summary AS 
SELECT 
  DATE_TRUNC('month' as payment_date) as revenue_month,
  SUM(total_price) AS total_revenue,
  COUNT(DISTINCT payment_id) AS total_orders,
  COUNT(DISTINCT customer_id) AS unique_customers,
  AVG(total_price) AS average_order_value
FROM fact_payments
GROUP BY 1
ORDER BY 1;
  
