import numpy as np
from PIL import Image

from mineru.model.ocr.vietocr_seq2seq import VietOCRSeq2SeqRecognizer


class RecordingPredictor:
    def __init__(self, predictions):
        self.predictions = iter(predictions)
        self.images = []

    def predict(self, image):
        self.images.append(image)
        return next(self.predictions)


def test_predicts_pil_rgb_crops_in_order_with_compatible_scores():
    predictor = RecordingPredictor(["Một", ""])
    recognizer = VietOCRSeq2SeqRecognizer(predictor=predictor)
    crops = [
        np.array([[[0, 0, 255]]], dtype=np.uint8),
        np.array([[[255, 0, 0]]], dtype=np.uint8),
    ]

    result, _ = recognizer(crops)

    assert result == [("Một", 1.0), ("", 0.0)]
    assert all(isinstance(image, Image.Image) for image in predictor.images)
    assert predictor.images[0].mode == "RGB"
    assert predictor.images[0].getpixel((0, 0)) == (255, 0, 0)


def test_predictor_is_created_lazily():
    created = []
    predictor = RecordingPredictor(["text", "text"])
    recognizer = VietOCRSeq2SeqRecognizer(
        predictor_factory=lambda: created.append(predictor) or predictor,
    )

    recognizer([np.zeros((1, 1, 3), dtype=np.uint8)])
    recognizer([np.zeros((1, 1, 3), dtype=np.uint8)])

    assert created == [predictor]


def test_pillow_compatibility_restores_vietocr_antialias_alias(monkeypatch):
    monkeypatch.delattr(Image, "ANTIALIAS", raising=False)

    recognizer = VietOCRSeq2SeqRecognizer(predictor=RecordingPredictor([]))
    recognizer._ensure_pillow_compatibility()

    assert Image.ANTIALIAS == Image.Resampling.LANCZOS
