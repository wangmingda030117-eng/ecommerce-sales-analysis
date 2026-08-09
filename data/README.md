# 数据说明

原始数据不会提交到 GitHub。请从 [Kaggle：Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) 下载数据，并将以下五个文件放入 `data/raw/`：

```text
data/raw/
├── olist_orders_dataset.csv
├── olist_order_items_dataset.csv
├── olist_customers_dataset.csv
├── olist_products_dataset.csv
└── product_category_name_translation.csv
```

本项目没有使用支付、评价、卖家或地理坐标文件。数据使用范围和授权条件以原始数据发布页为准。

运行以下命令生成 Tableau 数据源：

```bash
python src/prepare_dashboard_data.py --data-dir data/raw --output-dir outputs/tableau
```

请勿将下载的原始 CSV、压缩包或包含个人敏感信息的数据提交到仓库。
