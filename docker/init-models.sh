#!/bin/bash
# Initialize MinerU OCR models from external volume
# Usage: docker compose run --rm init-models

set -e

MODELS_DIR="${MINERU_MODEL_DIR:-/models}"
CACHE_DIR="${HOME}/.cache/modelscope"

echo "=========================================="
echo "MinerU OCR - Model Initialization"
echo "=========================================="
echo ""
echo "Models directory: $MODELS_DIR"
echo "Cache directory: $CACHE_DIR"
echo ""

# Create directories
mkdir -p "$MODELS_DIR"
mkdir -p "$CACHE_DIR"

# Check if models already exist
if [ -d "$CACHE_DIR/PDF-Extract-Kit-1.0" ]; then
    echo "✓ Models already exist at $CACHE_DIR"
    echo "  Skipping download. To re-download, delete the cache directory."
    exit 0
fi

echo "Downloading OCR models..."
echo ""

# Download models using MinerU's download script
python3 /app/docker/download_prod_models.py

# Create symlink if needed
if [ "$MODELS_DIR" != "$CACHE_DIR" ]; then
    echo ""
    echo "Symlinking models to $MODELS_DIR..."
    ln -sf "$CACHE_DIR" "$MODELS_DIR/cache"
fi

echo ""
echo "=========================================="
echo "Model initialization complete!"
echo "=========================================="
