with payments as (
    select
        *,
        row_number() over (
            partition by order_id
            order by payment_value desc, payment_sequential
        ) as value_rank
    from {{ ref('stg_order_payments') }}
)

select
    order_id,
    count(*) as payment_count,
    sum(payment_value) as payment_value,
    max(payment_installments) as max_installments,
    -- The method that covered the largest share of the order.
    max(case when value_rank = 1 then payment_type end) as primary_payment_type,
    bool_or(payment_type = 'voucher') as used_voucher
from payments
group by order_id
