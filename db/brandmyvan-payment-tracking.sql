alter table public.brandmyvan_logo_requests
 add column payment_status text not null default 'unpaid' check(payment_status in ('unpaid','paid')),
 add column paid_at timestamptz,
 add column production_status text not null default 'waiting' check(production_status in ('waiting','ready_to_print','printed','installed')),
 add column private_notes text not null default '' check(length(private_notes)<=5000);

create or replace function public.manage_brandmyvan_request(
 p_id uuid,p_revision integer,p_admin uuid,p_payment_status text,p_production_status text,p_private_notes text
) returns jsonb language plpgsql security invoker set search_path='' as $$
declare r public.brandmyvan_logo_requests;
begin
 if not exists(select 1 from public.brandmyvan_admins where user_id=p_admin) then return jsonb_build_object('error','forbidden');end if;
 if p_payment_status not in ('unpaid','paid') or p_production_status not in ('waiting','ready_to_print','printed','installed') or length(p_private_notes)>5000 then return jsonb_build_object('error','invalid');end if;
 select * into r from public.brandmyvan_logo_requests where id=p_id for update;
 if not found then return jsonb_build_object('error','not_found');end if;
 if r.revision<>p_revision then return jsonb_build_object('error','stale');end if;
 if p_payment_status='paid' and r.status<>'confirmed' then return jsonb_build_object('error','confirm_first');end if;
 if p_production_status<>'waiting' and p_payment_status<>'paid' then return jsonb_build_object('error','pay_first');end if;
 update public.brandmyvan_logo_requests set
  payment_status=p_payment_status,
  paid_at=case when p_payment_status='paid' then coalesce(paid_at,now()) else null end,
  production_status=p_production_status,
  private_notes=p_private_notes,
  revision=revision+1,
  reviewed_at=now(),
  reviewed_by=p_admin
 where id=p_id;
 return jsonb_build_object('id',p_id,'revision',r.revision+1,'payment_status',p_payment_status,'production_status',p_production_status);
end;
$$;
revoke all on function public.manage_brandmyvan_request(uuid,integer,uuid,text,text,text) from public,anon,authenticated;
grant execute on function public.manage_brandmyvan_request(uuid,integer,uuid,text,text,text) to service_role;
