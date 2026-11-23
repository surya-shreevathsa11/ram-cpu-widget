#!/usr/bin/env bash
set -euo pipefail

awk '
  /^MemTotal:/ { total = $2 }
  /^MemAvailable:/ { avail = $2 }
  END {
    if (total > 0) {
      used = total - avail
      printf "%.1f", (used / total) * 100
    } else {
      printf "n/a"
    }
  }
' /proc/meminfo
