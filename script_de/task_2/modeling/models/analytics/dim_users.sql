{{
    config(
        materialized = 'incremental',
        alias='dim_users',
		unique_key='id',
    )
}}


select 
	cr.id,
	name,
	case 
		when dob like '%1900%' then cast(null as date)
		when dob like '____-__-__' then cast(str_to_date(dob, '%Y-%m-%d') as date)
    	when dob like '____/__/__' then cast(str_to_date(dob, '%Y/%m/%d') as date)
    	when dob like '__/__/____' then cast(str_to_date(dob, '%d/%m/%Y') as date)
    end as dob,
    car.address,
    lower(car.city) as city,
    lower(car.province) as province,
    cr.created_at,
    cr.updated_at
from 
	(select *, rank() over(partition by id order by updated_at desc) as rnk from dwh_maju_jaya.customers_raw cr) cr 
left join 
	(select *, rank() over(partition by id order by datefile desc) as rnk from dwh_maju_jaya.customer_address_raw car) car
		on car.customer_id = cr.id 
			and car.rnk = 1
where cr.rnk = 1
{% if is_incremental() %}
AND cr.updated_at > (
    select COALESCE(max(cr.updated_at), '1900-01-01')
    from {{ this }}
)
{% endif %}