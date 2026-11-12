"""
Day-18 ATS Performance Benchmark
--------------------------------
Measures:
1. JD/resume text extraction time for local files.
2. /ats/score API latency when the server is running.

Run:
    python performance_benchmark.py --file path/to/resume.pdf
    python performance_benchmark.py --url http://127.0.0.1:8000/ats/score --payload payload.json

The script reports measured values only; it does not invent baseline/optimized numbers.
"""
import argparse
import json
import statistics
import time
import tracemalloc
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None


def measure(fn, runs=5):
    samples = []
    for _ in range(runs):
        start = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - start) * 1000)
    return {
        "runs": runs,
        "min_ms": min(samples),
        "avg_ms": statistics.mean(samples),
        "max_ms": max(samples),
    }


def measure_extraction(path):
    # Import the optimized parser lazily so the script can also be used
    # for API-only benchmarking.
    from jd_parser_day18_optimized import JDParser
    parser = JDParser()
    return measure(lambda: parser.extract_text(str(path)))


def measure_memory(fn):
    tracemalloc.start()
    fn()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {"current_kb": current / 1024, "peak_kb": peak / 1024}


def measure_api(url, payload):
    if requests is None:
        raise RuntimeError("Install requests to run API benchmarking: pip install requests")
    return measure(
        lambda: requests.post(
            url,
            json=payload,
            headers={"Accept": "application/json"},
            timeout=120,
        ),
        runs=5,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path)
    parser.add_argument("--url")
    parser.add_argument("--payload", type=Path)
    args = parser.parse_args()

    if args.file:
        result = measure_extraction(args.file)
        memory = measure_memory(
            lambda: __import__("jd_parser_day18_optimized").JDParser().extract_text(str(args.file))
        )
        print(json.dumps({"extraction": result, "memory": memory}, indent=2))

    if args.url and args.payload:
        payload = json.loads(args.payload.read_text(encoding="utf-8"))
        result = measure_api(args.url, payload)
        print(json.dumps({"api_latency": result}, indent=2))

    if not args.file and not (args.url and args.payload):
        parser.error("Provide --file or both --url and --payload")


if __name__ == "__main__":
    main()
