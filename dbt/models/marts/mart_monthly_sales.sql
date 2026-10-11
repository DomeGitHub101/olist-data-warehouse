-- Monthly business KPIs. Canceled and unavailable orders are excluded from revenue.
select
    date_trunc('month', purchased_at)::date as month,
    count(*) as orders,
    count(*) filter (where is_delivered) as delivered_orders,
    count(*) filter (where order_status = 'canceled') as canceled_orders,
    count(distinct customer_unique_id) as customers,
    sum(items_value) filter (where order_status not in ('canceled', 'unavailable')) as gmv,
    sum(freight_value) filter (where order_status not in ('canceled', 'unavailable')) as freight,
    round(
        avg(order_value) filter (where order_status not in ('canceled', 'unavailable')),
        2
    ) as avg_order_value,
    round(avg(review_score), 2) as avg_review_score,
    round(avg(delivery_days) filter (where is_delivered), 1) as avg_delivery_days,
    round(
        avg(is_late_delivery::integer) filter (where is_delivered),
        4
    ) as late_delivery_rate
from {{ ref('fct_orders') }}
group by 1
