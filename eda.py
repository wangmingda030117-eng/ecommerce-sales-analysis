import pandas as pd
import matplotlib.pyplot as plt
orders = pd.read_csv(r"C:\Users\wmdgod\Desktop\DA练习\电商分析\data\olist_orders_dataset.csv")
customers = pd.read_csv(r"C:\Users\wmdgod\Desktop\DA练习\电商分析\data\olist_customers_dataset.csv")
order_items = pd.read_csv(r"C:\Users\wmdgod\Desktop\DA练习\电商分析\data\olist_order_items_dataset.csv")

orders = orders.drop_duplicates()
customers = customers.drop_duplicates()
order_items = order_items.drop_duplicates()


orders = orders[orders["order_status"] == "delivered"]


print("Orders missing values:")
print(orders.isnull().sum())

print("Customers missing values:")
print(customers.isnull().sum())

print("Order items missing values:")
print(order_items.isnull().sum())
print("orders:", orders.shape)
print("customers:", customers.shape)
print("order_items:", order_items.shape)

print(orders.columns)
print(customers.columns)
print(order_items.columns)
order_items["sales"] = order_items["price"] + order_items["freight_value"]

order_sales = order_items.groupby("order_id")["sales"].sum().reset_index()

print(order_sales.head())
orders_sales = orders.merge(order_sales, on="order_id")

print(orders_sales.head())
orders_sales["order_purchase_timestamp"] = pd.to_datetime(
    orders_sales["order_purchase_timestamp"]
)

orders_sales["order_date"] = orders_sales["order_purchase_timestamp"].dt.date

daily_sales = orders_sales.groupby("order_date")["sales"].sum()

daily_sales.plot(figsize=(12,5), title="Daily Sales Trend")
plt.show()
daily_orders = orders_sales.groupby("order_date")["order_id"].count()

daily_orders.plot(figsize=(12,5), title="Daily Orders Trend")

plt.show()
orders_sales["order_month"] = orders_sales["order_purchase_timestamp"].dt.to_period("M")

monthly_sales = orders_sales.groupby("order_month")["sales"].sum()

monthly_sales.plot(figsize=(12,5), title="Monthly Sales Trend")

plt.show()
products = pd.read_csv(r"C:\Users\wmdgod\Desktop\DA练习\电商分析\data\olist_products_dataset.csv")
product_sales = order_items.groupby("product_id")["sales"].sum().reset_index()

product_sales = product_sales.sort_values("sales", ascending=False)

print(product_sales.head(10))
top_products = product_sales.head(10)

top_products.plot.bar(x="product_id", y="sales", figsize=(12,5), title="Top 10 Products")

plt.show()
orders_customer = orders.merge(customers, on="customer_id")

orders_sales_customer = orders_customer.merge(order_sales, on="order_id")
city_sales = orders_sales_customer.groupby("customer_city")["sales"].sum().sort_values(ascending=False)

city_sales.head(10).plot.bar(figsize=(12,5), title="Top Cities by Sales")

plt.show()
orders_customer = orders.merge(customers, on="customer_id")

orders_sales_customer = orders_customer.merge(order_sales, on="order_id")
customer_orders = orders_sales_customer.groupby("customer_unique_id")["order_id"].count()

repeat_rate = (customer_orders > 1).mean()


print(f"Repeat Purchase Rate: {repeat_rate:.2%}")
orders_sales_customer["order_purchase_timestamp"] = pd.to_datetime(
    orders_sales_customer["order_purchase_timestamp"]
)
snapshot_date = orders_sales_customer["order_purchase_timestamp"].max()
rfm = orders_sales_customer.groupby("customer_unique_id").agg({
    "order_purchase_timestamp": lambda x: (snapshot_date - x.max()).days,
    "order_id": "count",
    "sales": "sum"
})
rfm.columns = ["Recency", "Frequency", "Monetary"]
print(rfm.head())
rfm["R_score"] = pd.qcut(rfm["Recency"], 5, labels=[5,4,3,2,1])
rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1,2,3,4,5])
rfm["M_score"] = pd.qcut(rfm["Monetary"], 5, labels=[1,2,3,4,5])
rfm["RFM_score"] = rfm["R_score"].astype(str) + rfm["F_score"].astype(str) + rfm["M_score"].astype(str)
def segment(row):
    if row["R_score"] == 5 and row["F_score"] == 5:
        return "VIP"
    elif row["R_score"] >= 4:
        return "Loyal"
    elif row["R_score"] <= 2:
        return "Churn Risk"
    else:
        return "Normal"
rfm["Segment"] = rfm.apply(segment, axis=1)
print(rfm["Segment"].value_counts())
segment_counts = rfm["Segment"].value_counts()

order = ["VIP", "Loyal", "Normal", "Churn Risk"]

segment_counts = segment_counts.reindex(order)

segment_counts.plot.bar(
    figsize=(10,5),
    title="Customer Segmentation"
)

plt.show()