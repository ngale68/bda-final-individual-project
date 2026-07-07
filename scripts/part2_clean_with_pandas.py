import csv
from pathlib import Path
import re
import sys

import pandas as pd

# Paths
INPUT = Path("data/messy/messy_market_data.csv")
CLEANED_OUTPUT = Path("data/clean/cleaned_market_data.csv")
SAMPLE_OUTPUT = Path("results/pandas_sample_results.csv")
REPORT_OUTPUT = Path("results/data_quality_report.txt")

# Columns expected
NUMERIC_COLS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_volume",
    "trade_count",
]
TIME_COLS = ["open_time", "close_time"]
ALL_EXPECTED = [
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


def clean_symbol(s: str) -> str:
    if pd.isna(s):
        return s
    s = str(s).strip()
    # Replace common separators
    s = s.replace("/", "")
    s = s.replace(" ", "")
    # Remove any non-alphanumeric
    s = re.sub(r"[^A-Za-z0-9]", "", s)
    return s.upper()


def main():
    # Ensure output folders
    CLEANED_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    SAMPLE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    if not INPUT.exists():
        print(f"Missing input: {INPUT}")
        sys.exit(1)

    ### EASY TASKS
    # 1. Load data
    df = pd.read_csv(INPUT)
    rows_before = len(df)
    cols_before = len(df.columns)

    print(f"Loaded {INPUT}")
    print(f"Rows: {rows_before}")
    print(f"Columns: {cols_before}")
    print("First 10 rows shown")
    print(df.head(10))
    print("Dtypes:")
    print(df.dtypes)

    # 2. Count missing values per column
    missing_before = df.isna().sum()
    missing_report = missing_before[missing_before > 0].sort_values(ascending=False)
    print("Missing values:")
    print(missing_report)
    most_affected = missing_report.index[0] if len(missing_report) > 0 else None
    if most_affected:
        print(f"Most affected column: {most_affected}")


    ### MEDIUM TASKS
    # 3. Convert numeric columns
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    invalid_numeric_after = df[NUMERIC_COLS].isna().any(axis=1).sum()
    print("Converted numeric columns:")
    print(", ".join([c for c in NUMERIC_COLS if c in df.columns]))
    print(f"Invalid numeric rows after conversion: {invalid_numeric_after}")

    # 4. Convert timestamps
    for col in TIME_COLS:
        if col in df.columns:
            df[col + "__orig"] = df[col]
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
    invalid_times = {
        col: df[col].isna().sum() for col in TIME_COLS if col in df.columns
    }
    print("Converted timestamp columns:")
    print(", ".join([c for c in TIME_COLS if c in df.columns]))
    print("Invalid times:")
    print(invalid_times)

    # Clean symbol column
    if "symbol" in df.columns:
        symbols_before = df["symbol"].dropna().unique()[:20]
        df["symbol"] = df["symbol"].apply(clean_symbol)
        symbols_after = df["symbol"].dropna().unique()[:20]
        print("Symbols before cleaning (sample):", symbols_before)
        print("Symbols after cleaning (sample):", symbols_after)


    ### HARD TASKS
    # 5. Remove duplicates
    dup_count = df.duplicated().sum()
    print(f"Duplicate rows found: {dup_count}")
    rows_before_dups = len(df)
    df = df.drop_duplicates()
    rows_after_dups = len(df)
    print(f"Rows before removing duplicates: {rows_before_dups}")
    print(f"Rows after removing duplicates: {rows_after_dups}")

    # 6. Detect impossible numeric values
    neg_volume = df["volume"] < 0 if "volume" in df.columns else pd.Series(False, index=df.index)
    neg_trade = df["trade_count"] < 0 if "trade_count" in df.columns else pd.Series(False, index=df.index)
    high_lt_low = (df["high"] < df["low"]) if ("high" in df.columns and "low" in df.columns) else pd.Series(False, index=df.index)

    neg_volume_count = int(neg_volume.sum())
    neg_trade_count = int(neg_trade.sum())
    high_lt_low_count = int(high_lt_low.sum())
    invalid_rules_total = neg_volume_count + neg_trade_count + high_lt_low_count

    print(f"Negative volume rows: {neg_volume_count}")
    print(f"Negative trade_count rows: {neg_trade_count}")
    print(f"Rows where high < low: {high_lt_low_count}")
    print(f"Invalid numeric rows total (by rules): {invalid_rules_total}")

    # Remove invalid numeric rows (decision: drop rows violating these hard rules)
    invalid_mask = pd.Series(False, index=df.index)
    if "volume" in df.columns:
        invalid_mask = invalid_mask | (df["volume"] < 0)
    if "trade_count" in df.columns:
        invalid_mask = invalid_mask | (df["trade_count"] < 0)
    if "high" in df.columns and "low" in df.columns:
        invalid_mask = invalid_mask | (df["high"] < df["low"])

    removed_invalid_numeric = int(invalid_mask.sum())
    df = df.loc[~invalid_mask].copy()

    # 7. Create derived columns
    df["price_range"] = df["high"] - df["low"]
    df["price_change"] = df["close"] - df["open"]
    df["percent_change"] = (df["price_change"] / df["open"]).replace([pd.NA, pd.NaT, float("inf"), -float("inf")], pd.NA) * 100

    def direction(row):
        if pd.isna(row["open"]) or pd.isna(row["close"]):
            return pd.NA
        if row["close"] > row["open"]:
            return "up"
        if row["close"] < row["open"]:
            return "down"
        return "flat"

    df["candle_direction"] = df.apply(direction, axis=1)


    ### VERY HARD TASKS
    # 8. Build a before/after data-quality report:
    # Final missing counts
    missing_after = df.isna().sum()

    # Save cleaned dataset
    df.to_csv(CLEANED_OUTPUT, index=False)
    print(f"Saved cleaned dataset: {CLEANED_OUTPUT}")

    # Build data-quality report
    rows_after = len(df)
    duplicates_after = int(df.duplicated().sum())

    report_lines = [
        "Data-quality report",
        f"Rows before cleaning: {rows_before}",
        f"Rows after cleaning: {rows_after}",
        f"Missing values before (per column):\n{missing_before.to_dict()}",
        f"Missing values after (per column):\n{missing_after.to_dict()}",
        f"Duplicate rows before: {dup_count}",
        f"Duplicate rows after: {duplicates_after}",
        f"Invalid numeric rows removed: {removed_invalid_numeric}",
        f"Negative volume rows: {neg_volume_count}",
        f"Negative trade_count rows: {neg_trade_count}",
        f"Rows where high < low: {high_lt_low_count}",
        "Cleaning decision: removed rows with negative volume/trade_count or high < low; converted numeric and timestamp columns using safe coercion; deduplicated rows; cleaned symbol formatting.",
    ]

    REPORT_OUTPUT.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Saved report: {REPORT_OUTPUT}")


    ### SAMPLE CHECK: 5 random records per symbol (10 symbols x 5 = 50 random records)
    sample_frames = []
    for symbol, group in df.groupby("symbol"):
        n = min(len(group), 5)
        sample_frames.append(group.sample(n=n, random_state=1))
    sample_df = pd.concat(sample_frames, ignore_index=True)

    # Ensure we have 10 symbols
    symbols_in_sample = sample_df["symbol"].nunique()

    # Sample analytics
    avg_close = sample_df.groupby("symbol")["close"].mean()
    avg_volume = sample_df.groupby("symbol")["volume"].mean()
    candle_counts = sample_df["candle_direction"].value_counts(dropna=False)
    largest_range_row = sample_df.loc[sample_df["price_range"].idxmax()]

    # Save sample results
    with SAMPLE_OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        writer.writerow(["Sample rows used", len(sample_df)])
        writer.writerow(["Symbols included", symbols_in_sample])
        writer.writerow(["Records per symbol (target)", "5"])
        writer.writerow(["Questions answered", "average_close, highest_avg_volume, candle_direction_counts, largest_price_range_row"])
        writer.writerow(["-- average close by symbol --", ""])
        for sym, val in avg_close.items():
            writer.writerow([f"avg_close_{sym}", f"{val:.6f}"])
        writer.writerow(["-- highest average volume --", ""])
        if not avg_volume.empty:
            writer.writerow(["highest_avg_volume", avg_volume.idxmax()])
        writer.writerow(["-- candle direction counts --", ""])
        for dir_label, cnt in candle_counts.items():
            writer.writerow([f"candle_{dir_label}", int(cnt)])
        writer.writerow(["-- largest price range row --", ""])
        writer.writerow(["symbol", largest_range_row.get("symbol")])
        writer.writerow(["open_time", largest_range_row.get("open_time")])
        writer.writerow(["price_range", largest_range_row.get("price_range")])

    print(f"Saved results: {SAMPLE_OUTPUT}")
    print(f"Sample rows used: {len(sample_df)}")
    print(f"Symbols included: {symbols_in_sample}")
    print("Questions answered: average close by symbol; highest average volume; candle direction counts; largest price range row")

    # Short explanation about pandas vs Spark
    explanation = (
        "Pandas is useful for quick, in-memory inspection and iterative cleaning on small samples. "
        "However, pandas works in-memory and does not scale to large datasets efficiently; "
        "therefore the final analytics for the full dataset should be performed in Spark.")
    print(explanation)


if __name__ == '__main__':
    main()
