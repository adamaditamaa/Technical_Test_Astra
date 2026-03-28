{{
    config(
        materialized = 'incremental',
        alias='fact_after_sales',
		unique_key='id',
    )
}}

select 
	MD5(CONCAT(service_ticket, created_at)) as id,
	service_ticket,
	vin,
	customer_id as dim_userid,
	model,
	service_date,
	service_type,
	created_at,
	updated_at
from (
	select *,rank() over(partition by service_ticket order by updated_at desc) as rnk from dwh_maju_jaya.after_sales_raw asr 	
) ae
where rnk = 1
{% if is_incremental() %}
and updated_at > (
    select COALESCE(max(updated_at), '1900-01-01')
    from {{ this }}
)
{% endif %}