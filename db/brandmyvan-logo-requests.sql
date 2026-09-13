-- Private enquiries for the funding-v1 logo editor. No spot is sold by this form.
create table if not exists public.brandmyvan_logo_requests (
 id uuid primary key,
 created_at timestamptz not null default now(),
 status text not null default 'pending_review' check(status in ('pending_review','confirmed','declined')),
 company text not null check(length(company) between 1 and 100),
 email text not null check(length(email) between 3 and 254),
 spot_id text not null,
 price_eur integer not null check(price_eur in (200,400,750,1500)),
 duration_months integer not null default 12 check(duration_months=12),
 logo_name text not null,
 logo_png text not null check(length(logo_png)<=1900000),
 artwork_png text not null check(length(artwork_png)<=1900000),
 placement jsonb not null,
 request_hash text not null,
 client_hash text not null
);
alter table public.brandmyvan_logo_requests enable row level security;
revoke all on public.brandmyvan_logo_requests from public, anon, authenticated;
grant select,insert,update,delete on public.brandmyvan_logo_requests to service_role;
create index if not exists bmv_logo_requests_client_created on public.brandmyvan_logo_requests(client_hash,created_at);
create index if not exists bmv_logo_requests_email_created on public.brandmyvan_logo_requests(email,created_at);
create or replace function public.submit_brandmyvan_logo_request(p_request jsonb,p_client text,p_hash text)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare existing_hash text; new_id uuid := (p_request->>'id')::uuid;
begin
 -- Serialize each client and email, including concurrent requests on different instances.
 perform pg_advisory_xact_lock(hashtextextended('bmv-client:'||p_client,0));
 perform pg_advisory_xact_lock(hashtextextended('bmv-email:'||(p_request->>'email'),0));
 select request_hash into existing_hash from public.brandmyvan_logo_requests where id=new_id;
 if found then
   if existing_hash=p_hash then return jsonb_build_object('id',new_id,'status','pending_review');end if;
   return jsonb_build_object('error','id_conflict');
 end if;
 if (select count(*) from public.brandmyvan_logo_requests where client_hash=p_client and created_at>now()-interval '1 hour')>=5
 or (select count(*) from public.brandmyvan_logo_requests where email=p_request->>'email' and created_at>now()-interval '1 day')>=5 then
   return jsonb_build_object('error','rate_limit');
 end if;
 insert into public.brandmyvan_logo_requests(id,company,email,spot_id,price_eur,logo_name,logo_png,artwork_png,placement,request_hash,client_hash)
 values(new_id,p_request->>'company',p_request->>'email',p_request->>'spot_id',(p_request->>'price_eur')::integer,p_request->>'logo_name',p_request->>'logo_png',p_request->>'artwork_png',p_request->'placement',p_hash,p_client);
 return jsonb_build_object('id',new_id,'status','pending_review');
end;
$$;
revoke all on function public.submit_brandmyvan_logo_request(jsonb,text,text) from public,anon,authenticated;
grant execute on function public.submit_brandmyvan_logo_request(jsonb,text,text) to service_role;
