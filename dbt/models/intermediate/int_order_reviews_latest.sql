-- Some orders were reviewed more than once; keep the latest review.
with ranked as (
    select
        *,
        row_number() over (
            partition by order_id
            order by review_answered_at desc, review_created_date desc, review_id
        ) as review_rank
    from {{ ref('stg_order_reviews') }}
)

select
    order_id,
    review_id,
    review_score,
    review_created_date,
    review_answered_at
from ranked
where review_rank = 1
