select
    p.product_id,
    p.category_name,
    -- Two categories have no translation; fall back to the Portuguese name.
    coalesce(t.category_name_english, p.category_name, 'unknown') as category_name_english,
    p.name_length,
    p.description_length,
    p.photos_qty,
    p.weight_g,
    p.length_cm,
    p.height_cm,
    p.width_cm,
    p.length_cm * p.height_cm * p.width_cm as volume_cm3
from {{ ref('stg_products') }} as p
left join {{ ref('stg_category_translation') }} as t
    on p.category_name = t.category_name
