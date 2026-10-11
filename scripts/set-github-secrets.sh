#!/usr/bin/env bash
# Push every KEY=VALUE pair from an env file into GitHub Actions secrets.
#
# Usage:
#   scripts/set-github-secrets.sh .env.qa                 # repo-level secrets
#   scripts/set-github-secrets.sh .env.qa --env qa        # environment "qa" secrets (recommended)
#   DRY_RUN=1 scripts/set-github-secrets.sh .env.qa       # print key names only, change nothing
#
# Requirements: GitHub CLI (`gh auth login`) with admin rights on the repo.
# The env file is parsed line by line; blank lines and # comments are skipped,
# surrounding single/double quotes around values are stripped. Values are never echoed.
set -euo pipefail

ENV_FILE="${1:?usage: $0 <env-file> [--env <github-environment>]}"
shift || true
GH_ENV=""
REPO="${GITHUB_REPOSITORY:-Asim971/business_central}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) GH_ENV="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

[[ -f "$ENV_FILE" ]] || { echo "env file not found: $ENV_FILE" >&2; exit 1; }

if [[ -n "$GH_ENV" && -z "${DRY_RUN:-}" ]]; then
  # Create the environment if it does not exist yet (idempotent).
  gh api --method PUT "repos/${REPO}/environments/${GH_ENV}" >/dev/null
fi

count=0
while IFS= read -r line || [[ -n "$line" ]]; do
  line="${line%$'\r'}"
  [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
  key="${line%%=*}"
  value="${line#*=}"
  key="$(echo "$key" | xargs)"
  [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || { echo "skipping malformed line for key '$key'" >&2; continue; }
  # strip one layer of matching quotes
  if [[ "$value" =~ ^\"(.*)\"$ ]]; then value="${BASH_REMATCH[1]}"; fi
  if [[ "$value" =~ ^\'(.*)\'$ ]]; then value="${BASH_REMATCH[1]}"; fi
  if [[ -n "${DRY_RUN:-}" ]]; then
    echo "would set ${key} (${#value} chars)${GH_ENV:+ in environment ${GH_ENV}}"
  else
    if [[ -n "$GH_ENV" ]]; then
      printf '%s' "$value" | gh secret set "$key" --repo "$REPO" --env "$GH_ENV"
    else
      printf '%s' "$value" | gh secret set "$key" --repo "$REPO"
    fi
    echo "set ${key}"
  fi
  count=$((count + 1))
done < "$ENV_FILE"
echo "${count} secret(s) processed for ${REPO}${GH_ENV:+ (environment: ${GH_ENV})}"
