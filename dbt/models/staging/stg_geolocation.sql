-- The source has ~1M points for ~19K zip prefixes, some outside Brazil.
-- Reduce to one row per prefix: mean coordinates and most common city/state.
with points as (
    select
        geolocation_zip_code_prefix as zip_code_prefix,
        geolocation_lat::double precision as latitude,
        geolocation_lng::double precision as longitude,
        geolocation_city as city,
        geolocation_state as state
    from {{ source('raw', 'geolocation') }}
)

select
    zip_code_prefix,
    avg(latitude) as latitude,
    avg(longitude) as longitude,
    mode() within group (order by city) as city,
    mode() within group (order by state) as state
from points
-- Approximate bounding box of Brazil.
where latitude between -34 and 6
    and longitude between -74 and -34
group by zip_code_prefix
