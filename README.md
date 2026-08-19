<div align="center">

# MinerU-OCR (Vietnamese Edition) 🇻🇳

[![Repository](https://img.shields.io/badge/GitHub-TinBip28%2FminerU--ocr-blue.svg?logo=github)](https://github.com/TinBip28/minerU-ocr)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MinerU%20Open%20Source-green.svg)](LICENSE.md)
[![VietOCR](https://img.shields.io/badge/OCR-VietOCR%20Seq2Seq-orange.svg)](https://github.com/pbcquoc/vietocr)
[![PaddleOCR](https://img.shields.io/badge/Detector-PP--OCRv6-red.svg)](https://github.com/PaddlePaddle/PaddleOCR)

<p align="center">
  <b>Công cụ trích xuất tài liệu thông minh và OCR tiếng Việt nâng cao</b><br>
  Tích hợp <b>PP-OCRv6 Text Detector</b> + <b>VietOCR Seq2Seq Recognizer</b> trên nền tảng <b>MinerU v4</b>
</p>

</div>

---

## 🌟 Giới thiệu (Overview)

**MinerU-OCR** là phiên bản tùy biến chuyên sâu cho tài liệu tiếng Việt, được phát triển trên nền tảng **MinerU v4.0.0-alpha** thế hệ mới kết hợp với công nghệ nhận diện chữ tiếng Việt **VietOCR**:

* **🔍 Bộ phát hiện vùng văn bản PP-OCRv6 (Text Detector):** Định vị chính xác từng khối văn bản, bảng biểu và dòng chữ ngay cả trên các bản quét chất lượng thấp hoặc góc nghiêng.
* **✍️ Bộ nhận diện chữ VietOCR Seq2Seq (Text Recognizer):** Sử dụng kiến trúc `vgg_seq2seq` tối ưu hóa độ chính xác dấu tiếng Việt, từ vựng chuyên ngành và văn bản pháp lý.
* **📊 Trích xuất đa định dạng:** Chuyển đổi PDF (bản quét & điện tử), DOCX, PPTX, XLSX, hình ảnh sang Markdown và JSON có cấu trúc.
* **⚡ Kiến trúc MinerU v4:** Tối ưu hóa hiệu năng với ONNX Runtime, hỗ trợ CLI `mineru` và `mineru-kit`.

---

## 🚀 Cài đặt (Installation)

### 1. Clone repository
```bash
git clone https://github.com/TinBip28/minerU-ocr.git
cd minerU-ocr
```

### 2. Cài đặt môi trường & dependencies
```bash
# Cài đặt gói cơ bản và PyTorch / VietOCR
pip install -e ".[torch]"

# Hoặc cài đặt đầy đủ tất cả các backend
pip install -e ".[all]"
```

---

## 📖 Hướng dẫn sử dụng (Usage)

### 1. Trích xuất tài liệu tiếng Việt qua CLI

Chạy lệnh trích xuất với tham số ngôn ngữ `--lang vi` (hoặc `--lang vi_vietocr_seq2seq`):

```bash
# Trích xuất file PDF sang Markdown
mineru parse -p /duong/dan/tai_lieu.pdf -o ./output --lang vi

# Trích xuất hình ảnh scan
mineru parse -p /duong/dan/anh_scan.png -o ./output --lang vi
```

### 2. Sử dụng trong Python script

```python
from mineru.model.ocr.pytorch_paddle import PytorchPaddleOCR
import cv2

# Khởi tạo OCR engine với profile tiếng Việt
ocr_engine = PytorchPaddleOCR(lang="vi")

# Đọc ảnh và nhận diện
image = cv2.imread("document_sample.png")
boxes, results = ocr_engine(image)

for box, (text, score) in zip(boxes, results):
    print(f"BBox: {box} -> Text: {text} (Score: {score:.2f})")
```

---

## 🧪 Kiểm thử (Testing)

Chạy bộ unit test để kiểm tra hoạt động của VietOCR Seq2Seq và profile tiếng Việt:

```bash
python3 -m pytest tests/unittest/test_vietocr_seq2seq.py tests/unittest/test_vietnamese_ocr_profile.py -v
```

---

## 🤝 Ghi nhận đóng góp & Bản quyền (Credits & Attribution)

* Dự án được xây dựng và phát triển trên nền tảng nguồn mở [MinerU](https://github.com/opendatalab/MinerU) của **OpenDataLab**.
* Tích hợp bộ nhận diện [VietOCR](https://github.com/pbcquoc/vietocr) của tác giả **Phạm Bá Quốc (pbcquoc)**.
* Mô hình phát hiện văn bản dựa trên [PaddleOCR PP-OCRv6](https://github.com/PaddlePaddle/PaddleOCR) từ **Baidu PaddlePaddle**.
