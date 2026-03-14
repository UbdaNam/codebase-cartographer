"""Serve order metrics to downstream callers."""

from app.transforms import build_order_metrics


def get_metrics_endpoint() -> str:
    return build_order_metrics()
