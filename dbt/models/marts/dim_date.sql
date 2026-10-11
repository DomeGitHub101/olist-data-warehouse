-- Covers the full Olist period (purchases run from 2016-09 to 2018-10).
select
    date_day::date as date_day,
    extract(year from date_day)::integer as year,
    extract(quarter from date_day)::integer as quarter,
    extract(month from date_day)::integer as month,
    to_char(date_day, 'FMMonth') as month_name,
    to_char(date_day, 'YYYY-MM') as year_month,
    extract(isodow from date_day)::integer as day_of_week,
    to_char(date_day, 'FMDay') as day_name,
    extract(isodow from date_day) in (6, 7) as is_weekend
from generate_series(
    '2016-01-01'::date,
    '2018-12-31'::date,
    interval '1 day'
) as date_day
