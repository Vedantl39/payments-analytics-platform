import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Payments Analytics Dashboard",
    layout="wide"
)

st.title("Payments Analytics Dashboard")
st.markdown(
    "An end-to-end analytics dashboard built from the Online Retail dataset, "
    "modelled as a payments analytics platform."
)

# ================================
# Load data
# ================================

@st.cache_data
def load_data():
    monthly = pd.read_csv("output/monthly_summary.csv")
    customers = pd.read_csv("output/customer_summary.csv")
    products = pd.read_csv("output/product_summary.csv")
    countries = pd.read_csv("output/country_summary.csv")
    return monthly, customers, products, countries


monthly_summary, customer_summary, product_summary, country_summary = load_data()

# Make sure monthly data is ordered
monthly_summary = monthly_summary.sort_values("payment_month")
product_summary = product_summary.sort_values("product_revenue", ascending=False)
country_summary = country_summary.sort_values("country_revenue", ascending=False)
customer_summary = customer_summary.sort_values("total_spent", ascending=False)

# ================================
# Sidebar filters
# ================================

st.sidebar.header("Dashboard Filters")

top_n = st.sidebar.slider(
    "Select number of top records to display",
    min_value=5,
    max_value=20,
    value=10,
    step=1
)

selected_country = st.sidebar.selectbox(
    "Highlight country",
    ["All"] + country_summary["country"].dropna().astype(str).tolist()
)

# ================================
# KPI calculations
# ================================

gross_payment_volume = monthly_summary["monthly_revenue"].sum()
total_orders = monthly_summary["monthly_orders"].sum()
unique_customers = customer_summary["customer_id"].nunique()
average_order_value = gross_payment_volume / total_orders if total_orders > 0 else 0

# Country-specific KPI if selected
if selected_country != "All":
    selected_country_row = country_summary[country_summary["country"] == selected_country]

    if not selected_country_row.empty:
        selected_country_revenue = selected_country_row["country_revenue"].iloc[0]
        selected_country_orders = selected_country_row["total_orders"].iloc[0]
        selected_country_customers = selected_country_row["unique_customers"].iloc[0]
        selected_country_aov = selected_country_row["average_order_value"].iloc[0]
    else:
        selected_country_revenue = 0
        selected_country_orders = 0
        selected_country_customers = 0
        selected_country_aov = 0

# ================================
# Key Insights
# ================================

st.subheader("Key Insights")

st.markdown("""
- The United Kingdom is the dominant revenue market in the dataset.
- Revenue is concentrated among a small group of products and customers.
- Monthly revenue trends show strong variation across the year.
- Average order value remains relatively stable despite changes in order volume.
""")

# ================================
# KPI cards
# ================================

st.subheader("Overview KPIs")

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

kpi_col1.metric("Gross Payment Volume", f"{gross_payment_volume:,.2f}")
kpi_col2.metric("Total Orders", f"{int(total_orders):,}")
kpi_col3.metric("Unique Customers", f"{int(unique_customers):,}")
kpi_col4.metric("Average Order Value", f"{average_order_value:,.2f}")

if selected_country != "All":
    st.subheader(f"{selected_country} KPIs")

    country_kpi1, country_kpi2, country_kpi3, country_kpi4 = st.columns(4)

    country_kpi1.metric("Country Revenue", f"{selected_country_revenue:,.2f}")
    country_kpi2.metric("Country Orders", f"{int(selected_country_orders):,}")
    country_kpi3.metric("Country Customers", f"{int(selected_country_customers):,}")
    country_kpi4.metric("Country AOV", f"{selected_country_aov:,.2f}")

# ================================
# Monthly revenue trend
# ================================

st.subheader("Monthly Revenue Trend")

revenue_chart = monthly_summary.set_index("payment_month")["monthly_revenue"]
st.line_chart(revenue_chart)

# ================================
# Product and country charts
# ================================

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader(f"Top {top_n} Products by Revenue")
    top_products = (
        product_summary.head(top_n)
        .set_index("product_name")[["product_revenue"]]
    )
    st.bar_chart(top_products)

with chart_col2:
    st.subheader(f"Top {top_n} Countries by Revenue")
    top_countries = (
        country_summary.head(top_n)
        .set_index("country")[["country_revenue"]]
    )
    st.bar_chart(top_countries)

# ================================
# Customer insights
# ================================

st.subheader(f"Top {top_n} Customers by Spend")

top_customers = customer_summary.head(top_n).copy()

# Optional formatting for date columns if they exist
for date_col in ["first_purchase", "last_purchase"]:
    if date_col in top_customers.columns:
        top_customers[date_col] = pd.to_datetime(
            top_customers[date_col],
            errors="coerce"
        ).dt.strftime("%Y-%m-%d")

st.dataframe(top_customers, use_container_width=True)

# ================================
# Country summary table
# ================================

st.subheader("Country Summary")

display_country_summary = country_summary.copy()
st.dataframe(display_country_summary, use_container_width=True)

# ================================
# Monthly summary table
# ================================

st.subheader("Monthly Summary Table")
st.dataframe(monthly_summary, use_container_width=True)
