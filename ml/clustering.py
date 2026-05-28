"""
ml/clustering.py
K-Means customer clustering on RFM score space.

Pipeline:
  1. Load RFM score data (r_score, f_score, m_score)
  2. StandardScaler normalization
  3. KMeans with k=5 to align with general RFM segment count
  4. Return labeled DataFrame + cluster summary stats

Why K-Means on RFM scores?
  Score features are already ordinal and comparable, so clustering in
  score space produces segments that align with RFM segment categories.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


FEATURES = ["r_score", "f_score", "m_score"]
N_CLUSTERS = 4
RANDOM_STATE = 42

CLUSTER_LABELS = [
    "Champions",
    "Loyal Customers",
    "Potential Loyalists",
    "Lost Customers",
]


def fit_clusters(rfm_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Parameters
    ----------
    rfm_df : DataFrame with at least [customer_id, r_score, f_score, m_score]

    Returns
    -------
    labeled_df  : Original df + cluster_id + cluster_label columns
    model_info  : Dict with silhouette score, inertia, centroids
    """
    df = rfm_df.dropna(subset=FEATURES).copy()

    X = df[FEATURES].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    km = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10,)
    df["cluster_id"] = km.fit_predict(X_scaled)

    # Label clusters by centroid score ordering in RFM score space.
    centroids = scaler.inverse_transform(km.cluster_centers_)
    centroid_df = pd.DataFrame(centroids, columns=FEATURES)
    score_rank = centroid_df[FEATURES].sum(axis=1).argsort()[::-1].values
    labels = ["Champions", "Loyal Customers", "Potential Loyalists", "Lost Customers"]
    label_map = {int(score_rank[i]): labels[i] for i in range(min(len(score_rank), len(labels)))}
    df["cluster_label"] = df["cluster_id"].map(label_map)

    sil = round(silhouette_score(X_scaled, df["cluster_id"]), 4)

    model_info = {
        "silhouette_score": sil,
        "inertia":          round(km.inertia_, 2),
        "n_clusters":       N_CLUSTERS,
        "centroids":        centroid_df.round(2).to_dict("records"),
        "label_map":        label_map,
    }

    return df, model_info


def cluster_summary(labeled_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate cluster stats for the dashboard summary table."""
    return (
        labeled_df.groupby("cluster_label")
        .agg(
            customers=("customer_id", "count"),
            avg_recency=("recency_days", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
            total_revenue=("monetary", "sum"),
        )
        .round(2)
        .reset_index()
        .sort_values("avg_monetary", ascending=False)
    )
