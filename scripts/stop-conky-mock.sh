#!/usr/bin/env bash
set -euo pipefail

pkill -f "conky -c /data/personal-projs/ram-cpu-widget/conky/ram-cpu-widget.conkyrc" || true
echo "Conky mock widget stopped."
