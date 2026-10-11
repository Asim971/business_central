#!/usr/bin/env bash
# Read-only smoke test for the Business Central S2S connection.
# 1. Acquires a client-credentials token from Microsoft Entra ID.
# 2. GETs the companies list for Bc__Environment and checks Bc__CompanyId is present.
# 3. If Bc__AlPingEnabled=true, GETs the AnwarLogistics custom API `pings` endpoint.
# Never prints secret values. Exit code non-zero on any failure.
#
# Usage: set -a; source .env.qa; set +a; scripts/bc-smoke.sh
set -euo pipefail

: "${AzureAd__TenantId:?}" "${AzureAd__ClientId:?}" "${AzureAd__ClientSecret:?}"
: "${Bc__TenantId:?}" "${Bc__Environment:?}" "${Bc__CompanyId:?}"
INSTANCE="${AzureAd__Instance:-https://login.microsoftonline.com/}"
BC_BASE="${Bc__BaseUrl:-https://api.businesscentral.dynamics.com}"
SCOPE="${Bc__Scope:-https://api.businesscentral.dynamics.com/.default}"

token_json="$(curl -sS --fail-with-body -X POST "${INSTANCE%/}/${AzureAd__TenantId}/oauth2/v2.0/token" \
  --data-urlencode "client_id=${AzureAd__ClientId}" \
  --data-urlencode "client_secret=${AzureAd__ClientSecret}" \
  --data-urlencode "scope=${SCOPE}" \
  --data-urlencode "grant_type=client_credentials")" || { echo "token request failed"; exit 1; }
token="$(printf '%s' "$token_json" | python3 -I -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))')"
[[ -n "$token" ]] || { echo "no access_token in token response"; exit 1; }
echo "token acquired (expires_in=$(printf '%s' "$token_json" | python3 -I -c 'import sys,json; print(json.load(sys.stdin).get("expires_in"))')s)"

std="${BC_BASE}/v2.0/${Bc__TenantId}/${Bc__Environment}/api/v2.0"
companies="$(curl -sS --fail-with-body -H "Authorization: Bearer ${token}" -H "Accept: application/json" "${std}/companies")" \
  || { echo "GET companies failed"; exit 1; }
printf '%s' "$companies" | python3 -I -c '
import sys, json, os
want = os.environ["Bc__CompanyId"].lower()
rows = json.load(sys.stdin).get("value", [])
for r in rows:
    print(f"company {r.get(\"id\")}  name={r.get(\"name\")!r}  displayName={r.get(\"displayName\")!r}")
ids = [r.get("id","").lower() for r in rows]
if want not in ids:
    print(f"Bc__CompanyId not found among {len(rows)} companies", file=sys.stderr); sys.exit(1)
print("Bc__CompanyId resolved OK")
'

if [[ "${Bc__AlPingEnabled:-false}" == "true" ]]; then
  custom="${BC_BASE}/v2.0/${Bc__TenantId}/${Bc__Environment}/api/anwarGroup/logistics/v1.0"
  if ping="$(curl -sS --fail-with-body -H "Authorization: Bearer ${token}" -H "Accept: application/json" \
      "${custom}/companies(${Bc__CompanyId})/pings")"; then
    echo "AL extension ping OK: $(printf '%s' "$ping" | head -c 300)"
  else
    echo "AL extension ping FAILED (extension not published to ${Bc__Environment} or API group differs)"; exit 1
  fi
fi
echo "smoke test passed"
