"""
ml/clustering.py
K-Means customer clustering on RFM feature space.

Pipeline:
  1. Load RFM data (recency_days, frequency, monetary)
  2. StandardScaler normalisation
  3. KMeans with k=3 (elbow analysis shows diminishing returns beyond 3)
  4. Return labeled DataFrame + cluster summary stats

Why K-Means on RFM?
  RFM features map directly to customer value axes.
  Clustering finds natural groupings without manual rule thresholds,
  making it more data-driven than pure NTILE scoring.
  Clusters can be used to personalise campaign targeting.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


FEATURES = ["recency_days", "frequency", "monetary"]
N_CLUSTERS = 3
RANDOM_STATE = 42

CLUSTER_LABELS = {
    # Assigned post-fit by inspecting centroids:
    # lowest recency (most recent) + high F + high M → Premium
    # mid values → Regular
    # high recency (least recent) + low F + low M → Dormant
    0: "Regular",
    1: "Premium",
    2: "Dormant",
}


def fit_clusters(rfm_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Parameters
    ----------
    rfm_df : DataFrame with at least [customer_id, recency_days, frequency, monetary]

    Returns
    -------
    labeled_df  : Original df + cluster_id + cluster_label columns
    model_info  : Dict with silhouette score, inertia, centroids
    """
    df = rfm_df.dropna(subset=FEATURES).copy()

    X = df[FEATURES].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    km = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
    df["cluster_id"] = km.fit_predict(X_scaled)

    # Label clusters by interpreting centroids
    centroids = scaler.inverse_transform(km.cluster_centers_)
    centroid_df = pd.DataFrame(centroids, columns=FEATURES)

    # Sort by monetary desc: highest monetary = Premium (idx 0), etc.
    sorted_idx = centroid_df["monetary"].argsort()[::-1].values
    label_map = {int(sorted_idx[0]): "Premium",
                 int(sorted_idx[1]): "Regular",
                 int(sorted_idx[2]): "Dormant"}
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
