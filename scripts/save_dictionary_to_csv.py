import csv
from pathlib import Path


row = {
    "symbol": "BTCUSDT",
    "interval": "1h",
    "open_time": "2026-05-28T00:00:00+00:00",
    "open": 108742.01,
    "high": 109120.44,
    "low": 108330.50,
    "close": 108990.32,
    "volume": 1284.52,
}

output_path = Path("data/clean/example_dictionary_row.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=row.keys())
    writer.writeheader()
    writer.writerow(row)

print(f"Saved {output_path}")
