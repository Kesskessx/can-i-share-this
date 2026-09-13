
create table public.brandmyvan_admins (
 user_id uuid primary key references auth.users(id) on delete cascade,
 created_at timestamptz not null default now()
);
alter table public.brandmyvan_admins enable row level security;
revoke all on public.brandmyvan_admins from public,anon,authenticated;
grant select,insert,delete on public.brandmyvan_admins to service_role;
alter table public.brandmyvan_logo_requests add column revision integer not null default 0;
alter table public.brandmyvan_logo_requests add column reviewed_at timestamptz;
alter table public.brandmyvan_logo_requests add column reviewed_by uuid references auth.users(id);
create unique index bmv_one_confirmed_spot on public.brandmyvan_logo_requests(spot_id) where status='confirmed';
create function public.review_brandmyvan_request(p_id uuid,p_status text,p_revision integer,p_admin uuid)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare r public.brandmyvan_logo_requests; spot text;
begin
 if not exists(select 1 from public.brandmyvan_admins where user_id=p_admin) then return jsonb_build_object('error','forbidden'); end if;
 if p_status not in ('pending_review','confirmed','declined') then return jsonb_build_object('error','invalid'); end if;
 select spot_id into spot from public.brandmyvan_logo_requests where id=p_id;
 if not found then return jsonb_build_object('error','not_found');end if;
 perform pg_advisory_xact_lock(hashtextextended('bmv-spot:'||spot,0));
 select * into r from public.brandmyvan_logo_requests where id=p_id for update;
 if r.revision<>p_revision then return jsonb_build_object('error','stale');end if;
 if p_status='confirmed' and exists(select 1 from public.brandmyvan_logo_requests where spot_id=spot and status='confirmed' and id<>p_id) then return jsonb_build_object('error','spot_taken');end if;
 update public.brandmyvan_logo_requests set status=p_status,revision=revision+1,reviewed_at=now(),reviewed_by=p_admin where id=p_id;
 return jsonb_build_object('id',p_id,'status',p_status,'revision',r.revision+1);
end;
$$;
revoke all on function public.review_brandmyvan_request(uuid,text,integer,uuid) from public,anon,authenticated;
grant execute on function public.review_brandmyvan_request(uuid,text,integer,uuid) to service_role;
create function public.guard_brandmyvan_spot() returns trigger language plpgsql security invoker set search_path='' as $$
begin
 perform pg_advisory_xact_lock(hashtextextended('bmv-spot:'||new.spot_id,0));
 if exists(select 1 from public.brandmyvan_logo_requests where spot_id=new.spot_id and status='confirmed') then raise exception 'spot_taken';end if;
 return new;
end;
$$;
revoke all on function public.guard_brandmyvan_spot() from public,anon,authenticated;
grant execute on function public.guard_brandmyvan_spot() to service_role;
create trigger bmv_guard_spot before insert on public.brandmyvan_logo_requests for each row execute function public.guard_brandmyvan_spot();
