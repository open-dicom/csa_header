"""
Performance benchmarks for CSA header parsing.

Run with: python tests/benchmarks/bench_parsing.py
"""

from __future__ import annotations

import time
from pathlib import Path

from csa_header import CsaHeader

# Test data paths
TEST_FILES_DIR = Path(__file__).parent.parent / "files"
DWI_FILE = TEST_FILES_DIR / "dwi_image_header_info"
E11_FILE = TEST_FILES_DIR / "e11_series_header_info"
RSFMRI_FILE = TEST_FILES_DIR / "rsfmri_series_header_info"


def benchmark_parse(file_path: Path, n_iterations: int = 1000) -> dict[str, float]:
    """
    Benchmark CSA header parsing performance.

    Parameters
    ----------
    file_path : Path
        Path to CSA header test file
    n_iterations : int
        Number of iterations to run

    Returns
    -------
    dict[str, float]
        Performance metrics
    """
    # Load data once
    with open(file_path, "rb") as f:
        raw = f.read()

    # Warm up
    csa = CsaHeader(raw)
    csa.read()

    # Benchmark
    start_time = time.perf_counter()
    for _ in range(n_iterations):
        csa = CsaHeader(raw)
        result = csa.read()
    end_time = time.perf_counter()

    total_time = end_time - start_time
    avg_time = total_time / n_iterations
    throughput = n_iterations / total_time

    return {
        "file": file_path.name,
        "size_bytes": len(raw),
        "iterations": n_iterations,
        "total_time_sec": total_time,
        "avg_time_ms": avg_time * 1000,
        "throughput_per_sec": throughput,
        "n_tags": len(result),
    }


def main():
    """Run all benchmarks."""
    print("CSA Header Parsing Performance Benchmarks")
    print("=" * 60)
    print()

    test_files = [
        (DWI_FILE, "DWI Image Header (small)"),
        (E11_FILE, "E11 Series Header (medium)"),
        (RSFMRI_FILE, "rsfMRI Series Header (large)"),
    ]

    for file_path, description in test_files:
        if not file_path.exists():
            print(f"⚠️  {description}: File not found")
            continue

        print(f"{description}")
        print("-" * 60)

        results = benchmark_parse(file_path, n_iterations=1000)

        print(f"  File size:        {results['size_bytes']:>10,} bytes")
        print(f"  Number of tags:   {results['n_tags']:>10}")
        print(f"  Iterations:       {results['iterations']:>10,}")
        print(f"  Total time:       {results['total_time_sec']:>10.3f} sec")
        print(f"  Average time:     {results['avg_time_ms']:>10.3f} ms")
        print(f"  Throughput:       {results['throughput_per_sec']:>10.1f} parses/sec")
        print()


if __name__ == "__main__":
    main()
