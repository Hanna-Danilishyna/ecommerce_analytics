# scripts/run_analysis.py

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns


engine = create_engine('postgresql+psycopg2://nana:Ha-KI-248@localhost:5432/ecommerce_analytics')



customers = pd.read_sql("SELECT * FROM customers", engine)
orders = pd.read_sql("SELECT * FROM orders", engine)
order_items = pd.read_sql("SELECT * FROM order_items", engine)
products = pd.read_sql("SELECT * FROM products", engine)



df = orders.merge(order_items, on='order_id').merge(products, on='product_id')


# RFM: Recency, Frequency, Monetary
# --------------------------
rfm = df.groupby('customer_id').agg(
    last_purchase=('order_purchase_timestamp', 'max'),
    frequency=('order_id', 'count'),
    monetary=('price', 'sum')
).reset_index()
rfm['recency_days'] = (pd.Timestamp('today') - pd.to_datetime(rfm['last_purchase'])).dt.days


rfm['recency_score'] = pd.qcut(rfm['recency_days'], 4, labels=[4,3,2,1])
rfm['frequency_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 4, labels=[1,2,3,4])
rfm['monetary_score'] = pd.qcut(rfm['monetary'], 4, labels=[1,2,3,4])
rfm['RFM_score'] = rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(str)


# Revenue 

revenue_by_category = df.groupby('product_category_name').agg(
    total_revenue=('price', 'sum'),
    units_sold=('order_id', 'count'),
    avg_order_value=('price', 'mean')
).reset_index()

revenue_by_category['revenue_pct'] = revenue_by_category['total_revenue'] / revenue_by_category['total_revenue'].sum() * 100


avg_order_per_customer = df.groupby('customer_id').agg(
    avg_order_value=('price', 'mean'),
    total_orders=('order_id', 'count'),
    total_revenue=('price', 'sum')
).reset_index()

# Growth rates 
# --------------------------
df['month'] = df['order_purchase_timestamp'].dt.to_period('M')
monthly_agg = df.groupby('month').agg(
    revenue=('price', 'sum'),
    orders=('order_id', 'count')
).reset_index()
monthly_agg['revenue_growth_pct'] = monthly_agg['revenue'].pct_change() * 100

monthly_agg['month_dt'] = monthly_agg['month'].dt.to_timestamp()


rfm.to_csv('data/processed/rfm.csv', index=False)
revenue_by_category.to_csv('data/processed/revenue_by_category.csv', index=False)
avg_order_per_customer.to_csv('data/processed/avg_order_per_customer.csv', index=False)
monthly_agg.to_csv('data/processed/monthly_growth.csv', index=False)


sns.set(style="whitegrid")

# Scatterplot RFM: Frequency vs Monetary 
plt.figure(figsize=(10,6))
sns.scatterplot(data=rfm, x='frequency', y='monetary', hue='RFM_score', palette='tab10', alpha=0.7)
plt.yscale('log')
plt.title('RFM: Frequency vs Monetary (log scale)')
plt.xlabel('Frequency')
plt.ylabel('Monetary (log)')
plt.savefig('data/processed/plot_rfm_scatter.png')
plt.close()

# Heatmap RFM
rfm_pivot = rfm.pivot_table(index='recency_score', columns='frequency_score', values='monetary', aggfunc='mean')
plt.figure(figsize=(8,6))
sns.heatmap(rfm_pivot, annot=True, fmt=".0f", cmap="YlGnBu")
plt.title('RFM Heatmap (Monetary by Recency & Frequency)')
plt.savefig('data/processed/plot_rfm_heatmap.png')
plt.close()

# Revenue by category - barplot 
plt.figure(figsize=(12,6))
sns.barplot(data=revenue_by_category.sort_values('total_revenue', ascending=False),
            x='product_category_name', y='total_revenue', palette='viridis')
plt.xticks(rotation=90)
plt.title('Revenue by Product Category')
plt.ylabel('Total Revenue')
plt.savefig('data/processed/plot_revenue_category.png')
plt.close()

#  Average order per customer - histogram
plt.figure(figsize=(10,6))
sns.histplot(avg_order_per_customer['avg_order_value'], bins=50, kde=True)
plt.title('Distribution of Average Order Value per Customer')
plt.xlabel('Average Order Value')
plt.ylabel('Number of Customers')
plt.savefig('data/processed/plot_avg_order_hist.png')
plt.close()

#  Monthly revenue heatmap
monthly_pivot = monthly_agg.pivot_table(index='month', values='revenue')
plt.figure(figsize=(12,4))
sns.heatmap(monthly_pivot, annot=True, fmt=".0f", cmap="YlGnBu")
plt.title('Monthly Revenue Heatmap')
plt.savefig('data/processed/plot_monthly_heatmap.png')
plt.close()

#  Monthly revenue growth - lineplot
sns.lineplot(data=monthly_agg, x='month_dt', y='revenue_growth_pct', marker='o')
plt.title('Monthly Revenue Growth (%)')
plt.ylabel('Growth %')
plt.xlabel('Month')
plt.xticks(rotation=45)
plt.savefig('data/processed/plot_monthly_growth.png')
plt.close()
