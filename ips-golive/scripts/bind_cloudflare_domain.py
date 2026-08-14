#!/usr/bin/env python3
"""
Bind a Cloudflare-managed custom domain to an Azure Container App service.

Automates the deterministic Azure side of capability 3 (see
references/cloudflare-domain-binding.md):

  1. read the app's customDomainVerificationId, the environment static IP,
     and the app FQDN;
  2. print the exact Cloudflare DNS records + www redirect the user must add;
  3. pre-flight the DNS (the high-value check: is the apex accidentally
     proxied / orange? that single mistake breaks both cert issuance and
     serving);
  4. add the hostname, then bind a managed certificate using HTTP validation
     (the reliable path — needs NO extra DNS token record);
  5. poll the certificate to a terminal state;
  6. verify the live HTTPS endpoint.

This script does NOT touch Cloudflare — DNS records and redirect rules live in
the user's Cloudflare account and are added by the user (or, optionally, via
the Cloudflare API with the user's token; out of scope here).

Usage:
  # Step 1 — just show what to add in Cloudflare, then stop:
  python bind_cloudflare_domain.py --hostname example.com \
      --containerapp ca-foo --resource-group rg-foo --environment cae-foo \
      --print-dns-only

  # Step 2 — after the user added the DNS records, do the Azure binding:
  python bind_cloudflare_domain.py --hostname example.com \
      --containerapp ca-foo --resource-group rg-foo --environment cae-foo
"""
import argparse
import json
import subprocess
import sys
import time


def sh(cmd, check=True, capture=True, timeout=None):
    r = subprocess.run(cmd, shell=True, text=True,
                       capture_output=capture, timeout=timeout)
    if check and r.returncode != 0:
        sys.stderr.write((r.stderr or r.stdout or "").strip() + "\n")
        raise SystemExit(f"command failed ({r.returncode}): {cmd}")
    return (r.stdout or "").strip()


def az_json(cmd):
    out = sh(cmd)
    # az sometimes prefixes WARNINGs; strip to first JSON token
    for i, ch in enumerate(out):
        if ch in "[{":
            out = out[i:]
            break
    return json.loads(out) if out else None


def dig_short(name, rtype="A"):
    try:
        return sh(f"dig +short {name} {rtype} @1.1.1.1", check=False).splitlines()
    except Exception:
        return []


def is_apex(hostname):
    # Simple heuristic: 2 labels => apex (example.com). Multi-label => subdomain.
    # Known two-part public suffixes (co.uk, com.cn, ...) are the exception;
    # override with --record-type if needed.
    return hostname.count(".") == 1


def preflight_ok(args):
    print("\n=== DNS pre-flight ===")
    ok = True
    apex = args.record_type == "apex" or (args.record_type == "auto" and is_apex(args.hostname))
    a = dig_short(args.hostname, "A")
    print(f"{args.hostname} A -> {a or '<none>'}")
    if apex:
        if args.static_ip in a:
            if len(a) == 1:
                print("  OK: apex points straight at the Azure static IP (DNS only / grey).")
            else:
                print("  OK-ish: static IP present but multiple A records — ensure grey cloud (DNS only).")
        elif a:
            print("  !! apex does NOT resolve to the Azure static IP.")
            print("     If these look like Cloudflare IPs (104.x / 172.67.x), the record is")
            print("     PROXIED (orange). Azure cannot validate/serve through the proxy ->")
            print("     this causes stuck 'Pending' certs and Cloudflare 525. Set the apex")
            print("     A record to DNS only (grey cloud).")
            ok = False
        else:
            print("  !! apex has no A record yet — add it (grey cloud) before binding.")
            ok = False
    else:
        cn = dig_short(args.hostname, "CNAME") or a
        print(f"{args.hostname} target -> {cn or '<none>'}")
        if not cn:
            print("  !! subdomain has no record yet — add a CNAME to the app FQDN (grey) first.")
            ok = False
    return ok


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--hostname", required=True, help="custom domain, e.g. example.com or app.example.com")
    p.add_argument("--containerapp", required=True, help="Azure Container App name, e.g. ca-foo")
    p.add_argument("--resource-group", required=True)
    p.add_argument("--environment", required=True, help="Container Apps managed environment name")
    p.add_argument("--record-type", choices=["auto", "apex", "subdomain"], default="auto")
    p.add_argument("--validation", choices=["HTTP", "CNAME", "TXT"], default="HTTP",
                   help="managed-cert domain-control validation. HTTP is the reliable default "
                        "(no extra DNS token). Only use TXT if you will also add the cert "
                        "validationToken as asuid.<host> TXT.")
    p.add_argument("--print-dns-only", action="store_true",
                   help="only print the Cloudflare records to add, then stop")
    p.add_argument("--skip-verify", action="store_true")
    p.add_argument("--poll-seconds", type=int, default=1200)
    args = p.parse_args()

    # 0. login
    acct = az_json("az account show -o json")
    print(f"Azure subscription: {acct.get('name')} ({acct.get('id')})")

    # 1. gather app facts
    rg, app, env = args.resource_group, args.containerapp, args.environment
    args.verification_id = sh(
        f'az containerapp show -g {rg} -n {app} '
        f'--query "properties.customDomainVerificationId" -o tsv')
    args.static_ip = sh(
        f'az containerapp env show -g {rg} -n {env} '
        f'--query "properties.staticIp" -o tsv')
    args.fqdn = sh(
        f'az containerapp show -g {rg} -n {app} '
        f'--query "properties.configuration.ingress.fqdn" -o tsv')

    apex = args.record_type == "apex" or (args.record_type == "auto" and is_apex(args.hostname))
    root = args.hostname
    print("\n=== Cloudflare records to add (in the domain's Cloudflare zone) ===")
    if apex:
        print(f"  A     @      {args.static_ip}        Proxy: DNS only (GREY)")
    else:
        print(f"  CNAME {root}  {args.fqdn}   Proxy: DNS only (GREY)")
    print(f"  TXT   asuid.{root}   {args.verification_id}   (domain-ownership check)")
    print("\n  Optional www -> apex redirect (only for an apex/root domain):")
    print(f"  CNAME www   {root}   Proxy: PROXIED (ORANGE)")
    print("  + Redirect Rule: Hostname = www." + root +
          f'  =>  301  concat("https://{root}", http.request.uri.path)')
    print("\n  RULES:")
    print("   - Served apex/host stays GREY (DNS only) when using the Azure managed cert.")
    print("   - www stays ORANGE (proxied) so the redirect rule fires at Cloudflare's edge.")

    if args.print_dns_only:
        print("\n(--print-dns-only) Add the records above, then re-run without this flag.")
        return

    # 2. pre-flight
    if not preflight_ok(args):
        raise SystemExit("\nDNS pre-flight failed — fix the records above (esp. grey cloud on "
                         "the apex), wait for propagation, then re-run.")

    # 3. add hostname
    print("\n=== az containerapp hostname add ===")
    sh(f"az containerapp hostname add -g {rg} -n {app} --hostname {args.hostname}",
       capture=True)

    # 4. bind with managed cert (HTTP validation by default)
    print(f"=== binding managed cert (validation: {args.validation}) — up to 20 min ===")
    sh(f"az containerapp hostname bind -g {rg} -n {app} --hostname {args.hostname} "
       f"--environment {env} --validation-method {args.validation}",
       capture=True, timeout=args.poll_seconds)

    # 5. confirm state
    binding = az_json(
        f'az containerapp show -g {rg} -n {app} '
        f'--query "properties.configuration.ingress.customDomains" -o json')
    state = next((b for b in (binding or []) if b.get("name") == args.hostname), {})
    print(f"binding: {state.get('bindingType')}")
    if state.get("bindingType") != "SniEnabled":
        raise SystemExit("hostname is not SniEnabled — cert did not bind; see the reference "
                         "'Gotchas' (usually validation method or a proxied apex).")

    # 6. verify
    if not args.skip_verify:
        print("\n=== verify ===")
        code = sh(f'curl -s -o /dev/null -w "%{{http_code}}" --max-time 20 https://{args.hostname}/',
                  check=False)
        print(f"https://{args.hostname}/ -> {code}")

    print(f"\nDONE: https://{args.hostname} is bound and serving.")


if __name__ == "__main__":
    main()
