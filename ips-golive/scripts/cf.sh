#!/usr/bin/env bash
# Thin transport over the Cloudflare REST + GraphQL APIs.
#
# Auth is auto-detected, preferring the scoped token when both are present:
#   CLOUDFLARE_API_TOKEN                      -> Authorization: Bearer
#   CLOUDFLARE_EMAIL + CLOUDFLARE_API_KEY     -> X-Auth-Email + X-Auth-Key (Global API Key)
#
# The credential is never echoed. Every response is printed as
# "[VERB path -> HTTP nnn]" followed by the raw body, so a caller can strip the
# first line and pipe the rest to a JSON parser.
set -euo pipefail

API=https://api.cloudflare.com/client/v4

die() { echo "ips-golive: $*" >&2; exit 1; }

# Checked once in the parent shell. auth_args() itself runs inside process
# substitution, where an exit would not propagate — so the missing-credential
# case must fail here, before any command runs.
require_cred() {
  [[ -n "${CLOUDFLARE_API_TOKEN:-}" ]] && return 0
  [[ -n "${CLOUDFLARE_EMAIL:-}" && -n "${CLOUDFLARE_API_KEY:-}" ]] && return 0
  die "no credential. Set CLOUDFLARE_API_TOKEN, or CLOUDFLARE_EMAIL + CLOUDFLARE_API_KEY, in ~/.zshrc"
}

auth_args() {
  if [[ -n "${CLOUDFLARE_API_TOKEN:-}" ]]; then
    printf '%s\n' -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}"
  else
    printf '%s\n' -H "X-Auth-Email: ${CLOUDFLARE_EMAIL}" -H "X-Auth-Key: ${CLOUDFLARE_API_KEY}"
  fi
}

# request VERB PATH [BODY]
request() {
  local verb="$1" path="$2" body="${3:-}"
  local url="${API}/${path#/}"
  local -a args=(-sS -X "$verb" "$url")
  while IFS= read -r a; do args+=("$a"); done < <(auth_args)
  if [[ -n "$body" ]]; then
    args+=(-H "Content-Type: application/json")
    if [[ "$body" == @* ]]; then args+=(--data-binary "$body"); else args+=(--data-binary "$body"); fi
  fi
  local out code
  out="$(curl "${args[@]}" -w $'\n%{http_code}')"
  code="${out##*$'\n'}"
  echo "[$verb ${path#/} -> HTTP ${code}]"
  printf '%s\n' "${out%$'\n'*}"
  [[ "$code" =~ ^2 ]] || return 1
}

usage() {
  cat <<'EOF'
usage: cf.sh <cmd>
  whoami                       verify the credential and print the acting user
  accounts                     list accounts (id + name)
  zones [name]                 list zones, or resolve one zone by exact name
  get      <path>              GET   (path is relative to /client/v4/)
  post     <path> '<json>'|@f  POST
  put      <path> '<json>'|@f  PUT   (rum/site_info updates need PUT; PATCH -> 405)
  patch    <path> '<json>'|@f  PATCH
  delete   <path>              DELETE
  graphql  '<json>'|@file      POST to the GraphQL analytics endpoint

Credentials come from the environment and are never printed:
  CLOUDFLARE_API_TOKEN                    (preferred)
  CLOUDFLARE_EMAIL + CLOUDFLARE_API_KEY   (Global API Key — full account access)
EOF
}

cmd="${1:-}"; shift || true
case "$cmd" in ""|-h|--help|help) : ;; *) require_cred ;; esac
case "$cmd" in
  whoami)
    request GET user | tail -n +2 | python3 -c 'import sys,json;d=json.load(sys.stdin);r=d.get("result") or {};print("email:",r.get("email"));print("id:",r.get("id"))'
    ;;
  accounts)
    request GET accounts | tail -n +2 | python3 -c 'import sys,json;[print(a["id"],"|",a["name"]) for a in json.load(sys.stdin).get("result",[])]'
    ;;
  zones)
    if [[ $# -ge 1 ]]; then p="zones?name=$1"; else p="zones?per_page=50"; fi
    request GET "$p" | tail -n +2 | python3 -c 'import sys,json;[print(z["id"],"|",z["name"],"|",z["status"]) for z in json.load(sys.stdin).get("result",[])]'
    ;;
  get)     [[ $# -ge 1 ]] || die "get needs a path";    request GET "$1" ;;
  post)    [[ $# -ge 1 ]] || die "post needs a path";   request POST "$1" "${2:-{\}}" ;;
  put)     [[ $# -ge 2 ]] || die "put needs a path and a body";   request PUT "$1" "$2" ;;
  patch)   [[ $# -ge 2 ]] || die "patch needs a path and a body"; request PATCH "$1" "$2" ;;
  delete)  [[ $# -ge 1 ]] || die "delete needs a path"; request DELETE "$1" ;;
  graphql)
    [[ $# -ge 1 ]] || die "graphql needs a body"
    body="$1"; [[ "$body" == @* ]] && body="$(cat "${body#@}")"
    url="https://api.cloudflare.com/client/v4/graphql"
    declare -a args=(-sS -X POST "$url" -H "Content-Type: application/json" --data-binary "$body")
    while IFS= read -r a; do args+=("$a"); done < <(auth_args)
    curl "${args[@]}"
    ;;
  ""|-h|--help|help) usage ;;
  *) usage; die "unknown command: $cmd" ;;
esac
