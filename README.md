# 电商销售数据分析（E-commerce Sales Analysis）

本项目基于 **Olist Brazilian E-commerce Dataset**，使用 Python 对电商订单数据进行清洗、分析与可视化，探索平台销售趋势以及用户价值，并通过 **RFM 模型**进行用户分群。

---

## 项目目标

- 分析平台销售额随时间的变化趋势
- 识别销售额最高的商品
- 分析不同城市的销售贡献
- 通过 RFM 模型对用户进行价值分群

---

## 数据来源

Olist Brazilian E-commerce Dataset  
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

使用数据表包括：

- orders
- customers
- order_items
- products

---

## 分析内容

### 1 数据清洗
- 使用 **Pandas** 对多个数据表进行清洗与整合
- 去除重复值
- 处理缺失值
- 合并订单、用户与商品数据

### 2 销售额计算
构建销售额指标：

并计算订单级销售额。

### 3 销售趋势分析

分析：

- 日销售额趋势
- 月销售额趋势

用于观察平台整体销售变化。

### 4 商品销售分析

统计销售额最高的 **Top10 商品**，识别平台热销产品。

### 5 城市销售分析

统计不同城市的销售额贡献，分析销售区域分布。

### 6 用户分群（RFM模型）

构建用户价值模型：

- **Recency**：最近购买时间
- **Frequency**：购买次数
- **Monetary**：消费金额

根据 RFM 评分将用户划分为：

- VIP
- Loyal
- Normal
- Churn Risk

---

## 技术栈

- Python
- Pandas
- Matplotlib

