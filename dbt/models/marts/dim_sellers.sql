select
    s.seller_id,
    s.zip_code_prefix,
    s.city,
    s.state,
    geo.latitude,
    geo.longitude
from {{ ref('stg_sellers') }} as s
left join {{ ref('stg_geolocation') }} as geo
    on s.zip_code_prefix = geo.zip_code_prefix
