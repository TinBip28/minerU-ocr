"""Tests for VietOCRSeq2SeqRecognizer with batch inference and real confidence."""

from __future__ import annotations

from typing import Optional, Union

import numpy as np
from PIL import Image

from mineru.model.ocr.vietocr_seq2seq import VietOCRSeq2SeqRecognizer


class RecordingPredictor:
    """Mock predictor that records calls and returns configured results."""

    def __init__(self, predictions: list[tuple[str, Optional[float]]]):
        """Initialize with list of (text, prob) tuples."""
        self.predictions = iter(predictions)
        self.images: list[Image.Image] = []
        self.batch_calls: list[list[Image.Image]] = []
        self.single_calls: list[Image.Image] = []

    def predict(self, image: Image.Image, return_prob: bool = False) -> tuple[str, float]:
        """Record single-image prediction."""
        self.single_calls.append(image)
        text, prob = next(self.predictions)
        if return_prob:
            prob_value = prob if prob is not None else (1.0 if text else 0.0)
            return text, prob_value
        return text

    def predict_batch(
        self, images: list[Image.Image], return_prob: bool = False
    ) -> tuple[list[str], list[float]] | list[str]:
        """Record batch prediction.

        Returns (texts, probs) tuple matching VietOCR's actual API.
        """
        self.batch_calls.append(images)
        texts = []
        probs = []
        for _ in range(len(images)):
            text, prob = next(self.predictions)
            texts.append(text)
            if return_prob:
                probs.append(prob if prob is not None else (1.0 if text else 0.0))
        if return_prob:
            return texts, probs
        return texts


class TestCropConversion:
    """Test BGR to PIL RGB conversion."""

    def test_bgr_to_rgb_conversion(self):
        """Input BGR numpy array should become PIL RGB image."""
        predictor = RecordingPredictor([("text", 1.0)])
        recognizer = VietOCRSeq2SeqRecognizer(predictor=predictor)

        # BGR pixel (0, 0, 255) should become RGB (255, 0, 0)
        crops = [np.array([[[0, 0, 255]]], dtype=np.uint8)]
        recognizer(crops)

        # Check PIL image was created correctly (batch mode stores in batch_calls)
        assert len(predictor.batch_calls) == 1
        pil_image = predictor.batch_calls[0][0]
        assert pil_image.mode == "RGB"
        assert pil_image.getpixel((0, 0)) == (255, 0, 0)


class TestOrderPreservation:
    """Test that batch predictions maintain order."""

    def test_predictions_in_order(self):
        """Batch results should match input order."""
        predictor = RecordingPredictor([
            ("Một", 0.98),
            ("Hai", 0.73),
            ("Ba", 0.85),
        ])
        recognizer = VietOCRSeq2SeqRecognizer(predictor=predictor, batch_size=10)

        crops = [
            np.array([[[0, 0, 255]]], dtype=np.uint8),
            np.array([[[0, 255, 0]]], dtype=np.uint8),
            np.array([[[255, 0, 0]]], dtype=np.uint8),
        ]
        results, _ = recognizer(crops)

        assert results[0] == ("Một", 0.98)
        assert results[1] == ("Hai", 0.73)
        assert results[2] == ("Ba", 0.85)


class TestConfidenceScores:
    """Test real confidence scores from VietOCR."""

    def test_real_confidence_returned(self):
        """VietOCR confidence should be passed through."""
        predictor = RecordingPredictor([
            ("VT-01/2025-A", 0.982),
            ("VT-01/202S-A", 0.741),
        ])
        recognizer = VietOCRSeq2SeqRecognizer(predictor=predictor)

        crops = [
            np.array([[[0, 0, 255]]], dtype=np.uint8),
            np.array([[[0, 255, 0]]], dtype=np.uint8),
        ]
        results, _ = recognizer(crops)

        assert results[0] == ("VT-01/2025-A", 0.982)
        assert results[1] == ("VT-01/202S-A", 0.741)

    def test_numpy_array_prob_converted(self):
        """numpy array probabilities should be converted to float."""
        predictor = RecordingPredictor([
            ("text", np.array([0.9, 0.8, 0.95, 0.85])),
        ])
        recognizer = VietOCRSeq2SeqRecognizer(predictor=predictor)

        crops = [np.array([[[0, 0, 255]]], dtype=np.uint8)]
        results, _ = recognizer(crops)

        # Mean of [0.9, 0.8, 0.95, 0.85] = 0.875
        assert abs(results[0][1] - 0.875) < 0.01

    def test_none_prob_fallback(self):
        """None probability should fall back to 1.0/0.0 based on text."""
        predictor = RecordingPredictor([
            ("Valid text", None),
            ("", None),
        ])
        recognizer = VietOCRSeq2SeqRecognizer(predictor=predictor)

        crops = [
            np.array([[[0, 0, 255]]], dtype=np.uint8),
            np.array([[[0, 255, 0]]], dtype=np.uint8),
        ]
        results, _ = recognizer(crops)

        assert results[0] == ("Valid text", 1.0)
        assert results[1] == ("", 0.0)


class TestLazyLoading:
    """Test that predictor is loaded lazily."""

    def test_predictor_created_once(self):
        """Predictor factory should only be called once."""
        created = []
        # Provide 2 predictions for 2 calls
        predictor = RecordingPredictor([("text", 1.0), ("text", 1.0)])
        recognizer = VietOCRSeq2SeqRecognizer(
            predictor_factory=lambda: (created.append(predictor) or predictor),
        )

        recognizer([np.zeros((1, 1, 3), dtype=np.uint8)])
        recognizer([np.zeros((1, 1, 3), dtype=np.uint8)])

        assert len(created) == 1


class TestBatchSplitting:
    """Test batch size splitting logic."""

    def test_batches_split_correctly(self):
        """5 crops with batch_size=2 should create 3 batches: 2, 2, 1."""
        predictor = RecordingPredictor([
            ("a", 1.0), ("b", 1.0), ("c", 1.0), ("d", 1.0), ("e", 1.0)
        ])
        recognizer = VietOCRSeq2SeqRecognizer(predictor=predictor, batch_size=2)

        crops = [np.zeros((1, 1, 3), dtype=np.uint8) for _ in range(5)]
        recognizer(crops)

        # Should have 3 batch calls
        assert len(predictor.batch_calls) == 3
        assert len(predictor.batch_calls[0]) == 2
        assert len(predictor.batch_calls[1]) == 2
        assert len(predictor.batch_calls[2]) == 1


class TestEmptyInput:
    """Test handling of empty input."""

    def test_empty_list_returns_empty(self):
        """Empty crop list should return empty results."""
        predictor = RecordingPredictor([])
        recognizer = VietOCRSeq2SeqRecognizer(predictor=predictor)

        results, elapsed = recognizer([])

        assert results == []
        assert elapsed == 0.0


class TestTiming:
    """Test that elapsed time is recorded."""

    def test_elapsed_time_recorded(self):
        """Elapsed time should be returned, not 0.0."""
        predictor = RecordingPredictor([("text", 1.0)])
        recognizer = VietOCRSeq2SeqRecognizer(predictor=predictor)

        crops = [np.zeros((10, 10, 3), dtype=np.uint8)]
        results, elapsed = recognizer(crops)

        # Should have non-zero elapsed time
        assert elapsed > 0


class TestBatchInferenceFallback:
    """Test fallback to single inference when batch not available."""

    def test_fallback_when_no_batch_method(self):
        """Should use predict() when predict_batch() not available."""

        class NoBatchPredictor:
            def __init__(self):
                self.calls = []

            def predict(self, image, return_prob=False):
                self.calls.append(image)
                return "result", 0.95

        predictor = NoBatchPredictor()
        recognizer = VietOCRSeq2SeqRecognizer(predictor=predictor, batch_size=64)

        crops = [np.zeros((1, 1, 3), dtype=np.uint8)]
        results, _ = recognizer(crops)

        assert len(predictor.calls) == 1
        assert results[0] == ("result", 0.95)


class TestPillowCompatibility:
    """Test Pillow ANTIALIAS compatibility fix."""

    def test_antialias_restored(self, monkeypatch):
        """ANTIALIAS should be restored if missing."""
        monkeypatch.delattr(Image, "ANTIALIAS", raising=False)
        predictor = RecordingPredictor([("text", 1.0)])

        recognizer = VietOCRSeq2SeqRecognizer(predictor=predictor)
        recognizer._ensure_pillow_compatibility()

        assert Image.ANTIALIAS == Image.Resampling.LANCZOS


class TestBatchSizeValidation:
    """Test batch_size parameter validation."""

    def test_negative_batch_size_becomes_one(self):
        """Negative batch_size should be clamped to 1."""
        predictor = RecordingPredictor([("text", 1.0)])
        recognizer = VietOCRSeq2SeqRecognizer(predictor=predictor, batch_size=-5)

        assert recognizer.batch_size == 1

    def test_zero_batch_size_becomes_one(self):
        """Zero batch_size should be clamped to 1."""
        predictor = RecordingPredictor([("text", 1.0)])
        recognizer = VietOCRSeq2SeqRecognizer(predictor=predictor, batch_size=0)

        assert recognizer.batch_size == 1
