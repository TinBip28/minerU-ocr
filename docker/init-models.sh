#!/bin/bash
# Initialize MinerU OCR models from external volume
# Usage:
#   docker compose run --rm init-models
#   ./docker/init-models.sh

set -e

# MinerU model base directory (matches MINERU_HOME/.mineru/models)
MINERU_HOME_DIR="${MINERU_HOME:-/root/.mineru}"
MINERU_MODEL_DIR="${MINERU_MODEL_DIR:-$MINERU_HOME_DIR/models}"
MINERU_CACHE_DIR="${MINERU_HOME_DIR}"

echo "=========================================="
echo "MinerU OCR - Model Initialization"
echo "=========================================="
echo ""
echo "MinerU home: $MINERU_HOME_DIR"
echo "Model directory: $MINERU_MODEL_DIR"
echo ""

# Create directories
mkdir -p "$MINERU_MODEL_DIR"

# Check if PDF-Extract-Kit already exists
if [ -d "$MINERU_MODEL_DIR/PDF-Extract-Kit-1.0" ]; then
    echo "✓ Models already exist at $MINERU_MODEL_DIR"
    echo "  Skipping download. To re-download, delete the cache directory."
    exit 0
fi

echo "Downloading OCR models..."
echo ""

# Download models using MinerU's download script
cd /app
python3 /app/docker/download_prod_models.py

# Move downloaded models to expected location
if [ -d "$MINERU_CACHE_DIR/modelscope/PDF-Extract-Kit-1.0" ]; then
    echo ""
    echo "Moving models to $MINERU_MODEL_DIR..."
    mv "$MINERU_CACHE_DIR/modelscope/PDF-Extract-Kit-1.0" "$MINERU_MODEL_DIR/"
fi

echo ""
echo "=========================================="
echo "Model initialization complete!"
echo "=========================================="
echo ""
echo "Models are stored at: $MINERU_MODEL_DIR"
