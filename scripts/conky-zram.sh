#!/usr/bin/env bash
set -euo pipefail

awk '
  NR > 1 && $1 ~ /zram/ { used += $4; total += $3 }
  END {
    if (total > 0) {
      printf "%.1f%%", (used / total) * 100
    } else {
      printf "n/a"
    }
  }
' /proc/swaps
