import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Payments Analytics Dashboard",
    layout="wide"
)

st.title("Payments Analytics Dashboard")
st.markdown("An end-to-end analytics dashboard built from the Online Retail dataset, modelled as a payments analytics platform.")

# ================================
# Load data
# ================================

monthly_summary = pd.read_csv("output/monthly_summary.csv")
customer_summary = pd.read_csv("output/customer_summary.csv")
product_summary = pd.read_csv("output/product_summary.csv")
country_summary = pd.read_csv("output/country_summary.csv")

# Make sure monthly data is ordered
monthly_summary = monthly_summary.sort_values("payment_month")

# ================================
# KPI calculations
# ================================

gross_payment_volume = monthly_summary["monthly_revenue"].sum()
total_orders = monthly_summary["monthly_orders"].sum()
unique_customers = customer_summary["customer_id"].nunique()
average_order_value = gross_payment_volume / total_orders if total_orders > 0 else 0

# ================================
# KPI cards
# ================================

st.subheader("Overview KPIs")

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

kpi_col1.metric("Gross Payment Volume", f"{gross_payment_volume:,.2f}")
kpi_col2.metric("Total Orders", f"{int(total_orders):,}")
kpi_col3.metric("Unique Customers", f"{int(unique_customers):,}")
kpi_col4.metric("Average Order Value", f"{average_order_value:,.2f}")

# ================================
# Monthly revenue trend
# ================================

st.subheader("Monthly Revenue Trend")

fig1, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(monthly_summary["payment_month"], monthly_summary["monthly_revenue"], marker="o")
ax1.set_title("Monthly Revenue")
ax1.set_xlabel("Month")
ax1.set_ylabel("Revenue")
plt.xticks(rotation=45)
st.pyplot(fig1)

# ================================
# Product and country charts
# ================================

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Top 10 Products by Revenue")
    top_products = product_summary.head(10).sort_values("product_revenue", ascending=True)

    fig2, ax2 = plt.subplots(figsize=(8, 6))
    ax2.barh(top_products["product_name"], top_products["product_revenue"])
    ax2.set_xlabel("Revenue")
    ax2.set_title("Top Products")
    st.pyplot(fig2)

with chart_col2:
    st.subheader("Top 10 Countries by Revenue")
    top_countries = country_summary.head(10).sort_values("country_revenue", ascending=True)

    fig3, ax3 = plt.subplots(figsize=(8, 6))
    ax3.barh(top_countries["country"], top_countries["country_revenue"])
    ax3.set_xlabel("Revenue")
    ax3.set_title("Top Countries")
    st.pyplot(fig3)

# ================================
# Customer insights
# ================================

st.subheader("Top Customers by Spend")

top_customers = customer_summary.sort_values("total_spent", ascending=False).head(10)
st.dataframe(top_customers)

# ================================
# Monthly summary table
# ================================

st.subheader("Monthly Summary Table")
st.dataframe(monthly_summary)
