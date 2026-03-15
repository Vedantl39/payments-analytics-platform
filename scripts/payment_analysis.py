# ================================
# Payments Analytics Platform
# Python Analysis Layer
# ================================

# Friendly note:
# This notebook takes the cleaned fact and dimension tables,
# joins them together, and produces business metrics + charts.


# ================================
# 1. Import libraries
# ================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ================================
# 2. Load datasets
# ================================

buyers_table = pd.read_csv("../data/dim_customers.csv")
items_table = pd.read_csv("../data/dim_products.csv")
sales_table = pd.read_csv("../data/fact_payments.csv")

print("Customers shape:", buyers_table.shape)
print("Products shape:", items_table.shape)
print("Payments shape:", sales_table.shape)


# ================================
# 3. Quick preview
# ================================

print("\nCustomers preview:")
print(buyers_table.head())

print("\nProducts preview:")
print(items_table.head())

print("\nPayments preview:")
print(sales_table.head())


# ================================
# 4. Standardise column names
# ================================

buyers_table.columns = buyers_table.columns.str.strip().str.lower()
items_table.columns = items_table.columns.str.strip().str.lower()
sales_table.columns = sales_table.columns.str.strip().str.lower()

print("\nColumn names after standardisation:")
print("Customers:", buyers_table.columns.tolist())
print("Products:", items_table.columns.tolist())
print("Payments:", sales_table.columns.tolist())


# ================================
# 5. Convert data types
# ================================

sales_table["payment_date"] = pd.to_datetime(sales_table["payment_date"], errors="coerce")

numeric_fields = ["quantity", "unit_price", "total_price"]
for field_name in numeric_fields:
    sales_table[field_name] = pd.to_numeric(sales_table[field_name], errors="coerce")

sales_table["customer_id"] = pd.to_numeric(sales_table["customer_id"], errors="coerce")
buyers_table["customer_id"] = pd.to_numeric(buyers_table["customer_id"], errors="coerce")

sales_table["customer_id"] = sales_table["customer_id"].astype("Int64")
buyers_table["customer_id"] = buyers_table["customer_id"].astype("Int64")


# ================================
# 6. Basic null check
# ================================

print("\nNull values in payments table:")
print(sales_table.isnull().sum())

print("\nNull values in customers table:")
print(buyers_table.isnull().sum())

print("\nNull values in products table:")
print(items_table.isnull().sum())


# ================================
# 7. Merge dimension + fact tables
# ================================

joined_frame = sales_table.merge(
    items_table,
    on="product_id",
    how="left",
    suffixes=("", "_product")
)

joined_frame = joined_frame.merge(
    buyers_table,
    on="customer_id",
    how="left",
    suffixes=("", "_customer")
)

print("\nMerged dataset shape:", joined_frame.shape)
print(joined_frame.head())


# ================================
# 8. Clean duplicated country columns if needed
# ================================

# If both fact_payments and dim_customers contain country,
# keep the payment-level country first and fall back to customer country.

if "country_customer" in joined_frame.columns:
    joined_frame["final_country"] = joined_frame["country"].fillna(joined_frame["country_customer"])
else:
    joined_frame["final_country"] = joined_frame["country"]

# If a second product name appeared after merge, tidy it up
if "product_name_product" in joined_frame.columns:
    joined_frame["final_product_name"] = joined_frame["product_name"].fillna(joined_frame["product_name_product"])
else:
    joined_frame["final_product_name"] = joined_frame["product_name"]


# ================================
# 9. Create extra time features
# ================================

joined_frame["payment_month"] = joined_frame["payment_date"].dt.to_period("M").dt.to_timestamp()
joined_frame["payment_year"] = joined_frame["payment_date"].dt.year
joined_frame["payment_day"] = joined_frame["payment_date"].dt.date


# ================================
# 10. Core KPI calculations
# ================================

gross_payment_volume = joined_frame["total_price"].sum()
total_orders_count = joined_frame["payment_id"].nunique()
unique_buyers_count = joined_frame["customer_id"].nunique()
average_order_value = joined_frame["total_price"].mean()
total_units_sold = joined_frame["quantity"].sum()

print("\n================ PAYMENT KPIs ================ ")
print(f"Gross Payment Volume (GPV): {gross_payment_volume:,.2f}")
print(f"Total Orders: {total_orders_count:,}")
print(f"Unique Customers: {unique_buyers_count:,}")
print(f"Average Order Value (AOV): {average_order_value:,.2f}")
print(f"Total Units Sold: {total_units_sold:,.0f}")


# ================================
# 11. Monthly revenue summary
# ================================

monthly_money = (
    joined_frame.groupby("payment_month", as_index=False)["total_price"]
    .sum()
    .sort_values("payment_month")
)

monthly_orders = (
    joined_frame.groupby("payment_month", as_index=False)["payment_id"]
    .nunique()
    .rename(columns={"payment_id": "order_count"})
)

monthly_users = (
    joined_frame.groupby("payment_month", as_index=False)["customer_id"]
    .nunique()
    .rename(columns={"customer_id": "customer_count"})
)

monthly_kpi_table = monthly_money.merge(monthly_orders, on="payment_month", how="left")
monthly_kpi_table = monthly_kpi_table.merge(monthly_users, on="payment_month", how="left")
monthly_kpi_table["average_order_value"] = monthly_kpi_table["total_price"] / monthly_kpi_table["order_count"]

print("\nMonthly KPI summary:")
print(monthly_kpi_table.head())


# ================================
# 12. Top products by revenue
# ================================

best_earning_products = (
    joined_frame.groupby("final_product_name", as_index=False)
    .agg(
        product_revenue=("total_price", "sum"),
        units_sold=("quantity", "sum"),
        order_lines=("payment_id", "count")
    )
    .sort_values("product_revenue", ascending=False)
    .head(10)
)

print("\nTop 10 products by revenue:")
print(best_earning_products)


# ================================
# 13. Top customers by spend
# ================================

highest_value_customers = (
    joined_frame.groupby("customer_id", as_index=False)
    .agg(
        lifetime_spend=("total_price", "sum"),
        order_count=("payment_id", "nunique"),
        total_units=("quantity", "sum")
    )
    .sort_values("lifetime_spend", ascending=False)
    .head(10)
)

print("\nTop 10 customers by lifetime spend:")
print(highest_value_customers)


# ================================
# 14. Revenue by country
# ================================

country_money_table = (
    joined_frame.groupby("final_country", as_index=False)
    .agg(
        country_revenue=("total_price", "sum"),
        customer_count=("customer_id", "nunique"),
        order_count=("payment_id", "nunique")
    )
    .sort_values("country_revenue", ascending=False)
    .head(10)
)

print("\nTop 10 countries by revenue:")
print(country_money_table)


# ================================
# 15. Monthly active customers
# ================================

monthly_active_buyers = (
    joined_frame.groupby("payment_month", as_index=False)["customer_id"]
    .nunique()
    .rename(columns={"customer_id": "monthly_active_customers"})
)

print("\nMonthly active customers:")
print(monthly_active_buyers.head())


# ================================
# 16. Customer spend distribution
# ================================

buyer_value_curve = (
    joined_frame.groupby("customer_id", as_index=False)["total_price"]
    .sum()
    .rename(columns={"total_price": "customer_lifetime_value"})
)

print("\nCustomer lifetime value summary:")
print(buyer_value_curve["customer_lifetime_value"].describe())


# ================================
# 17. Plot 1 - Monthly revenue trend
# ================================

plt.figure(figsize=(12, 6))
plt.plot(monthly_kpi_table["payment_month"], monthly_kpi_table["total_price"], marker="o")
plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# ================================
# 18. Plot 2 - Top products by revenue
# ================================

product_plot_data = best_earning_products.sort_values("product_revenue", ascending=True)

plt.figure(figsize=(12, 6))
plt.barh(product_plot_data["final_product_name"], product_plot_data["product_revenue"])
plt.title("Top 10 Products by Revenue")
plt.xlabel("Revenue")
plt.ylabel("Product")
plt.tight_layout()
plt.show()


# ================================
# 19. Plot 3 - Revenue by country
# ================================

country_plot_data = country_money_table.sort_values("country_revenue", ascending=True)

plt.figure(figsize=(12, 6))
plt.barh(country_plot_data["final_country"], country_plot_data["country_revenue"])
plt.title("Top 10 Countries by Revenue")
plt.xlabel("Revenue")
plt.ylabel("Country")
plt.tight_layout()
plt.show()


# ================================
# 20. Plot 4 - Customer spend distribution
# ================================

plt.figure(figsize=(12, 6))
plt.hist(buyer_value_curve["customer_lifetime_value"], bins=50)
plt.title("Customer Lifetime Spend Distribution")
plt.xlabel("Total Customer Spend")
plt.ylabel("Number of Customers")
plt.tight_layout()
plt.show()


# ================================
# 21. Plot 5 - Monthly active customers
# ================================

plt.figure(figsize=(12, 6))
plt.plot(
    monthly_active_buyers["payment_month"],
    monthly_active_buyers["monthly_active_customers"],
    marker="o"
)
plt.title("Monthly Active Customers")
plt.xlabel("Month")
plt.ylabel("Active Customers")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# ================================
# 22. Additional insight tables
# ================================

# Top 10 days by revenue
best_revenue_days = (
    joined_frame.groupby("payment_day", as_index=False)["total_price"]
    .sum()
    .sort_values("total_price", ascending=False)
    .head(10)
)

print("\nTop 10 days by revenue:")
print(best_revenue_days)

# Top 10 products by units sold
most_sold_products = (
    joined_frame.groupby("final_product_name", as_index=False)["quantity"]
    .sum()
    .sort_values("quantity", ascending=False)
    .head(10)
)

print("\nTop 10 products by units sold:")
print(most_sold_products)


# ================================
# 23. Simple written insights
# ================================

top_country_name = country_money_table.iloc[0]["final_country"]
top_country_revenue = country_money_table.iloc[0]["country_revenue"]

top_product_name = best_earning_products.iloc[0]["final_product_name"]
top_product_revenue = best_earning_products.iloc[0]["product_revenue"]

top_customer_id = highest_value_customers.iloc[0]["customer_id"]
top_customer_spend = highest_value_customers.iloc[0]["lifetime_spend"]

print("\n================ KEY INSIGHTS ================ ")
print(f"1. Total gross payment volume across the dataset is {gross_payment_volume:,.2f}.")
print(f"2. The average order value is {average_order_value:,.2f}.")
print(f"3. The top revenue-generating country is {top_country_name} with revenue of {top_country_revenue:,.2f}.")
print(f"4. The highest earning product is '{top_product_name}' with total revenue of {top_product_revenue:,.2f}.")
print(f"5. The top customer by spend is {top_customer_id} with lifetime spend of {top_customer_spend:,.2f}.")


# ================================
# 24. Export useful output files
# ================================

monthly_kpi_table.to_csv("../data/monthly_kpi_summary.csv", index=False)
best_earning_products.to_csv("../data/top_products_by_revenue.csv", index=False)
country_money_table.to_csv("../data/top_countries_by_revenue.csv", index=False)
highest_value_customers.to_csv("../data/top_customers_by_spend.csv", index=False)
buyer_value_curve.to_csv("../data/customer_lifetime_value_summary.csv", index=False)

print("\nSummary CSV files exported successfully.")


# ================================
# 25. Export merged analytics table
# ================================

joined_frame.to_csv("../data/analytics_dataset.csv", index=False)
print("Merged analytics dataset exported successfully.")
