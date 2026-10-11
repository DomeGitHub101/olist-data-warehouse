-- fct_order_items must keep every staged item (joins must not drop rows).
with counts as (
    select
        (select count(*) from {{ ref('stg_order_items') }}) as staged,
        (select count(*) from {{ ref('fct_order_items') }}) as modeled
)

select *
from counts
where staged <> modeled
