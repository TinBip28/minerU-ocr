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
mineru-kit parse \
    ./benchmark/input \
    -o ./benchmark/results \
    --tier basic \
    --language vi \
    --ocr-mode auto

# Compare with baseline
diff -rq ./benchmark/results ./benchmark/baseline/md
diff -rq ./benchmark/results ./benchmark/baseline/json
```

## Benchmark Outputs

Place reference markdown and JSON outputs here after verification:

```
benchmark/
├── input/
│   ├── text_vi.pdf
│   ├── table_complex.pdf
│   └── ...
├── baseline/
│   ├── md/
│   │   ├── text_vi.md
│   │   └── ...
│   └── json/
│       ├── text_vi.json
│       └── ...
└── results/
    └── ... (output from mineru-kit parse)
```

## Regression Checklist

After any Docker image change:

- [ ] Text PDFs: CER < baseline, Vietnamese diacritics preserved
- [ ] Table PDFs: row count, column count, merged cells match
- [ ] Seal PDFs: seal detected, seal text OCR correct
- [ ] Mixed PDFs: reading order correct
- [ ] Degraded PDFs: no crashes, graceful degradation

## Performance Metrics

Record after each benchmark:

- Average sec/page
- P50 sec/page
- P95 sec/page
- Peak GPU VRAM
- Peak RAM
- Startup time
