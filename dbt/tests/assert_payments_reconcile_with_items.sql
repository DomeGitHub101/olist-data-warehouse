-- Paid amount should match items + freight. Some source orders differ
-- (installment interest, vouchers), so fail only when more than 1% of
-- orders are off by over 1 BRL.
with mismatches as (
    select
        count(*) filter (where abs(payment_value - order_value) > 1) as mismatched,
        count(*) as total
    from {{ ref('fct_orders') }}
    where payment_value is not null
        and item_count > 0
)

select *
from mismatches
where mismatched > total * 0.01
