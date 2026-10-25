"""Reproduce the proposal's segment -> EDA -> feature feedback loop.

The 2018-04 cohort was published in an earlier exploratory experiment.  Its
results here are descriptive replication, not a fresh confirmatory holdout.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from threadpoolctl import threadpool_limits

from experiment_common import DATA, ROOT, evaluate, features, hashes, i, orders, test, train, val


OUT = ROOT / "results" / "feedback"
OUT.mkdir(parents=True, exist_ok=True)
SEED = 2026
NUMERIC = features[:-1]
CLUSTER_INPUT = ["R", "F", "M"]


def fit_segments(frame: pd.DataFrame) -> tuple[StandardScaler, KMeans]:
    scaler = StandardScaler().fit(np.log1p(frame[CLUSTER_INPUT]))
    with threadpool_limits(limits=2):
        model = KMeans(n_clusters=4, n_init=20, random_state=SEED).fit(
            scaler.transform(np.log1p(frame[CLUSTER_INPUT]))
        )
    return scaler, model


def assign_segments(frame: pd.DataFrame, scaler: StandardScaler, model: KMeans) -> np.ndarray:
    return model.predict(scaler.transform(np.log1p(frame[CLUSTER_INPUT])))


scaler, clusters = fit_segments(train)
labels = {name: assign_segments(frame, scaler, clusters) for name, frame in
          [("train", train), ("validation", val), ("test", test)]}
stability = []
for repeat in range(5):
    sampled = train.sample(frac=0.8, random_state=repeat)
    alternative_scaler, alternative_model = fit_segments(sampled)
    stability.append(float(adjusted_rand_score(
        labels["validation"], assign_segments(val, alternative_scaler, alternative_model)
    )))
silhouette = float(silhouette_score(
    scaler.transform(np.log1p(val[CLUSTER_INPUT])), labels["validation"],
    sample_size=min(2000, len(val)), random_state=SEED,
))

# The product table and category dictionary are historical product attributes.
# Only items on approved, positive-value orders before each cutoff are used.
product = pd.read_csv(DATA / "olist_products_dataset.csv", usecols=["product_id", "product_category_name"])
translation = pd.read_csv(DATA / "product_category_name_translation.csv")
product = product.merge(translation, on="product_category_name", how="left", validate="many_to_one")
item_categories = i[["order_id", "product_id"]].merge(
    product[["product_id", "product_category_name_english"]],
    on="product_id", how="left", validate="many_to_one",
)


def category_buyers(cutoff: str) -> tuple[pd.DataFrame, int]:
    end = pd.Timestamp(cutoff)
    start = end - pd.DateOffset(months=6)
    eligible = orders.loc[
        orders.order_approved_at.ge(start) & orders.order_approved_at.lt(end),
        ["order_id", "customer_unique_id"],
    ]
    joined = eligible.merge(item_categories, on="order_id", validate="one_to_many")
    unknown = int(joined.product_category_name_english.isna().sum())
    known = joined.dropna(subset=["product_category_name_english"])[
        ["customer_unique_id", "product_category_name_english"]
    ].drop_duplicates()
    return known, unknown


buyer_categories = {}
unknown_category_rows = {}
for phase, date in [("train", "2017-10-01"), ("validation", "2018-01-01"), ("test", "2018-04-01")]:
    buyer_categories[phase], unknown_category_rows[phase] = category_buyers(date)
top_categories = (
    buyer_categories["train"].product_category_name_english.value_counts().head(5).index.tolist()
)
category_columns = [f"category_{j + 1}" for j in range(len(top_categories))]
category_map = dict(zip(category_columns, top_categories))


def model_frame(phase: str, frame: pd.DataFrame) -> pd.DataFrame:
    prepared = frame[features].copy()
    prepared["segment"] = labels[phase].astype(str)
    categories = buyer_categories[phase]
    for column, category in category_map.items():
        buyers = categories.loc[
            categories.product_category_name_english.eq(category), "customer_unique_id"
        ]
        prepared[column] = prepared.index.isin(buyers).astype(int)
    return prepared


x_train = model_frame("train", train)
x_val = model_frame("validation", val)
x_test = model_frame("test", test)


def classifier(variant: str) -> Pipeline:
    transformers = [
        ("numeric", Pipeline([
            ("log1p", FunctionTransformer(np.log1p)),
            ("scale", StandardScaler()),
        ]), NUMERIC),
        ("state", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["state"]),
    ]
    if variant in ("segment", "segment_categories"):
        transformers.append((
            "segment", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["segment"]
        ))
    if variant in ("categories", "segment_categories"):
        transformers.append(("categories", "passthrough", category_columns))
    return Pipeline([
        ("preprocess", ColumnTransformer(transformers, sparse_threshold=0)),
        ("model", LogisticRegression(C=1.0, max_iter=2000, random_state=SEED)),
    ])


variants = ["baseline", "segment", "categories", "segment_categories"]
validation = {}
validation_scores = {}
for variant in variants:
    model = classifier(variant)
    with threadpool_limits(limits=2):
        model.fit(x_train, train.y)
        score = model.predict_proba(x_val)[:, 1]
    validation[variant] = evaluate(val, score)
    validation_scores[variant] = score
    print("VALIDATION", variant, json.dumps(validation[variant]), flush=True)

# Use validation AP alone for selection.  An equal score keeps the simpler model.
selected = max(variants, key=lambda variant: validation[variant]["AP"])
combined_x = pd.concat([x_train, x_val])
combined_y = pd.concat([train.y, val.y])
test_results = {}
for variant in ["baseline", selected] if selected != "baseline" else ["baseline"]:
    model = classifier(variant)
    with threadpool_limits(limits=2):
        model.fit(combined_x, combined_y)
        score = model.predict_proba(x_test)[:, 1]
    test_results[variant] = evaluate(test, score)
    print("EXPLORATORY TEST", variant, json.dumps(test_results[variant]), flush=True)


def profile(phase: str, frame: pd.DataFrame, include_errors: bool = False) -> list[dict]:
    category_flags = model_frame(phase, frame)[category_columns]
    assigned = labels[phase]
    scores = validation_scores["baseline"] if include_errors else None
    rank_mask = np.zeros(len(frame), dtype=bool)
    if scores is not None:
        k = math.ceil(len(frame) * 0.1)
        rank = np.lexsort((frame.index.astype(str).to_numpy(), -scores))[:k]
        rank_mask[rank] = True
    rows = []
    for group in sorted(set(assigned)):
        mask = assigned == group
        portion = frame.iloc[np.flatnonzero(mask)]
        row = {
            "segment": int(group), "customers": int(mask.sum()),
            "repeaters": int(portion.y.sum()), "repeat_rate": float(portion.y.mean()),
            "median_R_days": float(portion.R.median()),
            "median_F_orders": float(portion.F.median()),
            "repeat_history_share": float(portion.F.gt(1).mean()),
            "median_M_BRL": float(portion.M.median()),
            "median_items_per_order": float(portion.average_item_rows.median()),
            "median_freight_share": float(portion.freight_share.median()),
        }
        if include_errors:
            row["baseline_top10_selected"] = int((mask & rank_mask).sum())
            row["baseline_top10_hits"] = int((frame.y.to_numpy() & mask & rank_mask).sum())
            row["baseline_top10_missed_repeaters"] = int((frame.y.to_numpy() & mask & ~rank_mask).sum())
        for col, category in category_map.items():
            count = int(category_flags.loc[portion.index, col].sum())
            overall = float(category_flags[col].mean())
            row[f"{col}_buyers"] = count
            row[f"{col}_share"] = count / len(portion)
            row[f"{col}_lift"] = (count / len(portion)) / overall if overall else None
        rows.append(row)
    return rows


training_profile = profile("train", train)
validation_profile = profile("validation", val, include_errors=True)
test_profile = profile("test", test)
pd.DataFrame(validation_profile).to_csv(OUT / "validation-groups.csv", index=False)
pd.DataFrame([
    {"variant": variant, **validation[variant],
     **{f"exploratory_test_{key}": value for key, value in test_results.get(variant, {}).items()}}
    for variant in variants
]).to_csv(OUT / "model-comparison.csv", index=False)

source_files = ["olist_orders_dataset.csv", "olist_order_items_dataset.csv",
                "olist_customers_dataset.csv", "olist_products_dataset.csv",
                "product_category_name_translation.csv"]
report = {
    "purpose": "Exploratory completion of proposal's segment, group EDA, and prediction feedback loop",
    "source_sha256": {name: hashlib.sha256((DATA / name).read_bytes()).hexdigest() for name in source_files},
    "cohorts": {"train": "2017-10-01", "validation": "2018-01-01", "test": "2018-04-01"},
    "target": "At least one new approved, positive-item-value order within 90 days",
    "segment_design": {
        "inputs": CLUSTER_INPUT, "transform": "log1p then standard scale fitted on training snapshot",
        "method": "KMeans", "clusters": 4, "seed": SEED,
        "fit_on": "training snapshot historical features only; no outcomes",
        "validation_silhouette_RFM": silhouette,
        "validation_resample_ARI": stability,
    },
    "top_categories_selected_on_train": category_map,
    "unknown_category_item_rows": unknown_category_rows,
    "model": "LogisticRegression C=1; baseline original 11 features; optional segment and/or five category flags",
    "selection": "Highest validation average precision; ties favor simpler model; 2018-04 test inspected only after this selection",
    "validation": validation,
    "selected": selected,
    "exploratory_test": test_results,
    "profiles": {"train": training_profile, "validation": validation_profile, "test": test_profile},
    "limitations": [
        "This test quarter appears in the already published baseline experiment, so it is not an untouched confirmatory holdout.",
        "Validation outcomes inform model selection and group diagnostics; those diagnostics are exploratory.",
        "Observed Olist approvals do not capture all customer purchases or causal effects of marketing.",
        "Category lift can reflect number of purchase opportunities; category attributes may be missing.",
        "The same buyer can occur in multiple temporal snapshots; model does not establish new-customer generalization.",
    ],
}
assert report["source_sha256"]["olist_orders_dataset.csv"] == hashes["olist_orders_dataset.csv"]
assert report["source_sha256"]["olist_order_items_dataset.csv"] == hashes["olist_order_items_dataset.csv"]
assert report["source_sha256"]["olist_customers_dataset.csv"] == hashes["olist_customers_dataset.csv"]
(OUT / "results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("SELECTED", selected, "VALIDATION AP", validation[selected]["AP"], flush=True)
