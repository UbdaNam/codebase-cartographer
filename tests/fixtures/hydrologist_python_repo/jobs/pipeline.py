import pandas as pd

orders = pd.read_csv("data/input/orders.csv")
orders.to_csv("data/output/orders_clean.csv")
engine.execute("INSERT INTO analytics.orders_enriched SELECT * FROM raw.orders")
