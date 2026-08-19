"""VietOCR Seq2Seq recognizer adapter for MinerU text crops."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Optional

import numpy as np
from PIL import Image


class VietOCRSeq2SeqRecognizer:
    """Adapt VietOCR's single-image predictor to MinerU's recognizer contract."""

    def __init__(
        self,
        device: Optional[str] = None,
        predictor: Any = None,
        predictor_factory: Optional[Callable[[], Any]] = None,
    ) -> None:
        if device is None:
            try:
                import torch
            except ImportError:
                device = "cpu"
            else:
                device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device
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
        if crop.ndim != 3 or crop.shape[2] != 3:
            raise ValueError(f"VietOCR expects an HWC BGR crop, got shape {crop.shape}")
        rgb_crop = crop[:, :, ::-1]
        return Image.fromarray(rgb_crop)

    def __call__(self, img_crop_list: Sequence[np.ndarray], **kwargs: Any) -> tuple[list[tuple[str, float]], float]:
        del kwargs
        predictor = self._get_predictor()
        results: list[tuple[str, float]] = []
        for crop in img_crop_list:
            text = predictor.predict(self._crop_to_pil(crop))
            text = str(text or "")
            results.append((text, 1.0 if text.strip() else 0.0))
        return results, 0.0
