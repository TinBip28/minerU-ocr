#!/bin/bash
# Build and compare Docker images for MinerU OCR production
# Usage: ./scripts/build_and_compare.sh [baseline|slim|all]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "=========================================="
echo "MinerU OCR - Docker Build Comparison"
echo "=========================================="
echo ""

# Build baseline image
build_baseline() {
    echo "[1/2] Building baseline image (current Dockerfile.ocr-prod)..."
    docker build \
        -f docker/Dockerfile.ocr-prod \
        -t mineru-ocr-vi:baseline .

    echo ""
    echo "Baseline image size:"
    docker image ls mineru-ocr-vi:baseline | tail -1
}

# Build slim image
build_slim() {
    echo "[2/2] Building slim image (Dockerfile.ocr-slim)..."
    docker build \
        -f docker/Dockerfile.ocr-slim \
        -t mineru-ocr-vi:slim .

    echo ""
    echo "Slim image size:"
    docker image ls mineru-ocr-vi:slim | tail -1
}

# Compare sizes
compare() {
    echo ""
    echo "=========================================="
    echo "Comparison"
    echo "=========================================="

    BASELINE_SIZE=$(docker image inspect mineru-ocr-vi:baseline --format='{{.Size}}' 2>/dev/null || echo "0")
    SLIM_SIZE=$(docker image inspect mineru-ocr-vi:slim --format='{{.Size}}' 2>/dev/null || echo "0")

    if [ "$BASELINE_SIZE" != "0" ] && [ "$SLIM_SIZE" != "0" ]; then
        BASELINE_GB=$(echo "scale=2; $BASELINE_SIZE/1024/1024/1024" | bc)
        SLIM_GB=$(echo "scale=2; $SLIM_SIZE/1024/1024/1024" | bc)
        SAVINGS=$(echo "scale=2; ($BASELINE_SIZE - $SLIM_SIZE)/1024/1024/1024" | bc)
        PERCENT=$(echo "scale=1; ($BASELINE_SIZE - $SLIM_SIZE)*100/$BASELINE_SIZE" | bc)

        echo "Baseline: $BASELINE_GB GB"
        echo "Slim:     $SLIM_GB GB"
        echo "Savings:  $SAVINGS GB ($PERCENT%)"
    else
        echo "Cannot compare - one or both images not found"
        echo "Baseline: $(docker image ls mineru-ocr-vi:baseline --format='{{.Size}}' 2>/dev/null || echo 'N/A')"
        echo "Slim:     $(docker image ls mineru-ocr-vi:slim --format='{{.Size}}' 2>/dev/null || echo 'N/A')"
    fi
}

# Main
case "${1:-all}" in
    baseline)
        build_baseline
        ;;
    slim)
        build_slim
        ;;
    all)
        build_baseline
        echo ""
        build_slim
        compare
        ;;
    compare)
        compare
        ;;
    *)
        echo "Usage: $0 [baseline|slim|all|compare]"
        exit 1
        ;;
esac
