import pandas as pd

print("Loading data...")

buyers_table = pd.read_csv("data/dim_customers.csv")
items_table = pd.read_csv("data/dim_products.csv")
sales_table = pd.read_csv("data/fact_payments.csv")

buyers_table.columns = buyers_table.columns.str.strip().str.lower()
items_table.columns = items_table.columns.str.strip().str.lower()
sales_table.columns = sales_table.columns.str.strip().str.lower()

buyers_table = buyers_table.dropna(subset=["customer_id"]).drop_duplicates(subset=["customer_id"])
items_table = items_table.drop_duplicates(subset=["product_id"])

sales_table["payment_date"] = pd.to_datetime(
    sales_table["payment_date"],
    errors="coerce"
)

print("Joining tables...")

payments_full = sales_table.merge(
    buyers_table,
    on="customer_id",
    how="left",
    suffixes=("", "_customer")
)

payments_full = payments_full.merge(
    items_table,
    on="product_id",
    how="left"
)

print("Merged shape:", payments_full.shape)

# ================================
# CORE KPIs
# ================================

print("\n================ CORE KPIs ================")

gross_payment_volume = payments_full["total_price"].sum()
total_orders = payments_full["payment_id"].nunique()
unique_customers = payments_full["customer_id"].nunique()
avg_order_value = payments_full["total_price"].mean()
total_units_sold = payments_full["quantity"].sum()

print("Gross Payment Volume:", round(gross_payment_volume, 2))
print("Total Orders:", total_orders)
print("Unique Customers:", unique_customers)
print("Average Order Value:", round(avg_order_value, 2))
print("Total Units Sold:", total_units_sold)

# ================================
# REVENUE ANALYTICS
# ================================

print("\n================ REVENUE ANALYTICS ================")

payments_full["payment_month"] = payments_full["payment_date"].dt.to_period("M").astype(str)

monthly_revenue = (
    payments_full.groupby("payment_month", as_index=False)["total_price"]
    .sum()
    .rename(columns={"total_price": "monthly_revenue"})
)

monthly_orders = (
    payments_full.groupby("payment_month", as_index=False)["payment_id"]
    .nunique()
    .rename(columns={"payment_id": "monthly_orders"})
)

monthly_active_customers = (
    payments_full.groupby("payment_month", as_index=False)["customer_id"]
    .nunique()
    .rename(columns={"customer_id": "monthly_active_customers"})
)

monthly_summary = monthly_revenue.merge(monthly_orders, on="payment_month", how="left")
monthly_summary = monthly_summary.merge(monthly_active_customers, on="payment_month", how="left")
monthly_summary["monthly_average_order_value"] = (
    monthly_summary["monthly_revenue"] / monthly_summary["monthly_orders"]
)

print(monthly_summary)

# ================================
# CUSTOMER ANALYTICS
# ================================

print("\n================ CUSTOMER ANALYTICS ================")

customer_summary = (
    payments_full.groupby("customer_id", as_index=False)
    .agg(
        total_spent=("total_price", "sum"),
        total_orders=("payment_id", "nunique"),
        total_units=("quantity", "sum"),
        first_purchase=("payment_date", "min"),
        last_purchase=("payment_date", "max")
    )
    .sort_values("total_spent", ascending=False)
)

top_customers_by_spend = customer_summary.head(10)

repeat_customers = customer_summary[customer_summary["total_orders"] > 1]

repeat_customer_count = repeat_customers["customer_id"].nunique()
repeat_customer_rate = repeat_customer_count / unique_customers if unique_customers > 0 else 0

print("Repeat Customer Count:", repeat_customer_count)
print("Repeat Customer Rate:", round(repeat_customer_rate * 100, 2), "%")
print("\nTop Customers by Spend:")
print(top_customers_by_spend)

# ================================
# PRODUCT ANALYTICS
# ================================

print("\n================ PRODUCT ANALYTICS ================")

product_summary = (
    payments_full.groupby("product_name", as_index=False)
    .agg(
        product_revenue=("total_price", "sum"),
        units_sold=("quantity", "sum"),
        order_count=("payment_id", "nunique")
    )
    .sort_values("product_revenue", ascending=False)
)

top_products_by_revenue = product_summary.head(10)
top_products_by_units = product_summary.sort_values("units_sold", ascending=False).head(10)

print("\nTop Products by Revenue:")
print(top_products_by_revenue)

print("\nTop Products by Units Sold:")
print(top_products_by_units)

# ================================
# GEOGRAPHIC ANALYTICS
# ================================

print("\n================ GEOGRAPHIC ANALYTICS ================")

country_summary = (
    payments_full.groupby("country", as_index=False)
    .agg(
        country_revenue=("total_price", "sum"),
        unique_customers=("customer_id", "nunique"),
        total_orders=("payment_id", "nunique")
    )
    .sort_values("country_revenue", ascending=False)
)

country_summary["average_order_value"] = (
    country_summary["country_revenue"] / country_summary["total_orders"]
)

top_countries = country_summary.head(10)

print(top_countries)

# ================================
# EXPORT OUTPUTS
# ================================

monthly_summary.to_csv("output/monthly_summary.csv", index=False)
customer_summary.to_csv("output/customer_summary.csv", index=False)
product_summary.to_csv("output/product_summary.csv", index=False)
country_summary.to_csv("output/country_summary.csv", index=False)

print("\nAnalytics outputs saved to output/")
print("\nScript completed successfully.")

import matplotlib.pyplot as plt

# Monthly revenue chart
plt.figure(figsize=(10, 5))
plt.plot(monthly_summary["payment_month"], monthly_summary["monthly_revenue"], marker="o")
plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("output/monthly_revenue.png")
plt.close()

# Top products chart
top_10_products = product_summary.head(10).sort_values("product_revenue", ascending=True)

plt.figure(figsize=(10, 6))
plt.barh(top_10_products["product_name"], top_10_products["product_revenue"])
plt.title("Top 10 Products by Revenue")
plt.xlabel("Revenue")
plt.tight_layout()
plt.savefig("output/top_products.png")
plt.close()

# Top countries chart
top_10_countries = country_summary.head(10).sort_values("country_revenue", ascending=True)

plt.figure(figsize=(10, 6))
plt.barh(top_10_countries["country"], top_10_countries["country_revenue"])
plt.title("Top Countries by Revenue")
plt.xlabel("Revenue")
plt.tight_layout()
plt.savefig("output/top_countries.png")
plt.close()

print("Charts saved to output/")
