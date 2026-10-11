-- One row per real customer (customer_unique_id); location is taken
-- from their most recent order.
with orders as (
    select
        c.customer_unique_id,
        c.zip_code_prefix,
        c.city,
        c.state,
        o.order_id,
        o.order_status,
        o.purchased_at,
        row_number() over (
            partition by c.customer_unique_id
            order by o.purchased_at desc, o.order_id
        ) as recency_rank
    from {{ ref('stg_orders') }} as o
    inner join {{ ref('stg_customers') }} as c
        on o.customer_id = c.customer_id
),

order_stats as (
    select
        orders.customer_unique_id,
        count(*) as order_count,
        min(orders.purchased_at) as first_order_at,
        max(orders.purchased_at) as last_order_at,
        coalesce(sum(payments.payment_value) filter (
            where orders.order_status not in ('canceled', 'unavailable')
        ), 0) as lifetime_value
    from orders
    left join {{ ref('int_order_payments_aggregated') }} as payments
        on orders.order_id = payments.order_id
    group by orders.customer_unique_id
)

select
    latest.customer_unique_id,
    latest.zip_code_prefix,
    latest.city,
    latest.state,
    geo.latitude,
    geo.longitude,
    stats.order_count,
    stats.first_order_at,
    stats.last_order_at,
    stats.lifetime_value,
    case when stats.order_count > 1 then 'repeat' else 'one-time' end as customer_type
from orders as latest
inner join order_stats as stats
    on latest.customer_unique_id = stats.customer_unique_id
left join {{ ref('stg_geolocation') }} as geo
    on latest.zip_code_prefix = geo.zip_code_prefix
where latest.recency_rank = 1
