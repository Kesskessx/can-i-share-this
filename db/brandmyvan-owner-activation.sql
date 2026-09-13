create table public.brandmyvan_admin_invitations(
 id uuid primary key default gen_random_uuid(),
 email text not null,
 token_hash text not null unique,
 expires_at timestamptz not null default now()+interval '24 hours',
 used_at timestamptz
);
alter table public.brandmyvan_admin_invitations enable row level security;
revoke all on public.brandmyvan_admin_invitations from public,anon,authenticated;
grant select,insert,update on public.brandmyvan_admin_invitations to service_role;
create function public.redeem_brandmyvan_admin_invitation(p_hash text,p_user uuid)
returns boolean language plpgsql security invoker set search_path='' as $$
declare invite public.brandmyvan_admin_invitations;
begin
 select * into invite from public.brandmyvan_admin_invitations where token_hash=p_hash for update;
 if not found or invite.used_at is not null or invite.expires_at<=now() then return false;end if;
 -- Only the service role calls this after validating the Auth Admin API response.
 insert into public.brandmyvan_admins(user_id) values(p_user) on conflict do nothing;
 update public.brandmyvan_admin_invitations set used_at=now() where id=invite.id;
 return true;
end;
$$;
revoke all on function public.redeem_brandmyvan_admin_invitation(text,uuid) from public,anon,authenticated;
grant execute on function public.redeem_brandmyvan_admin_invitation(text,uuid) to service_role;
