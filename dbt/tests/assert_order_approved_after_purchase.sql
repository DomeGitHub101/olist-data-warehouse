-- An order cannot be approved before it was placed.
select order_id, purchased_at, approved_at
from {{ ref('stg_orders') }}
where approved_at < purchased_at
