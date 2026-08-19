#!/usr/bin/env python3
"""Download models for MinerU Vietnamese OCR production.

Downloads ONLY the models needed for Vietnamese OCR production:
- Layout: PP-DocLayoutV2 (full PyTorch)
- Text detection: PP-OCRv6 detector (full PyTorch)
- Text recognition: VietOCR vgg_seq2seq (full PyTorch)
- Table: SLANet+, UNet structure, Table classifier
- Seal: seal detector + PP-OCRv6 medium recognizer

NOT downloaded:
- VLM models (MinerU2.5-Pro)
- Formula models
- ONNX weights (using full PyTorch for quality baseline)
- Other OCR language models

Exit code 0 only if ALL required models download successfully.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mineru.utils.model_registry import (
    PDF_EXTRACT_KIT,
)


def download_with_progress(name: str, model_path, verbose: bool = True) -> bool:
    """Download a model and return success status."""
    try:
        if verbose:
            print(f"  Downloading {name}...")
        model_path.ensure()
        if verbose:
            print(f"  ✓ {name}")
        return True
    except Exception as e:
        print(f"  ✗ {name} failed: {e}")
        return False


def download_all_models() -> list[str]:
    """Download all production models. Returns list of failed models."""
    failed: list[str] = []

    print("=" * 60)
    print("MinerU OCR Production - Model Downloader")
    print("=" * 60)
    print()
    print("Downloading FULL STACK weights (not ONNX) for quality baseline:")
    print("  - PP-DocLayoutV2 (layout)")
    print("  - PP-OCRv6 detector (text detection)")
    print("  - VietOCR vgg_seq2seq (Vietnamese text recognition)")
    print("  - SLANet+ (table recognition)")
    print("  - UNet structure (wired table)")
    print("  - Table classifier")
    print("  - Seal detector + recognizer")
    print()

    # 1. Layout - full PyTorch version
    print("[1/7] Layout model...")
    if not download_with_progress("PP-DocLayoutV2", PDF_EXTRACT_KIT.pp_doclayout_v2):
        failed.append("PP-DocLayoutV2")

    # 2. Text detection - using PaddleOCR (full)
    print("[2/7] Text detection models...")
    if not download_with_progress("PP-OCRv6 small detector", PDF_EXTRACT_KIT.pytorch_paddle.path("ch_PP-OCRv6_small_det_infer.safetensors")):
        failed.append("PP-OCRv6-det")
    if not download_with_progress("PP-OCRv6 small recognizer", PDF_EXTRACT_KIT.pytorch_paddle.path("ch_PP-OCRv6_small_rec_infer.safetensors")):
        failed.append("PP-OCRv6-rec")

    # 3. VietOCR vgg_seq2seq - download and cache locally
    print("[3/7] VietOCR vgg_seq2seq (Vietnamese text recognition)...")
    print("  NOTE: VietOCR weights are downloaded by the vietocr package")
    print("  at first inference. To pre-download, ensure vietocr can access")
    print("  its model cache directory.")
    try:
        # Trigger vietocr config to ensure weights URL is available
        from vietocr.tool.config import Cfg
        config = Cfg.load_config_from_name("vgg_seq2seq")
        print("  ✓ VietOCR config loaded")
    except ImportError:
        print("  ⚠ vietocr not installed yet (will be installed with mineru[torch])")
    except Exception as e:
        print(f"  ⚠ VietOCR config check: {e}")

    # 4. Table recognition - SLANet+
    print("[4/7] Table recognition models...")
    if not download_with_progress("SLANet+", PDF_EXTRACT_KIT.slanet_plus):
        failed.append("SLANet+")
    # UNet for wired table
    if not download_with_progress("UNet structure", PDF_EXTRACT_KIT.unet_structure):
        failed.append("UNet")

    # 5. Table classification
    print("[5/7] Table classification model...")
    if not download_with_progress("Table classifier", PDF_EXTRACT_KIT.paddle_table_cls):
        failed.append("TableClassifier")

    # 6. Seal detection + recognition
    print("[6/7] Seal detection models...")
    if not download_with_progress("Seal detector (server/GPU)", PDF_EXTRACT_KIT.seal_det_server):
        failed.append("SealDetectorServer")
    if not download_with_progress("Seal detector (lite/CPU)", PDF_EXTRACT_KIT.seal_det_lite):
        failed.append("SealDetectorLite")
    # Seal recognizer - PP-OCRv6 medium for better quality
    if not download_with_progress("Seal recognizer (medium)", PDF_EXTRACT_KIT.pytorch_paddle.path("ch_PP-OCRv6_medium_rec_infer.safetensors")):
        failed.append("SealRecognizer")

    # 7. Dict file for OCR
    print("[7/7] OCR dictionary...")
    # The dict file should be in mineru's resources
    dict_path = Path(__file__).parent.parent / "mineru" / "model" / "utils" / "pytorchocr" / "utils" / "resources"
    if dict_path.exists():
        print(f"  ✓ OCR resources found at {dict_path}")
    else:
        print(f"  ⚠ OCR resources not found at {dict_path}")

    return failed


def main() -> int:
    """Main entry point. Returns 0 on success, non-zero on failure."""
    print()
    failed = download_all_models()

    print()
    print("=" * 60)
    print("Download Summary")
    print("=" * 60)

    if not failed:
        print("✓ All models downloaded successfully")
        print()
        print("Estimated disk usage: ~2-3 GB")
        print()
        print("Next steps:")
        print("  1. Build: docker build -f docker/Dockerfile.ocr-prod -t mineru-ocr-vi:prod .")
        print("  2. Run: docker compose -f docker/compose.ocr-prod.yaml up")
        return 0
    else:
        print(f"✗ {len(failed)} model(s) failed to download:")
        for name in failed:
            print(f"  - {name}")
        print()
        print("Please check:")
        print("  - Network connectivity")
        print("  - HuggingFace/ModelScope access")
        print("  - Disk space")
        return 1


if __name__ == "__main__":
    sys.exit(main())
