# Payments Analytics Platform

An end-to-end analytics project analysing payment transaction data using SQL and Python.

This project simulates a payment processing system and builds an analytics workflow to uncover insights about transaction activity, revenue trends, refunds, and payment performance.

## Project Goals

• Analyse payment volume and revenue trends  
• Understand transaction success and failure patterns  
• Identify merchants with high refund rates  
• Generate operational insights from payment data  

## Tech Stack

Python  
SQL  
PostgreSQL  
Pandas  
Matplotlib  

## Project Structure

data/ → raw and generated datasets  
sql/ → database schema and analytical queries  
scripts/ → data generation and pipeline scripts  
notebooks/ → exploratory analysis  
dashboard/ → analytics dashboards

## Data Source

The dataset used in this project comes from the UCI Machine Learning Repository.

Online Retail Dataset:
https://archive.ics.uci.edu/ml/datasets/online+retail

The raw dataset contains transactional records from a UK-based online retail store between 2010 and 2011.

For this project, the dataset was cleaned and transformed into a dimensional analytics model consisting of:

- dim_customers
- dim_products
- fact_payments

### SQL Layer

- `schema.sql` defines the dimensional data model used for analytics
- `analytics_queries.sql` contains KPI and business analysis queries
- `data_quality_checks.sql` includes validation checks for data integrity

### Project Outputs

The Python analytics layer generates the following summary tables:

- `monthly_summary.csv`: monthly revenue, order volume, active customers, and average order value
- `customer_summary.csv`: customer-level spend, order count, units purchased, and purchase history
- `product_summary.csv`: product-level revenue, units sold, and order frequency
- `country_summary.csv`: geographic revenue distribution, customer count, and average order value

### Run the Dashboard

```bash
pip3 install -r requirements.txt
streamlit run dashboard/app.py

## Status

🚧 Project currently in development
