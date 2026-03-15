-- =========================================
-- Data Quality Checks for Payments Analytics Platform
-- =========================================
-- Purpose:
-- These checks validate the integrity, consistency, and completeness
-- of the dimensional model before running analytics queries.
--
-- Tables checked:
-- 1. dim_customers
-- 2. dim_products
-- 3. fact_payments
-- =========================================


-- =========================================
-- 1. NULL CHECKS
-- =========================================

-- Check for missing customer IDs in dim_customers
SELECT *
FROM dim_customers
WHERE customer_id IS NULL;

-- Check for missing countries in dim_customers
SELECT *
FROM dim_customers
WHERE country IS NULL;

-- Check for missing product IDs in dim_products
SELECT *
FROM dim_products
WHERE product_id IS NULL;

-- Check for missing product names in dim_products
SELECT *
FROM dim_products
WHERE product_name IS NULL;

-- Check for missing key fields in fact_payments
SELECT *
FROM fact_payments
WHERE payment_id IS NULL
   OR customer_id IS NULL
   OR product_id IS NULL
   OR payment_date IS NULL
   OR quantity IS NULL
   OR unit_price IS NULL
   OR total_price IS NULL
   OR country IS NULL;


-- =========================================
-- 2. DUPLICATE CHECKS
-- =========================================

-- Check for duplicate customer IDs in dim_customers
SELECT
    customer_id,
    COUNT(*) AS duplicate_count
FROM dim_customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Check for duplicate product IDs in dim_products
SELECT
    product_id,
    COUNT(*) AS duplicate_count
FROM dim_products
GROUP BY product_id
HAVING COUNT(*) > 1;

-- Check for duplicate payment-product rows in fact_payments
-- This helps identify repeated transaction line items beyond expected structure
SELECT
    payment_id,
    product_id,
    COUNT(*) AS duplicate_count
FROM fact_payments
GROUP BY payment_id, product_id
HAVING COUNT(*) > 1;


-- =========================================
-- 3. REFERENTIAL INTEGRITY CHECKS
-- =========================================

-- Check for customer IDs in fact_payments that do not exist in dim_customers
SELECT DISTINCT
    f.customer_id
FROM fact_payments f
LEFT JOIN dim_customers c
    ON f.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- Check for product IDs in fact_payments that do not exist in dim_products
SELECT DISTINCT
    f.product_id
FROM fact_payments f
LEFT JOIN dim_products p
    ON f.product_id = p.product_id
WHERE p.product_id IS NULL;


-- =========================================
-- 4. NUMERIC VALUE CHECKS
-- =========================================

-- Check for zero or negative quantity values
SELECT *
FROM fact_payments
WHERE quantity <= 0;

-- Check for negative unit prices
SELECT *
FROM fact_payments
WHERE unit_price < 0;

-- Check for negative total prices
SELECT *
FROM fact_payments
WHERE total_price < 0;

-- Check for rows where total_price does not match quantity * unit_price
SELECT *
FROM fact_payments
WHERE ROUND(quantity * unit_price, 2) <> ROUND(total_price, 2);


-- =========================================
-- 5. DATE VALIDATION CHECKS
-- =========================================

-- Check for payments with future dates
SELECT *
FROM fact_payments
WHERE payment_date > CURRENT_TIMESTAMP;

-- Check for unusually old dates
-- Adjust the cutoff if needed based on the dataset context
SELECT *
FROM fact_payments
WHERE payment_date < '2000-01-01';


-- =========================================
-- 6. COUNTRY CONSISTENCY CHECKS
-- =========================================

-- Check for countries in fact_payments not found in dim_customers
-- This identifies inconsistencies between transaction-level and customer-level country values
SELECT DISTINCT
    f.customer_id,
    f.country AS payment_country,
    c.country AS customer_country
FROM fact_payments f
JOIN dim_customers c
    ON f.customer_id = c.customer_id
WHERE f.country <> c.country;


-- =========================================
-- 7. BASIC ROW COUNT CHECKS
-- =========================================

-- Count total records in each table
SELECT 'dim_customers' AS table_name, COUNT(*) AS row_count
FROM dim_customers

UNION ALL

SELECT 'dim_products' AS table_name, COUNT(*) AS row_count
FROM dim_products

UNION ALL

SELECT 'fact_payments' AS table_name, COUNT(*) AS row_count
FROM fact_payments;


-- =========================================
-- 8. BUSINESS LOGIC CHECKS
-- =========================================

-- Check for payments with unusually large total_price values
-- Useful for identifying outliers or data entry issues
SELECT *
FROM fact_payments
WHERE total_price > 100000;

-- Check for payments with extremely high quantity values
SELECT *
FROM fact_payments
WHERE quantity > 1000;

-- Check for payments with zero total price
SELECT *
FROM fact_payments
WHERE total_price = 0;


-- =========================================
-- 9. SUMMARY QUALITY METRICS
-- =========================================

-- Summary of null counts in fact_payments
SELECT
    SUM(CASE WHEN payment_id IS NULL THEN 1 ELSE 0 END) AS null_payment_id,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer_id,
    SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) AS null_product_id,
    SUM(CASE WHEN payment_date IS NULL THEN 1 ELSE 0 END) AS null_payment_date,
    SUM(CASE WHEN quantity IS NULL THEN 1 ELSE 0 END) AS null_quantity,
    SUM(CASE WHEN unit_price IS NULL THEN 1 ELSE 0 END) AS null_unit_price,
    SUM(CASE WHEN total_price IS NULL THEN 1 ELSE 0 END) AS null_total_price,
    SUM(CASE WHEN country IS NULL THEN 1 ELSE 0 END) AS null_country
FROM fact_payments;


-- Summary of duplicate payment-product combinations
SELECT
    COUNT(*) AS duplicate_payment_product_groups
FROM (
    SELECT
        payment_id,
        product_id
    FROM fact_payments
    GROUP BY payment_id, product_id
    HAVING COUNT(*) > 1
) duplicate_check;
