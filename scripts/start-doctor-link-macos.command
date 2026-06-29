#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if command -v doctor-link >/dev/null 2>&1; then
  exec doctor-link wizard
fi
if [ -x ".venv/bin/doctor-link" ]; then
  exec .venv/bin/doctor-link wizard
fi
echo "Doctor link is not installed."
echo "Next step: pip install -e ."
exit 1
