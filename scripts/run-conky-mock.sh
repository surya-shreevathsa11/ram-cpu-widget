#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_FILE="${PROJECT_ROOT}/conky/ram-cpu-widget.conkyrc"

if ! command -v conky >/dev/null 2>&1; then
  echo "Conky is not installed."
  echo "Install it first, then run this script again:"
  echo "  sudo apt install conky-all"
  exit 1
fi

pkill -f "conky -c ${CONFIG_FILE}" >/dev/null 2>&1 || true
exec conky -c "${CONFIG_FILE}"
