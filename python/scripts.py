# # scripts/run_analysis.py

# import pandas as pd
# import numpy as np
# from sqlalchemy import create_engine
# import matplotlib.pyplot as plt
# import seaborn as sns


# engine = create_engine('postgresql+psycopg2://nana:Ha-KI-248@localhost:5432/ecommerce_analytics')



# customers = pd.read_sql("SELECT * FROM customers", engine)
# orders = pd.read_sql("SELECT * FROM orders", engine)
# order_items = pd.read_sql("SELECT * FROM order_items", engine)
# products = pd.read_sql("SELECT * FROM products", engine)
# customer_rfm = pd.read_sql("SELECT * FROM customer_rfm", engine)


# df = orders.merge(order_items, on='order_id').merge(products, on='product_id')


# # RFM: Recency, Frequency, Monetary
# # --------------------------
# rfm = df.groupby('customer_id').agg(
#     last_purchase=('order_purchase_timestamp', 'max'),
#     frequency=('order_id', 'count'),
#     monetary=('price', 'sum')
# ).reset_index()
# rfm['recency_days'] = (pd.Timestamp('today') - pd.to_datetime(rfm['last_purchase'])).dt.days


# rfm['recency_score'] = pd.qcut(rfm['recency_days'], 4, labels=[4,3,2,1])
# rfm['frequency_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 4, labels=[1,2,3,4])
# rfm['monetary_score'] = pd.qcut(rfm['monetary'], 4, labels=[1,2,3,4])
# rfm['RFM_score'] = rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(str)

# # --------------------------
# # RFM classes
# # --------------------------
# def assign_segment(row):
#     if row['monetary'] > 1000 and row['frequency'] > 5 and row['recency_days'] <= 90:
#         return 'VIP'
#     elif row['monetary'] > 500:
#         return 'High Potential'
#     elif row['recency_days'] > 180:
#         return 'At Risk'
#     else:
#         return 'Regular'

# rfm['segment'] = rfm.apply(assign_segment, axis=1)

# # Amount of customers in each segment
# segment_counts = rfm['segment'].value_counts()
# print(segment_counts)

# # Revenue 

# revenue_by_category = df.groupby('product_category_name').agg(
#     total_revenue=('price', 'sum'),
#     units_sold=('order_id', 'count'),
#     avg_order_value=('price', 'mean')
# ).reset_index()

# revenue_by_category['revenue_pct'] = revenue_by_category['total_revenue'] / revenue_by_category['total_revenue'].sum() * 100

# # --------------------------
# # ABC Product Analysis
# # --------------------------
# revenue_by_category = revenue_by_category.sort_values('total_revenue', ascending=False)
# revenue_by_category['cum_revenue_pct'] = revenue_by_category['total_revenue'].cumsum() / revenue_by_category['total_revenue'].sum() * 100

# def abc_class(pct):
#     if pct <= 80:
#         return 'A'
#     elif pct <= 95:
#         return 'B'
#     else:
#         return 'C'

# revenue_by_category['ABC_class'] = revenue_by_category['cum_revenue_pct'].apply(abc_class)
# revenue_by_category.to_csv('data/processed/revenue_by_category_abc.csv', index=False)
# avg_order_per_customer = df.groupby('customer_id').agg(
#     avg_order_value=('price', 'mean'),
#     total_orders=('order_id', 'count'),
#     total_revenue=('price', 'sum')
# ).reset_index()

# # Select high potential customers
# high_potential_customers = customer_rfm[customer_rfm['segment'] == 'High Potential']
# hp_ids = high_potential_customers['customer_id'].tolist()

# # Orders from high potential customers
# df_hp = df[df['customer_id'].isin(hp_ids)]

# # Revenue by Product Category - High Potential
# revenue_by_category_hp = df_hp.groupby('product_category_name').agg(
#     total_revenue=('price', 'sum'),
#     units_sold=('order_id', 'count'),
#     avg_order_value=('price', 'mean')
# ).reset_index()

# # ABC classification
# revenue_by_category_hp = revenue_by_category_hp.sort_values('total_revenue', ascending=False)
# revenue_by_category_hp['cum_revenue_pct'] = revenue_by_category_hp['total_revenue'].cumsum() / revenue_by_category_hp['total_revenue'].sum() * 100

# def abc_class(pct):
#     if pct <= 80:
#         return 'A'
#     elif pct <= 95:
#         return 'B'
#     else:
#         return 'C'

# revenue_by_category_hp['ABC_class'] = revenue_by_category_hp['cum_revenue_pct'].apply(abc_class)

# # --------------------------
# # VISUALIZATIONS
# # --------------------------
# import matplotlib.ticker as mtick

# sns.set(style="whitegrid")

# # Revenue by Category - Barplot
# plt.figure(figsize=(12, max(6, len(revenue_by_category_hp)//2)))  # подстраиваем высоту
# sns.barplot(
#     data=revenue_by_category_hp,
#     x='product_category_name',
#     y='total_revenue',
#     hue='ABC_class',
#     palette='Set2'
# )
# plt.xticks(rotation=90)
# plt.title('High Potential Customers - Revenue by Product Category (ABC)')
# plt.ylabel('Total Revenue')
# plt.xlabel('Product Category')
# plt.legend(title='ABC Class', bbox_to_anchor=(1.05, 1), loc='upper left')
# plt.tight_layout()
# plt.savefig('data/processed/plot_revenue_category_hp.png')
# plt.close()

# # Average Order Value - Histogram
# avg_order_hp = df_hp.groupby('customer_id').agg(avg_order_value=('price', 'mean')).reset_index()
# plt.figure(figsize=(10,6))
# sns.histplot(avg_order_hp['avg_order_value'], bins=30, kde=True)
# plt.title('High Potential Customers - Distribution of Average Order Value')
# plt.xlabel('Average Order Value')
# plt.ylabel('Number of Customers')
# plt.tight_layout()
# plt.savefig('data/processed/plot_avg_order_hp.png')
# plt.close()

# # RFM Scatter (Frequency vs Monetary) - High Potential
# rfm_hp = high_potential_customers.copy()
# rfm_hp = rfm_hp.merge(df_hp.groupby('customer_id').agg(frequency=('order_id','count'), monetary=('price','sum')).reset_index(), on='customer_id', how='left')

# plt.figure(figsize=(10,6))
# sns.scatterplot(data=rfm_hp, x='frequency', y='monetary', hue='segment', palette='Set1', alpha=0.7)
# plt.yscale('log')
# plt.title('High Potential Customers - RFM Scatter (Frequency vs Monetary)')
# plt.xlabel('Frequency')
# plt.ylabel('Monetary (log)')
# plt.legend(title='Segment')
# plt.tight_layout()
# plt.savefig('data/processed/plot_rfm_scatter_hp.png')
# plt.close()

# # Monthly Revenue Growth - High Potential
# df_hp['month'] = df_hp['order_purchase_timestamp'].dt.to_period('M')
# monthly_agg_hp = df_hp.groupby('month').agg(
#     revenue=('price','sum'),
#     orders=('order_id','count')
# ).reset_index()
# monthly_agg_hp['revenue_growth_pct'] = monthly_agg_hp['revenue'].pct_change() * 100
# monthly_agg_hp['month_dt'] = monthly_agg_hp['month'].dt.to_timestamp()

# plt.figure(figsize=(12,6))
# sns.lineplot(data=monthly_agg_hp, x='month_dt', y='revenue_growth_pct', marker='o')
# plt.title('High Potential Customers - Monthly Revenue Growth (%)')
# plt.ylabel('Growth %')
# plt.xlabel('Month')
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.savefig('data/processed/plot_monthly_growth_hp.png')
# plt.close()

# # Growth rates 
# # --------------------------
# df['month'] = df['order_purchase_timestamp'].dt.to_period('M')
# monthly_agg = df.groupby('month').agg(
#     revenue=('price', 'sum'),
#     orders=('order_id', 'count')
# ).reset_index()
# monthly_agg['revenue_growth_pct'] = monthly_agg['revenue'].pct_change() * 100

# monthly_agg['month_dt'] = monthly_agg['month'].dt.to_timestamp()

# # --------------------------
# # Cohort Analysis based on the months of the first order
# # --------------------------
# df['order_month'] = df['order_purchase_timestamp'].dt.to_period('M')
# first_order = df.groupby('customer_id')['order_purchase_timestamp'].min().dt.to_period('M').reset_index()
# first_order.columns = ['customer_id', 'first_order_month']

# df = df.merge(first_order, on='customer_id', how='left')
# cohorts = df.groupby(['first_order_month', 'order_month'])['customer_id'].nunique().reset_index()
# cohorts['retention_rate'] = cohorts.groupby('first_order_month')['customer_id'].transform(lambda x: x / x.max())





# cohorts.to_csv('data/processed/cohort_analysis.csv', index=False)

# rfm.to_csv('data/processed/rfm.csv', index=False)
# revenue_by_category.to_csv('data/processed/revenue_by_category.csv', index=False)
# avg_order_per_customer.to_csv('data/processed/avg_order_per_customer.csv', index=False)
# monthly_agg.to_csv('data/processed/monthly_growth.csv', index=False)


# sns.set(style="whitegrid")

# # Scatterplot RFM: Frequency vs Monetary 
# plt.figure(figsize=(16,8))
# sns.scatterplot(
#     data=rfm,
#     x='frequency', 
#     y='monetary', 
#     hue='RFM_score', 
#     palette='tab10', 
#     alpha=0.7
# )
# plt.yscale('log')
# plt.title('RFM: Frequency vs Monetary (log scale)')
# plt.xlabel('Frequency')
# plt.ylabel('Monetary (log)')
# plt.legend(title='RFM Score', bbox_to_anchor=(1.05, 1), loc='upper left')
# plt.savefig('data/processed/plot_rfm_scatter.png')
# plt.close()

# # Heatmap RFM
# rfm_pivot = rfm.pivot_table(index='recency_score', columns='frequency_score', values='monetary', aggfunc='mean')
# fig, ax = plt.subplots(constrained_layout=True)
# sns.heatmap(rfm_pivot, annot=True, fmt=".0f", cmap="YlGnBu", cbar_kws={'label':'Average Monetary'})
# plt.title('RFM Heatmap (Monetary by Recency & Frequency)')

# plt.savefig('data/processed/plot_rfm_heatmap.png')
# plt.close()

# # Revenue by category - barplot 
# # plt.figure(figsize=(9,6))
# # sns.barplot(
# #     data=revenue_by_category.sort_values('total_revenue', ascending=False),
# #     x='product_category_name', 
# #     y='total_revenue', 
# #     hue='ABC_class',
# #     palette='Set2'
# # )
# # plt.xticks(rotation=90)
# # plt.title('Revenue by Product Category (ABC Classification)')
# # plt.ylabel('Total Revenue')
# # plt.xlabel('Product Category')
# # plt.legend(title='ABC Class', bbox_to_anchor=(1.05, 1), loc='upper left')
# # plt.savefig('data/processed/plot_revenue_category.png')
# # plt.close()
# import matplotlib.pyplot as plt
# import seaborn as sns


# num_categories = revenue_by_category['product_category_name'].nunique()
# fig_width = max(9, num_categories * 0.5) 


# fig, ax = plt.subplots(figsize=(fig_width, 6), constrained_layout=True)


# sns.barplot(
#     data=revenue_by_category.sort_values('total_revenue', ascending=False),
#     x='product_category_name',
#     y='total_revenue',
#     hue='ABC_class',
#     palette='Set2',
#     ax=ax
# )


# ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
# ax.set_title('Revenue by Product Category (ABC Classification)')
# ax.set_ylabel('Total Revenue')
# ax.set_xlabel('Product Category')


# ax.legend(title='ABC Class', bbox_to_anchor=(1.05, 1), loc='upper left')


# plt.savefig('data/processed/plot_revenue_category.png', bbox_inches='tight')
# plt.close()

# #  Average order per customer - histogram
# fig, ax = plt.subplots(constrained_layout=True)
# sns.histplot(avg_order_per_customer['avg_order_value'], bins=50, kde=True)
# plt.title('Distribution of Average Order Value per Customer')
# plt.xlabel('Average Order Value')
# plt.ylabel('Number of Customers')

# plt.savefig('data/processed/plot_avg_order_hist.png')
# plt.close()

# #  Monthly revenue heatmap
# monthly_pivot = monthly_agg.pivot_table(index='month', values='revenue')
# fig, ax = plt.subplots(constrained_layout=True)
# sns.heatmap(monthly_pivot, annot=True, fmt=".0f", cmap="YlGnBu")
# plt.title('Monthly Revenue Heatmap')

# plt.savefig('data/processed/plot_monthly_heatmap.png')
# plt.close()

# #  Monthly revenue growth - lineplot
# fig, ax = plt.subplots(constrained_layout=True)
# sns.lineplot(data=monthly_agg, x='month_dt', y='revenue_growth_pct', marker='o')
# plt.title('Monthly Revenue Growth (%)')
# plt.ylabel('Growth %')
# plt.xlabel('Month')
# plt.xticks(rotation=45)

# plt.savefig('data/processed/plot_monthly_growth.png')
# plt.close()

# # --------------------------
# # VIP vs Other Segments Revenue
# plt.figure(figsize=(15,6))
# sns.barplot(
#     x='segment', 
#     y='monetary', 
#     data=rfm.groupby('segment')['monetary'].sum().reset_index(),
#     palette='Set2'
# )
# plt.title('Revenue Contribution by Customer Segment')
# plt.ylabel('Total Revenue')
# plt.xlabel('Segment')
# plt.legend(title='Segment', bbox_to_anchor=(1.05, 1), loc='upper left')

# plt.savefig('data/processed/plot_segment_revenue.png')
# plt.close()




# # --------------------------
# # Load High Potential customers
# # --------------------------
# high_pot_df = pd.read_sql("""
#     SELECT c.customer_id, o.order_id, oi.price, p.product_category_name
#     FROM customer_rfm c
#     JOIN orders o ON c.customer_id = o.customer_id
#     JOIN order_items oi ON o.order_id = oi.order_id
#     JOIN products p ON oi.product_id = p.product_id
#     WHERE c.segment = 'High Potential';
# """, engine)

# if high_pot_df.empty:
#     print("No High Potential customers found.")
#     exit()

# # --------------------------
# # Aggregate metrics
# # --------------------------
# agg_df = high_pot_df.groupby('customer_id').agg(
#     total_orders=('order_id', 'nunique'),
#     total_revenue=('price', 'sum'),
#     avg_order_value=('price', 'mean')
# ).reset_index()

# print(agg_df.describe())

# # --------------------------
# # Plot settings
# # --------------------------
# sns.set(style="whitegrid")

# # Average Order Value distribution
# plt.figure(figsize=(10,6))
# sns.histplot(agg_df['avg_order_value'], bins=50, kde=True, color='skyblue')
# plt.title('High Potential Customers: Avg Order Value Distribution')
# plt.xlabel('Average Order Value')
# plt.ylabel('Number of Customers')
# plt.tight_layout()
# plt.savefig('data/processed/high_potential_avg_order_value.png')
# plt.close()

# # Total Revenue distribution
# plt.figure(figsize=(10,6))
# sns.histplot(agg_df['total_revenue'], bins=50, kde=True, color='orange')
# plt.title('High Potential Customers: Total Revenue Distribution')
# plt.xlabel('Total Revenue')
# plt.ylabel('Number of Customers')
# plt.tight_layout()
# plt.savefig('data/processed/high_potential_total_revenue.png')
# plt.close()

# # Total Orders distribution
# plt.figure(figsize=(10,6))
# sns.histplot(agg_df['total_orders'], bins=20, kde=False, color='green')
# plt.title('High Potential Customers: Total Orders Distribution')
# plt.xlabel('Total Orders')
# plt.ylabel('Number of Customers')
# plt.tight_layout()
# plt.savefig('data/processed/high_potential_total_orders.png')
# plt.close()

# # Revenue by Product Category
# category_df = high_pot_df.groupby('product_category_name').agg(
#     total_revenue=('price', 'sum'),
#     units_sold=('order_id', 'count')
# ).reset_index().sort_values('total_revenue', ascending=False)

# plt.figure(figsize=(12,6))
# sns.barplot(
#     data=category_df,
#     x='product_category_name',
#     y='total_revenue',
#     palette='Set2'
# )
# plt.xticks(rotation=90)
# plt.title('High Potential Customers: Revenue by Product Category')
# plt.xlabel('Product Category')
# plt.ylabel('Total Revenue')
# plt.tight_layout()
# plt.savefig('data/processed/high_potential_revenue_by_category.png')
# plt.close()

# print("High Potential analysis completed. Plots saved in data/processed/")




# scripts/run_analysis.py

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------
# DB Connection
# --------------------------
engine = create_engine('postgresql+psycopg2://nana:Ha-KI-248@localhost:5432/ecommerce_analytics')

# --------------------------
# Load tables
# --------------------------
customers = pd.read_sql("SELECT * FROM customers", engine)
orders = pd.read_sql("SELECT * FROM orders", engine)
order_items = pd.read_sql("SELECT * FROM order_items", engine)
products = pd.read_sql("SELECT * FROM products", engine)
customer_rfm = pd.read_sql("SELECT * FROM customer_rfm", engine)

# Merge orders + items + products
df = orders.merge(order_items, on='order_id').merge(products, on='product_id')

# --------------------------
# RFM Metrics
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

# --------------------------
# Assign customer segments
# --------------------------
def assign_segment(row):
    if row['monetary'] > 1000 and row['frequency'] > 5 and row['recency_days'] <= 90:
        return 'VIP'
    elif row['monetary'] > 500:
        return 'High Potential'
    elif row['recency_days'] > 180:
        return 'At Risk'
    else:
        return 'Regular'

rfm['segment'] = rfm.apply(assign_segment, axis=1)

print("Customer segments counts:")
print(rfm['segment'].value_counts())

# --------------------------
# Revenue by product category
# --------------------------
revenue_by_category = df.groupby('product_category_name').agg(
    total_revenue=('price', 'sum'),
    units_sold=('order_id', 'count'),
    avg_order_value=('price', 'mean')
).reset_index()

revenue_by_category = revenue_by_category.sort_values('total_revenue', ascending=False)
revenue_by_category['cum_revenue_pct'] = revenue_by_category['total_revenue'].cumsum() / revenue_by_category['total_revenue'].sum() * 100

def abc_class(pct):
    if pct <= 80:
        return 'A'
    elif pct <= 95:
        return 'B'
    else:
        return 'C'

revenue_by_category['ABC_class'] = revenue_by_category['cum_revenue_pct'].apply(abc_class)

# --------------------------
# High Potential Customers Analysis
# --------------------------
high_potential = rfm[rfm['segment'] == 'High Potential']
hp_ids = high_potential['customer_id'].tolist()
df_hp = df[df['customer_id'].isin(hp_ids)]

# Aggregate metrics for High Potential
agg_hp = df_hp.groupby('customer_id').agg(
    total_orders=('order_id','nunique'),
    total_revenue=('price','sum'),
    avg_order_value=('price','mean'),
    frequency=('order_id','count'),
    monetary=('price','sum')
).reset_index()

# Revenue by category High Potential
revenue_by_category_hp = df_hp.groupby('product_category_name').agg(
    total_revenue=('price','sum'),
    units_sold=('order_id','count'),
    avg_order_value=('price','mean')
).reset_index().sort_values('total_revenue', ascending=False)
revenue_by_category_hp['cum_revenue_pct'] = revenue_by_category_hp['total_revenue'].cumsum() / revenue_by_category_hp['total_revenue'].sum() * 100
revenue_by_category_hp['ABC_class'] = revenue_by_category_hp['cum_revenue_pct'].apply(abc_class)

# --------------------------
# VISUALIZATIONS
# --------------------------
sns.set(style="whitegrid")

# High Potential Revenue by Category
plt.figure(figsize=(12, max(6, len(revenue_by_category_hp)//2)))
sns.barplot(
    data=revenue_by_category_hp,
    x='product_category_name',
    y='total_revenue',
    hue='ABC_class',
    palette='Set2'
)
plt.xticks(rotation=90)
plt.title('High Potential Customers - Revenue by Product Category (ABC)')
plt.ylabel('Total Revenue')
plt.xlabel('Product Category')
plt.legend(title='ABC Class', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('data/processed/plot_revenue_category_hp.png')
plt.close()

# High Potential Avg Order Value Distribution
plt.figure(figsize=(10,6))
sns.histplot(agg_hp['avg_order_value'], bins=30, kde=True, color='skyblue')
plt.title('High Potential Customers - Avg Order Value')
plt.xlabel('Average Order Value')
plt.ylabel('Number of Customers')
plt.tight_layout()
plt.savefig('data/processed/plot_avg_order_hp.png')
plt.close()

# High Potential RFM Scatter (Frequency vs Monetary)
plt.figure(figsize=(10,6))
sns.scatterplot(
    data=agg_hp,
    x='frequency',
    y='monetary',
    hue='total_revenue',  # Можно заменить на segment, но все High Potential
    palette='Reds',
    alpha=0.7
)
plt.yscale('log')
plt.title('High Potential Customers - RFM Scatter')
plt.xlabel('Frequency')
plt.ylabel('Monetary (log)')
plt.tight_layout()
plt.savefig('data/processed/plot_rfm_scatter_hp.png')
plt.close()

# High Potential Monthly Revenue Growth
df_hp['month'] = df_hp['order_purchase_timestamp'].dt.to_period('M')
monthly_hp = df_hp.groupby('month').agg(revenue=('price','sum')).reset_index()
monthly_hp['revenue_growth_pct'] = monthly_hp['revenue'].pct_change() * 100
monthly_hp['month_dt'] = monthly_hp['month'].dt.to_timestamp()

plt.figure(figsize=(12,6))
sns.lineplot(data=monthly_hp, x='month_dt', y='revenue_growth_pct', marker='o')
plt.title('High Potential Customers - Monthly Revenue Growth (%)')
plt.ylabel('Growth %')
plt.xlabel('Month')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('data/processed/plot_monthly_growth_hp.png')
plt.close()

print("High Potential analysis completed. Plots saved in data/processed/")