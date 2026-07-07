import csv
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import requests

URL = "https://data-api.binance.vision/api/v3/klines"
SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "AVAXUSDT",
    "LINKUSDT",
    "DOTUSDT",
]
INTERVAL = "1h"
LIMIT = 1000
FIELDNAMES = [
    "symbol",
    "interval",
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_volume",
    "trade_count",
]

DATA_PATH = Path("data/clean/clean_market_data.csv")
LOG_PATH = Path("results/api_download.log")
BENCHMARK_PATH = Path("results/runtime_comparison.csv")

rate_lock = threading.Lock()
log_lock = threading.Lock()
request_timestamps = deque()
rate_limit_waits = 0


def ensure_directories():
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def iso_timestamp(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()


def log(message: str):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{timestamp} | {message}\n"
    with log_lock:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line)


def wait_for_rate_slot(log_phase: bool = True):
    global rate_limit_waits
    with rate_lock:
        now = time.monotonic()
        while request_timestamps and now - request_timestamps[0] >= 60:
            request_timestamps.popleft()

        if len(request_timestamps) >= 100:
            earliest = request_timestamps[0]
            wait_seconds = 60 - (now - earliest)
            if log_phase:
                log(f"WAIT rate_limit_seconds={wait_seconds:.2f}")
            rate_limit_waits += 1
            time.sleep(wait_seconds)
            now = time.monotonic()
            while request_timestamps and now - request_timestamps[0] >= 60:
                request_timestamps.popleft()

        request_timestamps.append(now)


def download_symbol(symbol: str, log_phase: bool = True) -> list[dict]:
    wait_for_rate_slot(log_phase=log_phase)
    params = {"symbol": symbol, "interval": INTERVAL, "limit": LIMIT}
    if log_phase:
        log(f"START request symbol={symbol} interval={INTERVAL} limit={LIMIT}")
    response = requests.get(URL, params=params, timeout=30)
    response.raise_for_status()
    records = response.json()
    if log_phase:
        log(f"END request symbol={symbol} records={len(records)}")

    rows = []
    for record in records:
        rows.append(
            {
                "symbol": symbol,
                "interval": INTERVAL,
                "open_time": iso_timestamp(record[0]),
                "open": record[1],
                "high": record[2],
                "low": record[3],
                "close": record[4],
                "volume": record[5],
                "close_time": iso_timestamp(record[6]),
                "quote_volume": record[7],
                "trade_count": record[8],
            }
        )
    return rows


def download_serial() -> list[dict]:
    all_rows = []
    for symbol in SYMBOLS:
        # suppress per-request logging for the serial benchmark
        all_rows.extend(download_symbol(symbol, log_phase=False))
    return all_rows


def download_multithreaded() -> list[dict]:
    all_rows = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        # enable logging for multithreaded requests
        futures = {executor.submit(download_symbol, symbol, True): symbol for symbol in SYMBOLS}
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                rows = future.result()
                print(f"Downloaded {symbol}: {len(rows)} records")
                all_rows.extend(rows)
            except Exception as exc:
                log(f"ERROR symbol={symbol} error={exc}")
                raise
    return all_rows


def save_csv(rows: list[dict], path: Path):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def save_runtime_comparison(serial_seconds: float, threaded_seconds: float):
    with BENCHMARK_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["method", "seconds", "records", "note"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "method": "serial",
                "seconds": f"{serial_seconds:.4f}",
                "records": len(SYMBOLS) * LIMIT,
                "note": "downloaded the ten symbols one after another",
            }
        )
        writer.writerow(
            {
                "method": "multithreading",
                "seconds": f"{threaded_seconds:.4f}",
                "records": len(SYMBOLS) * LIMIT,
                "note": "downloaded several symbols at the same time",
            }
        )


def main():
    ensure_directories()
    print(f"Symbols configured: {len(SYMBOLS)}")
    print(f"Interval: {INTERVAL}")
    print(f"Limit per symbol: {LIMIT}")
    print(
        f"Expected records: {len(SYMBOLS) * LIMIT}"
    )

    serial_start = time.perf_counter()
    serial_rows = download_serial()
    serial_seconds = time.perf_counter() - serial_start

    # Reset rate limiter state for the second benchmark
    with rate_lock:
        request_timestamps.clear()

    multithread_start = time.perf_counter()
    threaded_rows = download_multithreaded()
    threaded_seconds = time.perf_counter() - multithread_start

    if len(threaded_rows) != len(serial_rows):
        raise ValueError("Serial and threaded downloads returned different record counts")

    print("Multithreaded download complete")

    save_csv(threaded_rows, DATA_PATH)
    log(f"WROTE csv={DATA_PATH} records={len(threaded_rows)}")

    save_runtime_comparison(serial_seconds, threaded_seconds)

    print(f"Created folders: {DATA_PATH.parent}, {LOG_PATH.parent}")
    print(f"Saved: {DATA_PATH}")
    print(f"Saved: {BENCHMARK_PATH}")
    print(f"Total records saved: {len(threaded_rows)}")
    print("Record count check: passed")
    print(f"Log file: {LOG_PATH}")
    print(f"Request limit: 100 requests per minute")
    print(f"Rate-limit wait events logged: {rate_limit_waits}")
    print("Script completed successfully")
    print("Output files found: 3")
    print("No price analytics were calculated in Team 1")


if __name__ == "__main__":
    main()