# 获取 Olist 原始数据

运行 `python scripts/download_data.py` 从 Olist 的 Kaggle 下载接口取得原始压缩包 `olist-v2.zip`。当前已核验版本为 44,717,580 字节，解压后九个 CSV 共 126,186,995 字节。仓库保存来源链接和哈希，不在 Git 历史中重复存放大型原始包；下载脚本只依赖 Python 标准库。2026-10-25 已验证该公开接口可直接下载。

接着运行 `python scripts/extract_data.py`，CSV 出现在 `data/raw/`。下载时验证压缩包 SHA-256；解压时再验证 ZIP、九个文件的哈希。遇到已被修改的原件会停止。

| 文件 | 行数 | 列数 |
|---|---:|---:|
| olist_orders_dataset.csv | 99,441 | 8 |
| olist_order_items_dataset.csv | 112,650 | 7 |
| olist_customers_dataset.csv | 99,441 | 5 |
| olist_order_payments_dataset.csv | 103,886 | 5 |
| olist_order_reviews_dataset.csv | 99,224 | 7 |
| olist_products_dataset.csv | 32,951 | 9 |
| olist_sellers_dataset.csv | 3,095 | 4 |
| olist_geolocation_dataset.csv | 1,000,163 | 5 |
| product_category_name_translation.csv | 71 | 2 |

来源：[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)，发布者Olist；下载于2026-09-30，API版本2。平台更新日不等于业务发生时间，数据反映2016–2018年。

许可：**CC BY-NC-SA 4.0**，[许可摘要](https://creativecommons.org/licenses/by-nc-sa/4.0/)。本项目不修改下载的原始包。重新分享或衍生使用请保留来源、注明改变，并遵守非商业及相同方式共享条件。每个文件的 SHA-256 在 [source-manifest.json](source-manifest.json)。

完整字段解释见 [九表说明](../docs/02-data-guide.md)。匿名买家编号不能用于识别或联系现实中的个人；公开研究数据不等于真实营销联系名单。
