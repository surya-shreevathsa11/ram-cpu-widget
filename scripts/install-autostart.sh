#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TARGET_DIR="${HOME}/.config/autostart"
TARGET_FILE="${TARGET_DIR}/ram-widget.desktop"

mkdir -p "${TARGET_DIR}"

sed "s|^Exec=.*|Exec=python3 ${PROJECT_ROOT}/ram_widget.py|" \
  "${PROJECT_ROOT}/packaging/ram-widget.desktop" > "${TARGET_FILE}"

echo "Installed autostart entry:"
echo "  ${TARGET_FILE}"
