"""Build curated order metrics from raw inputs."""

from app.ingestion import load_orders


def build_order_metrics() -> str:
    df = load_orders()
    df.to_parquet("warehouse/order_metrics.parquet")
    return "warehouse/order_metrics.parquet"
