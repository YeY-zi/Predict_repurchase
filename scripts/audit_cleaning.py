"""Audit the three core Olist tables without changing the raw CSV files."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results" / "cleaning-audit.json"
MANIFEST = json.loads((ROOT / "data" / "source-manifest.json").read_text(encoding="utf-8"))
expected = {record["name"]: record["sha256"] for record in MANIFEST["files"]}
names = ["olist_orders_dataset.csv", "olist_order_items_dataset.csv", "olist_customers_dataset.csv"]
for name in names:
    assert hashlib.sha256((RAW / name).read_bytes()).hexdigest() == expected[name], name

orders = pd.read_csv(RAW / names[0], dtype={"order_id": "string", "customer_id": "string"})
items = pd.read_csv(RAW / names[1], dtype={"order_id": "string", "product_id": "string"})
customers = pd.read_csv(RAW / names[2], dtype={"customer_id": "string", "customer_unique_id": "string"})
approved = pd.to_datetime(orders.order_approved_at, errors="coerce")
purchase = pd.to_datetime(orders.order_purchase_timestamp, errors="coerce")
item_total = items.groupby("order_id", dropna=False).agg(
    amount=("price", "sum"), item_rows=("order_item_id", "size"), freight=("freight_value", "sum")
)
joined = orders.merge(item_total, left_on="order_id", right_index=True, how="left", validate="one_to_one")
joined = joined.merge(
    customers[["customer_id", "customer_unique_id"]], on="customer_id", how="left", validate="many_to_one"
)
eligible = approved.notna() & joined.amount.gt(0) & joined.customer_unique_id.notna()
report = {
    "source": MANIFEST["source_page"],
    "raw_sha256_verified": names,
    "orders_raw": int(len(orders)),
    "items_raw": int(len(items)),
    "customers_raw": int(len(customers)),
    "distinct_order_ids": int(orders.order_id.nunique()),
    "duplicate_order_id_rows": int(orders.order_id.duplicated().sum()),
    "duplicate_customer_id_rows": int(customers.customer_id.duplicated().sum()),
    "missing_or_invalid_purchase_timestamp": int(purchase.isna().sum()),
    "missing_or_invalid_approval_timestamp": int(approved.isna().sum()),
    "orders_without_item_rows": int(joined.item_rows.isna().sum()),
    "orders_with_nonpositive_or_missing_item_amount": int((~joined.amount.gt(0)).sum()),
    "orders_without_customer_match": int(joined.customer_unique_id.isna().sum()),
    "approved_positive_value_orders_used": int(eligible.sum()),
    "orders_not_used_for_approval_based_analysis": int((~eligible).sum()),
    "unique_buyers_in_eligible_orders": int(joined.loc[eligible, "customer_unique_id"].nunique()),
    "rule": "Approved timestamp present, positive sum of item prices, customer match; no final-status filter",
    "raw_files_modified": False,
}
assert report["duplicate_order_id_rows"] == 0
assert report["duplicate_customer_id_rows"] == 0
assert report["approved_positive_value_orders_used"] + report["orders_not_used_for_approval_based_analysis"] == len(orders)
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
