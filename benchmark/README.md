# MinerU OCR Production - Benchmark Corpus

## Purpose
Representative PDF samples for regression testing after Docker image changes.

## Corpus (5 files minimum)

| # | File | Type | Purpose |
|---|------|------|---------|
| 1 | text_vi.pdf | Vietnamese text | Verify diacritics, reading order |
| 2 | table_complex.pdf | Multi-row/merged cells | Table structure correctness |
| 3 | seal_invoice.pdf | Seal + text | Seal detection and OCR |
| 4 | mixed_page.pdf | Text + table + seal | Full integration |
| 5 | degraded_scan.pdf | Low quality / skew | Robustness |

## Usage

```bash
# Run benchmark
mineru-kit parse --pdf ./benchmark/input --output ./benchmark/results

# Compare with baseline
diff -rq ./benchmark/results ./benchmark/baseline
```

## Baseline Outputs

Place reference markdown and JSON outputs here after verification.
