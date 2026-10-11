select
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    o.order_status,
    o.purchased_at,
    o.purchased_at::date as purchase_date,
    o.approved_at,
    o.delivered_to_carrier_at,
    o.delivered_to_customer_at,
    o.estimated_delivery_date,
    coalesce(items.item_count, 0) as item_count,
    coalesce(items.items_value, 0) as items_value,
    coalesce(items.freight_value, 0) as freight_value,
    coalesce(items.items_value, 0) + coalesce(items.freight_value, 0) as order_value,
    payments.payment_value,
    payments.primary_payment_type,
    payments.max_installments,
    coalesce(payments.used_voucher, false) as used_voucher,
    reviews.review_score,
    o.order_status = 'delivered' and o.delivered_to_customer_at is not null as is_delivered,
    round(
        (extract(epoch from o.delivered_to_customer_at - o.purchased_at) / 86400)::numeric,
        1
    ) as delivery_days,
    case
        when o.delivered_to_customer_at is null then null
        else o.delivered_to_customer_at::date > o.estimated_delivery_date
    end as is_late_delivery
from {{ ref('stg_orders') }} as o
inner join {{ ref('stg_customers') }} as c
    on o.customer_id = c.customer_id
left join {{ ref('int_order_items_aggregated') }} as items
    on o.order_id = items.order_id
left join {{ ref('int_order_payments_aggregated') }} as payments
    on o.order_id = payments.order_id
left join {{ ref('int_order_reviews_latest') }} as reviews
    on o.order_id = reviews.order_id
