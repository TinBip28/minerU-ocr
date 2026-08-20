"""VietOCR Seq2Seq recognizer adapter for MinerU text crops."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from time import perf_counter
from typing import Any, Optional

import numpy as np
from PIL import Image


class VietOCRSeq2SeqRecognizer:
    """Adapt VietOCR's single-image predictor to MinerU's recognizer contract.

    Optimized for batch inference with real confidence scores.
    """

    def __init__(
        self,
        device: Optional[str] = None,
        predictor: Any = None,
        predictor_factory: Optional[Callable[[], Any]] = None,
        batch_size: int = 64,
    ) -> None:
        if device is None:
            try:
                import torch
            except ImportError:
                device = "cpu"
            else:
                device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device
        self.batch_size = max(1, int(batch_size))
        self._predictor = predictor
        self._predictor_factory = predictor_factory or self._load_predictor

    def _load_predictor(self) -> Any:
        self._ensure_pillow_compatibility()
        from vietocr.tool.config import Cfg
        from vietocr.tool.predictor import Predictor

        config = Cfg.load_config_from_name("vgg_seq2seq")
        config["device"] = self.device
        config.setdefault("predictor", {})["beamsearch"] = False
        return Predictor(config)

    @staticmethod
    def _ensure_pillow_compatibility() -> None:
        """Restore the Pillow alias used by released VietOCR versions."""
        if not hasattr(Image, "ANTIALIAS"):
            resampling = getattr(Image, "Resampling", Image)
            Image.ANTIALIAS = resampling.LANCZOS

    def _get_predictor(self) -> Any:
        if self._predictor is None:
            self._predictor = self._predictor_factory()
        return self._predictor

    @staticmethod
    def _crop_to_pil(crop: np.ndarray) -> Image.Image:
        """Convert BGR numpy array (HWC) to PIL RGB Image."""
        if crop.ndim != 3 or crop.shape[2] != 3:
            raise ValueError(f"VietOCR expects an HWC BGR crop, got shape {crop.shape}")
        rgb_crop = crop[:, :, ::-1]
        return Image.fromarray(rgb_crop)

    def __call__(
        self,
        img_crop_list: Sequence[np.ndarray],
        **kwargs: Any,
    ) -> tuple[list[tuple[str, float]], float]:
        """Recognize text from image crops with batch inference.

        Args:
            img_crop_list: List of BGR numpy arrays (HWC format).
            **kwargs: Ignored, for API compatibility.

        Returns:
            Tuple of (list of (text, confidence) tuples, elapsed_ms).
        """
        del kwargs

        if not img_crop_list:
            return [], 0.0

        predictor = self._get_predictor()
        started_at = perf_counter()

        # Convert all crops to PIL images
        images = [self._crop_to_pil(crop) for crop in img_crop_list]

        # Try batch inference first, fall back to sequential if not available
        results: list[tuple[str, float]] = []

        if hasattr(predictor, "predict_batch"):
            # Batch inference: process in chunks
            # VietOCR predict_batch returns (texts: list[str], probs: list[float|None])
            for start in range(0, len(images), self.batch_size):
                batch = images[start : start + self.batch_size]
                texts, probs = predictor.predict_batch(batch, return_prob=True)
                for text, prob in zip(texts, probs):
                    normalized_text = str(text or "")
                    # Handle prob: can be float, numpy array, or None
                    if prob is None:
                        normalized_score = 1.0 if normalized_text.strip() else 0.0
                    elif isinstance(prob, np.ndarray):
                        normalized_score = float(np.mean(prob))
                    else:
                        normalized_score = float(prob)
                    results.append((normalized_text, normalized_score))
        else:
            # Fallback: sequential inference
            for image in images:
                text, prob = predictor.predict(image, return_prob=True)
                normalized_text = str(text or "")
                if prob is None:
                    normalized_score = 1.0 if normalized_text.strip() else 0.0
                elif isinstance(prob, np.ndarray):
                    normalized_score = float(np.mean(prob))
                else:
                    normalized_score = float(prob)
                results.append((normalized_text, normalized_score))

        elapsed = perf_counter() - started_at  # seconds (matching MinerU OCR contract)

        return results, elapsed
