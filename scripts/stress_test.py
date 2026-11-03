#!/usr/bin/env python3
"""
Zero-dependency Stress Testing & Benchmark Script for FastAPI Cluster
Uses only Python Standard Library (concurrent.futures + urllib).
Works on any environment without needing pip install / httpx.
"""
import concurrent.futures
import urllib.request
import json
import time
import collections
import statistics

TARGET_URL = "http://localhost:8080/health"
TOTAL_REQUESTS = 300
CONCURRENCY = 20


def send_single_request(req_id: int):
    start = time.perf_counter()
    try:
        req = urllib.request.Request(
            TARGET_URL,
            headers={"User-Agent": "Benchmark-Script/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            elapsed_ms = (time.perf_counter() - start) * 1000
            status_code = resp.status
            body = json.loads(resp.read().decode())
            server_id = body.get("server_id", "unknown")
            upstream_addr = resp.headers.get("X-Upstream-Backend", "unknown")
            return {
                "id": req_id,
                "status": status_code,
                "server_id": server_id,
                "upstream": upstream_addr,
                "latency_ms": elapsed_ms,
                "error": None,
            }
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "id": req_id,
            "status": 0,
            "server_id": "failed",
            "upstream": "none",
            "latency_ms": elapsed_ms,
            "error": str(e),
        }


def run_benchmark():
    print("🚀 Starting Stress Test:")
    print(f"   Target URL:     {TARGET_URL}")
    print(f"   Total Requests: {TOTAL_REQUESTS}")
    print(f"   Concurrency:    {CONCURRENCY} threads\n")

    results = []
    start_total = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [executor.submit(send_single_request, i) for i in range(TOTAL_REQUESTS)]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    total_time = time.perf_counter() - start_total

    # Analytics
    success_requests = [r for r in results if r["status"] == 200]
    success_count = len(success_requests)
    fail_count = TOTAL_REQUESTS - success_count
    latencies = [r["latency_ms"] for r in success_requests]
    distribution = collections.Counter(r["server_id"] for r in success_requests)

    throughput = TOTAL_REQUESTS / total_time if total_time > 0 else 0
    p50 = statistics.median(latencies) if latencies else 0
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else (max(latencies) if latencies else 0)
    p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else (max(latencies) if latencies else 0)

    print("══════════════════════════════════════════════")
    print("               BENCHMARK RESULTS              ")
    print("══════════════════════════════════════════════")
    print(f" Total Duration:      {total_time:.2f} s")
    print(f" Throughput:          {throughput:.1f} req/s")
    print(f" Successful Requests: {success_count}/{TOTAL_REQUESTS} ({(success_count/TOTAL_REQUESTS)*100:.1f}%)")
    print(f" Failed Requests:     {fail_count}")
    print(f" Min Latency:         {min(latencies):.1f} ms" if latencies else "N/A")
    print(f" Avg Latency:         {statistics.mean(latencies):.1f} ms" if latencies else "N/A")
    print(f" Median (p50):        {p50:.1f} ms")
    print(f" p95 Latency:         {p95:.1f} ms")
    print(f" p99 Latency:         {p99:.1f} ms")
    print(f" Max Latency:         {max(latencies):.1f} ms" if latencies else "N/A")
    print("──────────────────────────────────────────────")
    print(" Traffic Distribution Across Nodes:")
    for server, count in distribution.items():
        pct = (count / success_count * 100) if success_count else 0
        print(f"   • {server:<18}: {count} req ({pct:.1f}%)")
    print("══════════════════════════════════════════════")
    print("\n👉 Check Grafana Dashboard at http://localhost:3001 to view realtime metrics!")


if __name__ == "__main__":
    run_benchmark()
