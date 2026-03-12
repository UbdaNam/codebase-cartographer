create table analytics.orders_enriched as
with base as (
  select * from raw.orders
)
select *
from base
join raw.customers on base.customer_id = raw.customers.id;
