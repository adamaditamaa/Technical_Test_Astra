{{
    config(
        materialized = 'incremental',
        alias='fact_sales',
		unique_key='id',
    )
}}

with main_data as (
	select *, rank() over(partition by vin order by updated_at desc) as rnk
	from sales_raw sr 
)
select 
	MD5(CONCAT(vin, created_at)) as id,
	vin,
	customer_id as dim_userid,
	model,
	invoice_date,
	price,
	created_at,
	updated_at
from main_data sr 
where rnk = 1
{% if is_incremental() %}
and updated_at > (
    select COALESCE(max(updated_at), '1900-01-01')
    from {{ this }}
)
{% endif %}