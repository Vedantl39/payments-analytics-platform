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

## Status

🚧 Project currently in development
