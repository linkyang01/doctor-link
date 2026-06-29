#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT_DIR}"

if [[ -z "${PYPI_API_TOKEN:-}" ]]; then
  echo "PYPI_API_TOKEN is not set."
  echo "Next step: export PYPI_API_TOKEN and rerun, or trigger the Release workflow with publish_pypi=true."
  exit 1
fi

python -m pip install --upgrade pip build twine
python -m build
TWINE_USERNAME=__token__ TWINE_PASSWORD="${PYPI_API_TOKEN}" python -m twine upload dist/*
echo "Published doctor-link to PyPI."