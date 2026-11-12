# Day-18 Stability Improvements

## Implemented

1. Early PDF validation and 10 MB file-size limit.
2. Controlled HTTP errors for invalid/unsupported files.
3. API timing and operational logging.
4. PDF extraction fallback for pages with poor text extraction.
5. Resource-safe PDF handling using context managers.
6. Explicit cleanup after background ATS processing.
7. Blocking service calls moved off the FastAPI event loop in async routes.

## Verification to perform

1. Start the ATS API.
2. Run all six Day-17 scoring test cases again.
3. Upload a normal PDF.
4. Upload an oversized PDF and confirm HTTP 413.
5. Upload a non-PDF and confirm HTTP 400.
6. Test a noisy/poorly formatted PDF.
7. Compare `/ats/score` latency using the benchmark script.
8. Check the `X-Process-Time-MS` response header.
9. Check application logs for timing entries.
