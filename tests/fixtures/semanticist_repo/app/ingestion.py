"""Load raw order data for downstream processing."""

import pandas as pd


def load_orders():
    return pd.read_csv("data/orders.csv")
