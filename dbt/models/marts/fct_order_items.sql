select
    i.order_id || '-' || i.order_item_id as order_item_key,
    i.order_id,
    i.order_item_id,
    i.product_id,
    i.seller_id,
    c.customer_unique_id,
    o.order_status,
    o.purchased_at::date as purchase_date,
    i.shipping_limit_at,
    i.price,
    i.freight_value,
    i.price + i.freight_value as total_value
from {{ ref('stg_order_items') }} as i
inner join {{ ref('stg_orders') }} as o
    on i.order_id = o.order_id
inner join {{ ref('stg_customers') }} as c
    on o.customer_id = c.customer_id
