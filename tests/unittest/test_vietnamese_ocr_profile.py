from pathlib import Path

from mineru.utils.ocr_language import normalize_ocr_model_lang, validate_public_ocr_lang

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "mineru/model/utils/pytorchocr/utils/resources/models_config.yml"


def test_vi_and_vietocr_seq2seq_are_public_ocr_languages():
    assert validate_public_ocr_lang("vi") == "vi"
    assert validate_public_ocr_lang("vi_vietocr_seq2seq") == "vi_vietocr_seq2seq"
    assert normalize_ocr_model_lang("vi") == "vi_vietocr_seq2seq"
    assert normalize_ocr_model_lang("vi_vietocr_seq2seq") == "vi_vietocr_seq2seq"


def test_vietocr_seq2seq_profile_is_configured_with_ppocrv6_detector():
    config = CONFIG.read_text(encoding="utf-8")

    assert "  vi_vietocr_seq2seq:" in config
    assert "det: ch_PP-OCRv6_small_det_infer.safetensors" in config
