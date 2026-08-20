#!/bin/bash
# Measure Docker image sizes for MinerU OCR production

set -e

IMAGE_NAME="${1:-mineru-ocr-vi}"
TAG="${2:-latest}"

echo "=========================================="
echo "Docker Image Size Measurement"
echo "Image: $IMAGE_NAME:$TAG"
echo "=========================================="
echo ""

# 1. Basic image info
echo "1. Image ID and Size"
docker image ls "$IMAGE_NAME:$TAG" | tail -1
echo ""

# 2. Raw size in bytes
echo "2. Raw Size (bytes)"
SIZE=$(docker image inspect "$IMAGE_NAME:$TAG" --format='{{.Size}}')
echo "$SIZE bytes"
echo "   = $(echo "scale=2; $SIZE/1024/1024/1024" | bc) GB"
echo ""

# 3. Layer analysis
echo "3. Layer Breakdown (top 10 largest)"
docker history --no-trunc "$IMAGE_NAME:$TAG" --format '{{.Size}}\t{{.CreatedBy}}' \
    | head -20 \
    | sort -rn \
    | head -10
echo ""

# 4. Directory sizes inside container
echo "4. Directory Sizes Inside Container"
docker run --rm --entrypoint /bin/bash "$IMAGE_NAME:$TAG" -c '
    echo "Python packages:"
    du -sh /usr/local/lib/python3*/dist-packages/* 2>/dev/null | sort -rh | head -10
    echo ""
    echo "Application:"
    du -sh /app 2>/dev/null || echo "/app not found"
    echo ""
    echo "CUDA libraries:"
    du -sh /usr/local/cuda* 2>/dev/null || echo "CUDA not at standard path"
    echo ""
    echo "Models (if any):"
    du -sh /root/.mineru 2>/dev/null || du -sh /root/.cache 2>/dev/null || echo "No model cache"
' 2>/dev/null || echo "Container run failed (image may not exist)"
echo ""

# 5. Summary
echo "=========================================="
echo "Summary"
echo "=========================================="
echo "Registry/Compressed: $(echo "scale=2; $SIZE/1024/1024/1024" | bc) GB"
echo ""
