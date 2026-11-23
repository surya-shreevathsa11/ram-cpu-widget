#!/usr/bin/env bash
set -euo pipefail

for zone in /sys/class/thermal/thermal_zone*; do
  [[ -f "${zone}/type" && -f "${zone}/temp" ]] || continue
  zone_type="$(tr '[:upper:]' '[:lower:]' < "${zone}/type" 2>/dev/null || true)"
  raw="$(cat "${zone}/temp" 2>/dev/null || true)"
  [[ -n "${raw}" ]] || continue
  [[ "${raw}" =~ ^[0-9]+$ ]] || continue
  (( raw > 0 )) || continue

  if [[ "${zone_type}" == *x86_pkg_temp* || "${zone_type}" == *cpu* || "${zone_type}" == *pkg* ]]; then
    awk -v t="${raw}" 'BEGIN { printf "%.0f", t / 1000 }'
    exit 0
  fi
done

echo "n/a"
