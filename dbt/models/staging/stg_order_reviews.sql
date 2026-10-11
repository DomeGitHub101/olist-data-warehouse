-- review_id is not unique on its own: one review can cover several orders.
select
    review_id,
    order_id,
    review_score::integer as review_score,
    review_comment_title as comment_title,
    review_comment_message as comment_message,
    review_creation_date::timestamp::date as review_created_date,
    review_answer_timestamp::timestamp as review_answered_at
from {{ source('raw', 'order_reviews') }}
