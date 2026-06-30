import argparse
import csv
import random
from pathlib import Path


NUMERIC_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_volume",
    "trade_count",
    "taker_buy_base_volume",
    "taker_buy_quote_volume",
]

TIME_COLUMNS = ["open_time", "close_time"]
SYMBOL_COLUMN = "symbol"
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


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if not rows:
        raise ValueError(f"No rows found in {path}")

    return rows, fieldnames


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sample_indices(row_count, fraction, minimum):
    size = max(minimum, int(row_count * fraction))
    size = min(size, row_count)
    return random.sample(range(row_count), size)


def corrupt_missing_values(rows, fieldnames):
    columns = [column for column in NUMERIC_COLUMNS + TIME_COLUMNS if column in fieldnames]
    if not columns:
        return 0

    count = 0
    for index in sample_indices(len(rows), 0.05, 10):
        column = random.choice(columns)
        rows[index][column] = ""
        count += 1

    return count


def corrupt_numeric_text(rows, fieldnames):
    columns = [column for column in NUMERIC_COLUMNS if column in fieldnames]
    if not columns:
        return 0

    replacements = ["not_available", "error", "missing", "unknown"]
    count = 0

    for index in sample_indices(len(rows), 0.04, 8):
        column = random.choice(columns)
        rows[index][column] = random.choice(replacements)
        count += 1

    return count


def corrupt_invalid_times(rows, fieldnames):
    columns = [column for column in TIME_COLUMNS if column in fieldnames]
    if not columns:
        return 0

    replacements = ["not_a_date", "1900-99-99", "missing_time"]
    count = 0

    for index in sample_indices(len(rows), 0.03, 6):
        column = random.choice(columns)
        rows[index][column] = random.choice(replacements)
        count += 1

    return count


def corrupt_symbol_names(rows, fieldnames):
    if SYMBOL_COLUMN not in fieldnames:
        return 0

    replacements = {
        symbol: [
            symbol.lower(),
            f" {symbol} ",
            symbol.replace("USDT", "/USDT"),
        ]
        for symbol in SYMBOLS
    }

    count = 0
    for index in sample_indices(len(rows), 0.04, 8):
        current = rows[index].get(SYMBOL_COLUMN, "").strip().upper().replace("/", "")
        options = replacements.get(current)
        if not options:
            continue

        rows[index][SYMBOL_COLUMN] = random.choice(options)
        count += 1

    return count


def corrupt_negative_volumes(rows, fieldnames):
    volume_columns = [
        column
        for column in ["volume", "quote_volume", "taker_buy_base_volume", "taker_buy_quote_volume"]
        if column in fieldnames
    ]
    if not volume_columns:
        return 0

    count = 0
    for index in sample_indices(len(rows), 0.03, 6):
        column = random.choice(volume_columns)
        value = rows[index].get(column, "")

        try:
            rows[index][column] = str(-abs(float(value)))
        except ValueError:
            rows[index][column] = "-999"

        count += 1

    return count


def duplicate_rows(rows):
    duplicate_count = max(5, int(len(rows) * 0.03))
    duplicate_count = min(duplicate_count, len(rows))
    duplicates = [dict(rows[index]) for index in random.sample(range(len(rows)), duplicate_count)]
    rows.extend(duplicates)
    return duplicate_count


def drop_rows(rows):
    drop_count = max(5, int(len(rows) * 0.03))
    drop_count = min(drop_count, len(rows) - 1)
    drop_indices = set(random.sample(range(len(rows)), drop_count))
    kept_rows = [row for index, row in enumerate(rows) if index not in drop_indices]
    rows[:] = kept_rows
    return drop_count


def mess_data(input_path, output_path, seed):
    random.seed(seed)

    rows, fieldnames = read_csv(input_path)
    original_count = len(rows)

    summary = {
        "original_rows": original_count,
        "dropped_rows": drop_rows(rows),
        "duplicated_rows": duplicate_rows(rows),
        "missing_values": corrupt_missing_values(rows, fieldnames),
        "text_in_numeric_columns": corrupt_numeric_text(rows, fieldnames),
        "invalid_times": corrupt_invalid_times(rows, fieldnames),
        "inconsistent_symbols": corrupt_symbol_names(rows, fieldnames),
        "negative_volumes": corrupt_negative_volumes(rows, fieldnames),
        "final_rows": len(rows),
    }

    random.shuffle(rows)
    write_csv(output_path, rows, fieldnames)

    return summary


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create a deliberately messy version of a market data CSV file."
    )
    parser.add_argument(
        "--input",
        default="data/clean/clean_market_data.csv",
        help="Path to the clean input CSV file.",
    )
    parser.add_argument(
        "--output",
        default="data/messy/messy_market_data.csv",
        help="Path to the messy output CSV file.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible corruption.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    summary = mess_data(input_path, output_path, args.seed)

    print(f"Created messy dataset: {output_path}")
    print("Summary:")
    for key, value in summary.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
