#!/usr/bin/env python3
"""
API Load Tester — Benchmark endpoints, detect bottlenecks, generate reports.

Simulates concurrent requests, tracks latency percentiles (p50/p95/p99),
monitors throughput and error rates, and generates HTML/JSON reports.

Usage:
    python api_load_tester.py --url http://localhost:3000/api/users --concurrency 50 --duration 30
    python api_load_tester.py --url http://localhost:3000/api/orders --ramp 10,50,100 --duration 60
    python api_load_tester.py --url http://localhost:3000/api --suite endpoints.json --report html
"""

import argparse
import asyncio
import json
import math
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

try:
    import aiohttp
except ImportError:
    aiohttp = None


@dataclass
class RequestResult:
    status: int
    latency_ms: float
    error: Optional[str] = None
    size_bytes: int = 0


@dataclass
class LoadTestResults:
    url: str
    method: str
    concurrency: int
    duration_s: float
    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    latencies: list[float] = field(default_factory=list)
    errors: dict[str, int] = field(default_factory=dict)
    status_codes: dict[int, int] = field(default_factory=dict)
    start_time: float = 0
    end_time: float = 0

    @property
    def elapsed_s(self) -> float:
        return self.end_time - self.start_time if self.end_time else 0

    @property
    def rps(self) -> float:
        return self.total_requests / self.elapsed_s if self.elapsed_s > 0 else 0

    @property
    def error_rate(self) -> float:
        return (self.failed / self.total_requests * 100) if self.total_requests > 0 else 0

    def percentile(self, p: float) -> float:
        if not self.latencies:
            return 0
        sorted_lat = sorted(self.latencies)
        idx = int(math.ceil(p / 100 * len(sorted_lat))) - 1
        return sorted_lat[max(0, idx)]

    def summary(self) -> dict:
        return {
            "url": self.url,
            "method": self.method,
            "concurrency": self.concurrency,
            "duration_s": round(self.elapsed_s, 2),
            "total_requests": self.total_requests,
            "successful": self.successful,
            "failed": self.failed,
            "rps": round(self.rps, 2),
            "error_rate_pct": round(self.error_rate, 2),
            "latency_ms": {
                "min": round(min(self.latencies), 2) if self.latencies else 0,
                "max": round(max(self.latencies), 2) if self.latencies else 0,
                "mean": round(sum(self.latencies) / len(self.latencies), 2) if self.latencies else 0,
                "p50": round(self.percentile(50), 2),
                "p95": round(self.percentile(95), 2),
                "p99": round(self.percentile(99), 2),
            },
            "status_codes": dict(sorted(self.status_codes.items())),
            "errors": dict(sorted(self.errors.items(), key=lambda x: -x[1])),
        }


async def make_request(
    session: "aiohttp.ClientSession",
    url: str,
    method: str,
    headers: dict,
    body: Optional[str],
) -> RequestResult:
    start = time.monotonic()
    try:
        kwargs = {"headers": headers}
        if body and method in ("POST", "PUT", "PATCH"):
            kwargs["data"] = body
            kwargs["headers"]["Content-Type"] = "application/json"

        async with session.request(method, url, **kwargs) as resp:
            data = await resp.read()
            latency = (time.monotonic() - start) * 1000
            return RequestResult(
                status=resp.status,
                latency_ms=latency,
                size_bytes=len(data),
            )
    except asyncio.TimeoutError:
        latency = (time.monotonic() - start) * 1000
        return RequestResult(status=0, latency_ms=latency, error="timeout")
    except aiohttp.ClientError as e:
        latency = (time.monotonic() - start) * 1000
        return RequestResult(status=0, latency_ms=latency, error=str(type(e).__name__))
    except Exception as e:
        latency = (time.monotonic() - start) * 1000
        return RequestResult(status=0, latency_ms=latency, error=str(e))


async def run_load_test(
    url: str,
    method: str = "GET",
    concurrency: int = 10,
    duration: float = 10,
    headers: Optional[dict] = None,
    body: Optional[str] = None,
    timeout: float = 30,
) -> LoadTestResults:
    if aiohttp is None:
        print("Error: aiohttp is required. Install with: pip install aiohttp")
        sys.exit(1)

    results = LoadTestResults(url=url, method=method, concurrency=concurrency, duration_s=duration)
    headers = headers or {}

    connector = aiohttp.TCPConnector(limit=concurrency, force_close=False)
    client_timeout = aiohttp.ClientTimeout(total=timeout)

    async with aiohttp.ClientSession(connector=connector, timeout=client_timeout) as session:
        results.start_time = time.monotonic()
        end_time = results.start_time + duration

        async def worker():
            while time.monotonic() < end_time:
                result = await make_request(session, url, method, dict(headers), body)
                results.total_requests += 1
                results.latencies.append(result.latency_ms)
                results.status_codes[result.status] = results.status_codes.get(result.status, 0) + 1

                if result.error:
                    results.failed += 1
                    results.errors[result.error] = results.errors.get(result.error, 0) + 1
                elif 200 <= result.status < 400:
                    results.successful += 1
                else:
                    results.failed += 1

        workers = [asyncio.create_task(worker()) for _ in range(concurrency)]
        await asyncio.gather(*workers)
        results.end_time = time.monotonic()

    return results


async def run_ramp_test(
    url: str,
    method: str,
    ramp_stages: list[int],
    duration_per_stage: float,
    headers: Optional[dict] = None,
    body: Optional[str] = None,
) -> list[LoadTestResults]:
    all_results = []
    for i, concurrency in enumerate(ramp_stages):
        print(f"\n  Stage {i + 1}/{len(ramp_stages)}: {concurrency} concurrent users for {duration_per_stage}s")
        result = await run_load_test(url, method, concurrency, duration_per_stage, headers, body)
        all_results.append(result)
        print_results(result, compact=True)
    return all_results


def print_results(results: LoadTestResults, compact: bool = False):
    s = results.summary()
    lat = s["latency_ms"]

    if compact:
        print(f"    RPS: {s['rps']} | p50: {lat['p50']}ms | p95: {lat['p95']}ms | p99: {lat['p99']}ms | Errors: {s['error_rate_pct']}%")
        return

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  Load Test Results                          │
  ├─────────────────────────────────────────────┤
  │  URL:          {s['url']:<30}│
  │  Method:       {s['method']:<30}│
  │  Concurrency:  {s['concurrency']:<30}│
  │  Duration:     {s['duration_s']}s{' ' * (28 - len(str(s['duration_s'])))}│
  ├─────────────────────────────────────────────┤
  │  Total Requests:  {s['total_requests']:<26}│
  │  Successful:      {s['successful']:<26}│
  │  Failed:          {s['failed']:<26}│
  │  RPS:             {s['rps']:<26}│
  │  Error Rate:      {s['error_rate_pct']}%{' ' * (25 - len(str(s['error_rate_pct'])))}│
  ├─────────────────────────────────────────────┤
  │  Latency (ms)                               │
  │    Min:   {lat['min']:<35}│
  │    Mean:  {lat['mean']:<35}│
  │    p50:   {lat['p50']:<35}│
  │    p95:   {lat['p95']:<35}│
  │    p99:   {lat['p99']:<35}│
  │    Max:   {lat['max']:<35}│
  └─────────────────────────────────────────────┘""")

    if s["status_codes"]:
        print("\n  Status Codes:")
        for code, count in s["status_codes"].items():
            print(f"    {code}: {count}")

    if s["errors"]:
        print("\n  Errors:")
        for err, count in s["errors"].items():
            print(f"    {err}: {count}")


def generate_html_report(results: LoadTestResults, output_path: Path):
    s = results.summary()
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Load Test Report — {s['url']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; padding: 2rem; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ font-size: 1.5rem; margin-bottom: 0.5rem; color: #f8fafc; }}
        .subtitle {{ color: #94a3b8; margin-bottom: 2rem; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 1.25rem; }}
        .card .label {{ font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }}
        .card .value {{ font-size: 1.75rem; font-weight: 700; margin-top: 0.25rem; }}
        .card .value.green {{ color: #4ade80; }}
        .card .value.red {{ color: #f87171; }}
        .card .value.blue {{ color: #60a5fa; }}
        .card .value.yellow {{ color: #fbbf24; }}
        table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 12px; overflow: hidden; }}
        th, td {{ padding: 0.75rem 1rem; text-align: left; }}
        th {{ background: #334155; font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; }}
        td {{ border-top: 1px solid #334155; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Load Test Report</h1>
        <p class="subtitle">{s['method']} {s['url']} — {s['concurrency']} concurrent users for {s['duration_s']}s</p>
        <div class="grid">
            <div class="card"><div class="label">Total Requests</div><div class="value blue">{s['total_requests']}</div></div>
            <div class="card"><div class="label">Requests/sec</div><div class="value green">{s['rps']}</div></div>
            <div class="card"><div class="label">Error Rate</div><div class="value {'red' if s['error_rate_pct'] > 1 else 'green'}">{s['error_rate_pct']}%</div></div>
            <div class="card"><div class="label">p50 Latency</div><div class="value yellow">{s['latency_ms']['p50']}ms</div></div>
            <div class="card"><div class="label">p95 Latency</div><div class="value yellow">{s['latency_ms']['p95']}ms</div></div>
            <div class="card"><div class="label">p99 Latency</div><div class="value yellow">{s['latency_ms']['p99']}ms</div></div>
        </div>
        <table>
            <thead><tr><th>Metric</th><th>Value</th></tr></thead>
            <tbody>
                <tr><td>Min Latency</td><td>{s['latency_ms']['min']}ms</td></tr>
                <tr><td>Mean Latency</td><td>{s['latency_ms']['mean']}ms</td></tr>
                <tr><td>Max Latency</td><td>{s['latency_ms']['max']}ms</td></tr>
                <tr><td>Successful</td><td>{s['successful']}</td></tr>
                <tr><td>Failed</td><td>{s['failed']}</td></tr>
            </tbody>
        </table>
    </div>
</body>
</html>"""
    output_path.write_text(html)
    print(f"\n  📊 HTML report saved to: {output_path}")


def generate_json_report(results: LoadTestResults, output_path: Path):
    output_path.write_text(json.dumps(results.summary(), indent=2))
    print(f"\n  📊 JSON report saved to: {output_path}")


async def run_suite(suite_path: Path, base_url: str, concurrency: int, duration: float):
    with open(suite_path) as f:
        suite = json.load(f)

    print(f"\n🧪 Running test suite: {suite_path.name} ({len(suite)} endpoints)\n")

    for endpoint in suite:
        url = base_url.rstrip("/") + endpoint.get("path", "/")
        method = endpoint.get("method", "GET").upper()
        headers = endpoint.get("headers", {})
        body = json.dumps(endpoint["body"]) if "body" in endpoint else None

        print(f"  → {method} {url}")
        result = await run_load_test(url, method, concurrency, duration, headers, body)
        print_results(result, compact=True)


def main():
    parser = argparse.ArgumentParser(description="API Load Tester — Benchmark and detect bottlenecks")
    parser.add_argument("--url", help="Target URL to test")
    parser.add_argument("--method", default="GET", choices=["GET", "POST", "PUT", "PATCH", "DELETE"])
    parser.add_argument("--concurrency", type=int, default=10, help="Number of concurrent users (default: 10)")
    parser.add_argument("--duration", type=float, default=10, help="Test duration in seconds (default: 10)")
    parser.add_argument("--ramp", help="Ramp-up stages as comma-separated concurrency values (e.g., 10,50,100)")
    parser.add_argument("--header", action="append", help="Custom header (format: Key:Value)")
    parser.add_argument("--body", help="Request body (JSON string)")
    parser.add_argument("--suite", help="Path to endpoint suite JSON file")
    parser.add_argument("--report", choices=["html", "json", "both"], help="Generate report")
    parser.add_argument("--output", default="./load-test-report", help="Report output path (without extension)")
    parser.add_argument("--timeout", type=float, default=30, help="Request timeout in seconds (default: 30)")

    args = parser.parse_args()

    if not args.url and not args.suite:
        print("Error: --url or --suite is required")
        sys.exit(1)

    headers = {}
    if args.header:
        for h in args.header:
            key, _, value = h.partition(":")
            headers[key.strip()] = value.strip()

    if args.suite:
        asyncio.run(run_suite(Path(args.suite), args.url or "", args.concurrency, args.duration))
        return

    print(f"\n🚀 Load Testing: {args.method} {args.url}")
    print(f"   Concurrency: {args.concurrency} | Duration: {args.duration}s | Timeout: {args.timeout}s\n")

    if args.ramp:
        stages = [int(s.strip()) for s in args.ramp.split(",")]
        stage_duration = args.duration / len(stages)
        all_results = asyncio.run(run_ramp_test(args.url, args.method, stages, stage_duration, headers, args.body))
        results = all_results[-1]
    else:
        results = asyncio.run(run_load_test(
            args.url, args.method, args.concurrency, args.duration, headers, args.body, args.timeout
        ))
        print_results(results)

    if args.report:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        if args.report in ("html", "both"):
            generate_html_report(results, output.with_suffix(".html"))
        if args.report in ("json", "both"):
            generate_json_report(results, output.with_suffix(".json"))

    print()


if __name__ == "__main__":
    main()
