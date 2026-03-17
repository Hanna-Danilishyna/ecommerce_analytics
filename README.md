Ecommerce Analytics Project

Project: End-to-End E-commerce Sales & Customer Analytics (Olist Dataset)
Tech Stack: PostgreSQL, Python (pandas, SQLAlchemy, matplotlib, seaborn)
Dataset: Olist Brazilian E-commerce Public Dataset

Project Overview
---------------------------
This project demonstrates a complete data analytics workflow:

- Designing and building a relational database in PostgreSQL

- Performing SQL exploratory data analysis (EDA)

- Conducting advanced analytics in Python

- Preparing data for business dashboards in Tableau

The goal is to simulate a real-world data analyst workflow and generate actionable business insights from raw transactional data.

Business Objectives
---------------------------

- Analyze overall sales performance

- Identify top-performing product categories and products

- Segment customers using RFM (Recency, Frequency, Monetary)

- Measure revenue growth over time

- Evaluate customer behavior and average order value

- Prepare structured datasets for dashboard visualization

Project Architecture
---------------------------

CSV files
→ PostgreSQL (normalized schema with primary & foreign keys)
→ SQL EDA
→ Python analytics (RFM, growth, percentiles)
→ Processed CSV export
→ Tableau Dashboard

Database Schema
---------------------------

The following tables were created in PostgreSQL:

customers

sellers

products

orders

order_items

payments

geolocation



Relationships include:

orders.customer_id → customers.customer_id

order_items.order_id → orders.order_id

order_items.product_id → products.product_id

order_items.seller_id → sellers.seller_id

payments.order_id → orders.order_id

Primary and foreign keys ensure referential integrity.


SQL Analysis
---------------------------

Key SQL analyses performed:

- Dataset overview (total records, customers, products, date range, total revenue)

- Revenue distribution by product category

- Top-performing products by revenue and units sold

- Monthly revenue and order trends

- Geographic revenue distribution by state

- Revenue contribution percentages using window function



Advanced SQL features used:
---------------------------

- CTEs

- Aggregations

- Date truncation



Python Analysis
---------------------------

Using pandas and SQLAlchemy:

- Imported and cleaned CSV data

- Calculated RFM metrics per customer

- Computed revenue by category

- Calculated average order value per customer

- Computed monthly revenue growth rates

- Calculated percentiles for customer segmentation


Visualizations created:
----------------------------

- Scatterplots (Frequency vs Monetary)

- Heatmaps (RFM segmentation)

- Barplots (Revenue by category)

- Line plots (Revenue growth trends)



Project Structure
```
ecommerce_analytics/

data/
  raw/ — original CSV files
  processed/ — cleaned and aggregated CSV files

sql/
    01_data_overview.sql
    02_sales_by_category.sql
    03_temporal_patterns.sql
    04_top_products.sql
    05_customer_rfm.sql
    06_geography.sql



python/
    scripts.py
    01_create_table.py


README.md
```
How to Run the Project
1. Clone the repository

git clone <YOUR_REPOSITORY_URL>
cd ecommerce_analytics

2️. Install dependencies

pip install pandas sqlalchemy psycopg2-binary matplotlib seaborn

3️. Create PostgreSQL database

Run inside psql:

CREATE USER nana WITH PASSWORD 'your_password';
CREATE DATABASE ecommerce_analytics;
GRANT ALL PRIVILEGES ON DATABASE ecommerce_analytics TO nana;

4️. Run Python script

01_create_table.py

This will:

- - Create tables (if not existing)

Load CSV data

python python/scripts.py

- Clean missing values

- Compute analytics

- Export processed datasets

Tableau Dashboard

Processed CSV files can be uploaded into Tableau Public to build:

- RFM customer segmentation dashboard

- Revenue by category visualization

- Monthly growth trends

- Geographic revenue maps


Skills Demonstrated

- Relational database design

- SQL 

- Data cleaning and transformation

- Customer segmentation (RFM)

- Revenue growth analysis

- Data visualization

- End-to-end analytics workflow



License
------------------

This project is for educational and portfolio purposes.
