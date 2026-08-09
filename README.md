# Olist 电商销售看板｜数据准备与 Tableau 可视化

这是一个面向业务分析场景的 Olist 巴西电商项目：使用 Python 将订单、商品、客户与品类数据整理为可复现的分析表，再在 Tableau 中观察销售趋势、区域分布、品类结构与客户表现。

> Tableau Public：[查看销售看板](https://public.tableau.com/app/profile/mingda.wang/viz/OlistE-commerceDashboard_17764859070030/1?publish=yes)

## 项目目标

- 建立统一、可复现的 Tableau 数据准备流程；
- 区分商品成交金额、运费与含运费订单金额，避免口径混用；
- 从时间、州、品类和客户四个维度输出可直接连接 Tableau 的分析表；
- 在没有原始数据和计算结果佐证时，不写入无法复核的数值结论。

## 指标口径

| 指标 | 定义 | 说明 |
| --- | --- | --- |
| `merchandise_value` | `sum(price)` | 商品成交金额，不含运费；不能直接等同于平台收入或利润 |
| `freight_value` | `sum(freight_value)` | 订单商品行对应的运费 |
| `gross_order_value` | `merchandise_value + freight_value` | 本项目可观察到的含运费订单金额；不包含优惠券、支付分期等支付表信息 |
| `orders` | `nunique(order_id)` | 去重订单数 |
| `customers` | `nunique(customer_unique_id)` | 去重客户数 |
| `avg_gross_order_value_per_order` | `gross_order_value / orders` | 每单平均含运费金额 |

分析范围默认限定为 `order_status == "delivered"` 的订单，并使用 `order_purchase_timestamp` 归属月份。这个筛选规则写在脚本中，方便审阅和复现。

## 数据流程

```text
Olist 原始 CSV
    ├─ orders + order_items
    ├─ customers
    ├─ products
    └─ category translation
             ↓
src/prepare_dashboard_data.py
             ↓
monthly_sales.csv / state_sales.csv / category_sales.csv / customer_summary.csv
             ↓
Tableau Dashboard
```

脚本在合并前检查必需文件、字段、主键唯一性、金额字段与日期字段；合并时使用 pandas 的 `validate` 参数，降低多对多连接导致金额重复计算的风险。

## 快速开始

1. 从 [Kaggle：Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) 下载原始 CSV，并按 [data/README.md](data/README.md) 放置文件。
2. 创建环境并安装依赖：

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. 生成 Tableau 数据源：

```bash
python src/prepare_dashboard_data.py --data-dir data/raw --output-dir outputs/tableau
```

脚本运行成功后会在输出目录生成：

| 文件 | 粒度 | 主要用途 |
| --- | --- | --- |
| `monthly_sales.csv` | 月 | 销售趋势、订单量、客单表现 |
| `state_sales.csv` | 客户州 | 区域规模与金额结构 |
| `category_sales.csv` | 英文品类 | 品类结构与贡献分析 |
| `customer_summary.csv` | 唯一客户 | 购买频次、最近购买、客户价值分层 |

## 仓库结构

```text
.
├── data/
│   └── README.md
├── src/
│   └── prepare_dashboard_data.py
├── .gitignore
├── README.md
└── requirements.txt
```

## 方法边界

- 数据为公开历史样本，结果不能直接外推到当前电商市场。
- `gross_order_value` 是本项目根据商品价格与运费构造的分析口径，不代表 Olist 的会计收入、利润或实际支付金额。
- 仓库中的技术栈只列出已提供并可审阅的 Python 数据准备与 Tableau 可视化流程。

## 技术栈

Python · pandas · Tableau
