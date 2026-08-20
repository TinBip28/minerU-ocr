#!/bin/bash
# Initialize MinerU OCR models from external volume
# Usage:
#   docker compose run --rm init-models
#   docker run --rm -v ./models:/models mineru-ocr-vi:slim /bin/bash /app/docker/init-models.sh

set -euo pipefail

export MINERU_MODEL_SOURCE="${MINERU_MODEL_SOURCE:-auto}"
export MINERU_MODEL_BASE_DIR="${MINERU_MODEL_BASE_DIR:-/models}"

echo "=========================================="
echo "MinerU OCR - Model Initialization"
echo "=========================================="
echo ""
echo "Model source:   ${MINERU_MODEL_SOURCE}"
echo "Model base dir: ${MINERU_MODEL_BASE_DIR}"
echo ""

mkdir -p "${MINERU_MODEL_BASE_DIR}"

# Check if models already exist
if [ -d "${MINERU_MODEL_BASE_DIR}/PDF-Extract-Kit-1.0" ]; then
    echo "✓ Models already exist at ${MINERU_MODEL_BASE_DIR}"
    echo "  Skipping download."
    exit 0
fi

echo "Downloading OCR models..."
echo ""

cd /app
python3 docker/download_prod_models.py

echo ""
echo "=========================================="
echo "Model initialization completed"
echo "=========================================="
echo ""
echo "Models stored at:"
find "${MINERU_MODEL_BASE_DIR}" -maxdepth 2 -type d 2>/dev/null | head -20
