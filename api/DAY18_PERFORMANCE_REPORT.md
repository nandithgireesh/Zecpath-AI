# Zecpath Day-18 – Optimization & Performance Tuning

## Objective

Make the ATS more production-ready by improving extraction speed, API/model response handling,
memory behavior, entity/field detection robustness, and noisy-resume handling.

## Existing ATS baseline

The existing integration exposes resume upload/parsing, ATS scoring, ranking, shortlisting,
and asynchronous job processing through FastAPI. The scoring endpoint is `POST /ats/score`.
The existing API also supports background processing for longer operations.

## Implemented Day-18 improvements

### 1. Text extraction speed
- Replaced repeated string concatenation during PDF extraction with list accumulation.
- Uses PyMuPDF direct `get_text("text", sort=True)` for the common case.
- Uses block-based extraction only as a fallback for pages with very little extractable text.
- Uses context-managed PDF opening so resources are closed reliably.
- DOCX extraction now builds the result with a list/join operation.

### 2. Response time
- Added an API timing middleware.
- Every response receives an `X-Process-Time-MS` header.
- Blocking ATS scoring, parsing, ranking and shortlisting work is moved to a threadpool
  from async API routes so the FastAPI event loop is not blocked by synchronous service work.

### 3. Memory handling
- Added a 10 MB upload-size guard before parsing.
- Background ATS processing explicitly releases large temporary objects after completion and
  triggers garbage collection.
- The benchmark script can measure peak Python memory with `tracemalloc`.

### 4. Entity detection / normalization
- Preserved the existing role, skills, experience and education extraction pipeline.
- The optimized parser retains heading normalization and skill synonym normalization.
- The noisy-text fallback reduces the chance of empty/partial PDF extraction causing downstream
  entity detection to fail.

### 5. Noisy resume/JD handling
- PDF extraction falls back to block extraction when direct extraction produces too little text.
- Unsupported or oversized files are rejected early with controlled HTTP errors.
- Existing API exception handling remains in place for controlled failures and logging.

## Performance measurement

Use `performance_benchmark.py` to measure the system before and after applying the optimized
implementation. Record only actual measured values.

| Metric | Before | After | Improvement |
|---|---:|---:|---:|
| PDF extraction average (ms) | TBD | TBD | TBD |
| PDF extraction peak memory (KB) | TBD | TBD | TBD |
| `/ats/score` average latency (ms) | TBD | TBD | TBD |
| `/ats/score` maximum latency (ms) | TBD | TBD | TBD |

## Stability checklist

- [x] File-size validation
- [x] Controlled unsupported-file response
- [x] API processing-time measurement
- [x] Logging of request duration
- [x] PDF resource cleanup
- [x] Fallback extraction for low-text pages
- [x] Background object cleanup
- [ ] Run benchmark against the live local server
- [ ] Verify all existing Day-17 test cases after the optimization
- [ ] Record actual before/after numbers

## Important

The benchmark values are intentionally left as `TBD` until the application is run and measured.
This prevents the report from claiming performance improvements that have not actually been
measured.
