#!/usr/bin/env python3
"""
Load Balancer Verification Script
Sends consecutive requests to Nginx (http://localhost:8080/health)
and verifies that requests are distributed across multiple backend instances.
"""
import time
import urllib.request
import json
import collections
import sys

URL = "http://localhost:8080/health"
TOTAL_REQUESTS = 10


def test_load_balancer():
    print(f"Testing Load Balancer across {TOTAL_REQUESTS} requests -> {URL}\n")
    distribution = collections.defaultdict(int)

    for i in range(1, TOTAL_REQUESTS + 1):
        try:
            start_time = time.time()
            req = urllib.request.Request(URL)
            with urllib.request.urlopen(req, timeout=5) as res:
                elapsed_ms = (time.time() - start_time) * 1000
                body = json.loads(res.read().decode())
                server_id = body.get("server_id", "unknown")
                upstream_hdr = res.headers.get("X-Upstream-Backend", "unknown")
                distribution[server_id] += 1
                print(f"Request #{i:02d} | Server ID: {server_id:<16} | Upstream IP: {upstream_hdr:<30} | {elapsed_ms:6.1f} ms")
        except Exception as e:
            print(f"Request #{i:02d} | Error: {e}")


    print("\n--- Summary of Traffic Distribution ---")
    for server, count in distribution.items():
        percentage = (count / TOTAL_REQUESTS) * 100
        print(f"  {server}: {count}/{TOTAL_REQUESTS} requests ({percentage:.1f}%)")

    if len(distribution) > 1:
        print("\n [SUCCESS] Traffic is actively balanced across multiple instances!")
    else:
        print("\n  [INFO] Only 1 instance responded. Check if all instances are running.")


if __name__ == "__main__":
    test_load_balancer()
