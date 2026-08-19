#!/usr/bin/env python3
"""Download only OCR-production models for MinerU Vietnamese OCR pipeline.

This script downloads only the models needed for:
- Layout detection (PP-DocLayoutV2)
- Text detection (PP-OCRv6 small det ONNX)
- Vietnamese text recognition (VietOCR vgg_seq2seq - downloaded by vietocr package)
- Table detection/recognition (SLANet+, Table classifier)
- Seal detection (PP-OCR seal models)

NOT downloaded:
- VLM models (MinerU2.5-Pro)
- Formula models (if not needed)
- PaddleOCR text recognizers (using VietOCR instead)
- All 23 other OCR language models in paddleocr_torch folder
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mineru.utils.model_registry import (
    PDF_EXTRACT_KIT,
    PP_DOCLAYOUT_V2_ONNX,
    PP_OCR_V6_SMALL_DET_ONNX,
)


def download_ocr_models():
    """Download only OCR-production model weights."""
    print("=" * 60)
    print("MinerU OCR Production - Model Downloader")
    print("=" * 60)
    print()
    print("This will download only OCR/table/seal models:")
    print("  - PP-DocLayoutV2 (layout) - ONNX")
    print("  - PP-OCRv6 small detector - ONNX")
    print("  - SLANet+ (table recognition) - ONNX")
    print("  - Table classifier - ONNX")
    print("  - Seal detector (server/lite)")
    print()
    print("NOT downloading:")
    print("  - VLM models (MinerU2.5-Pro)")
    print("  - Formula models (unimernet)")
    print("  - PaddleOCR text recognizers (using VietOCR)")
    print("  - 23 other OCR language models")
    print()

    downloaded = []
    failed = []

    # 1. Layout model - ONNX version (lighter, ~214 MB)
    print("[1/5] Downloading PP-DocLayoutV2 (layout - ONNX)...")
    try:
        PP_DOCLAYOUT_V2_ONNX.ensure()
        downloaded.append("PP-DocLayoutV2 ONNX")
    except Exception as e:
        print(f"  WARNING: {e}")
        failed.append("PP-DocLayoutV2 ONNX")

    # 2. Text detector - ONNX version (~10 MB)
    print("[2/5] Downloading PP-OCRv6 small detector (ONNX)...")
    try:
        PP_OCR_V6_SMALL_DET_ONNX.ensure()
        downloaded.append("PP-OCRv6-small-det ONNX")
    except Exception as e:
        print(f"  WARNING: {e}")
        failed.append("PP-OCRv6-small-det ONNX")

    # 3. OCR models from PDF Extract Kit - SEAL ONLY
    print("[3/5] Downloading OCR models (seal detection only)...")

    # Only download seal detector models, not all 25 OCR models
    try:
        # Seal detector server (GPU) - 114 MB
        print("  - Downloading seal_PP-OCRv4_det_server (GPU)...")
        PDF_EXTRACT_KIT.seal_det_server.ensure()
        downloaded.append("seal_det_server")

        # Seal detector lite (CPU) - 14.5 MB
        print("  - Downloading seal_PP-OCRv4_det_lite (CPU)...")
        PDF_EXTRACT_KIT.seal_det_lite.ensure()
        downloaded.append("seal_det_lite")
    except Exception as e:
        print(f"  WARNING: {e}")
        failed.append("Seal detectors")

    # 4. Table models - ONNX versions
    print("[4/5] Downloading table models...")
    try:
        # SLANet+ - 7.76 MB
        print("  - Downloading slanet-plus.onnx...")
        PDF_EXTRACT_KIT.slanet_plus.ensure()
        downloaded.append("slanet_plus")

        # Table classifier - 6.78 MB
        print("  - Downloading table classifier...")
        PDF_EXTRACT_KIT.paddle_table_cls.ensure()
        downloaded.append("table_cls")
    except Exception as e:
        print(f"  WARNING: {e}")
        failed.append("Table models")

    # 5. VietOCR
    print("[5/5] VietOCR vgg_seq2seq...")
    print("  (Downloaded automatically by vietocr package at runtime)")
    downloaded.append("vietocr (runtime)")

    # Summary
    print()
    print("=" * 60)
    print("Download Summary")
    print("=" * 60)
    print(f"Successfully: {len(downloaded)} items")
    for name in downloaded:
        print(f"  ✓ {name}")
    if failed:
        print(f"\nFailed/skipped: {len(failed)}")
        for name in failed:
            print(f"  ✗ {name}")
    print()
    print("Estimated disk usage:")
    print("  - PP-DocLayoutV2 ONNX: ~214 MB")
    print("  - PP-OCRv6 detector ONNX: ~10 MB")
    print("  - Seal detectors: ~129 MB")
    print("  - Table models: ~15 MB")
    print("  - VietOCR (runtime): ~200 MB")
    print("  - Total estimate: ~568 MB")
    print()
    print("Next steps:")
    print("  1. Build: docker build -f docker/Dockerfile.ocr-prod -t mineru-ocr-vi:prod .")
    print("  2. Run: docker compose -f docker/compose.ocr-prod.yaml up")
    print()


if __name__ == "__main__":
    download_ocr_models()
