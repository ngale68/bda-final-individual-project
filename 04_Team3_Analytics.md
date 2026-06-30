# Team 3: Analytics

Team lead: **Zehra**

Zehra from the Analytics team receives your cleaned dataset.

> "Thanks. Now we need to run the full analysis in Spark. The client does not want a sample; they want a full summary across all symbols."

## Handoff Note

Team 2 uses pandas to clean the messy dataset and run a small 50-record check. Team 3 uses Spark to analyze the full cleaned dataset and produce the final ranked market summary for Zehra.

Use Spark to analyze:

```txt
data/clean/cleaned_market_data.csv
```

Google Colab is recommended for this part. You may use PySpark locally if you like.

Create:

```txt
part3_spark_analytics.ipynb
```

## Challenge tasks

Complete all eight tasks below.

Team 3 is worth **35 marks**.

### Easy tasks

1. Start a Spark session, load the full `data/clean/cleaned_market_data.csv` file, and print the schema, row count, and column names. This must be the cleaned file from Team 2, not the messy file and not the 50-record pandas sample. Use this to prove that Spark has loaded the dataset correctly. **3 marks**

   Example output:

   ```txt
   Spark session started
   Loaded file: data/clean/cleaned_market_data.csv
   Row count: 8364
   Columns: symbol, interval, open_time, open, high, low, close, volume, trade_count
   open_time: timestamp
   close: double
   volume: double
   ```

2. Register the DataFrame as a temporary SQL view named `market_data` and run a small test query. This lets you run Spark SQL queries against the dataset using the table name `market_data`. **3 marks**

   Example output:

   ```txt
   Temporary SQL view created: market_data
   Test query returned rows: 10
   ```

### Medium tasks

3. Add or verify `price_range`, `price_change`, `percent_change`, and `candle_direction` in Spark. Use the same meanings as Team 2: `price_range = high - low`, `price_change = close - open`, `percent_change = (price_change / open) * 100`, and `candle_direction` is `up`, `down`, or `flat` based on whether the close price is higher, lower, or equal to the open price. Show a small preview proving the columns exist. **4 marks**

   Example output:

   ```txt
   Created/verified columns:
   price_range, price_change, percent_change, candle_direction

   Example row:
   symbol=BTCUSDT price_range=880.85 price_change=403.87 percent_change=0.51 candle_direction=up
   ```

4. Create time features from `open_time`, such as `trade_date`, `trade_hour`, and day of week. Then run full-dataset Spark SQL queries for average close price by symbol, average volume by symbol, and row count by symbol. Briefly compare this full result with the 50-record pandas sample from Team 2 and explain why the full Spark result is more reliable. **5 marks**

   Example output:

   ```txt
   Created time features:
   trade_date, trade_hour, day_of_week

   Example row:
   open_time=2026-05-04 02:00:00 trade_date=2026-05-04 trade_hour=2 day_of_week=Mon

   Average close by symbol:
   BTCUSDT 79160.87
   ETHUSDT 1986.66

   Row count by symbol:
   BTCUSDT 842
   ETHUSDT 836

   Full Spark result uses all cleaned rows, not only 50 sample rows.
   ```

### Hard tasks

5. Create a volatility ranking by symbol using average, minimum, maximum, and standard deviation of `price_range`. A symbol with a higher average or standard deviation of `price_range` is usually more volatile. **4 marks**

   Example output:

   ```txt
   Volatility ranking:
   rank=1 symbol=BTCUSDT avg_price_range=842.21 stddev_price_range=410.32
   rank=2 symbol=ETHUSDT avg_price_range=26.73 stddev_price_range=12.84
   ```

6. Create an activity ranking by symbol using total trades, total quote volume, and average volume. A symbol with more trades and higher quote volume should appear more active. **4 marks**

   Example output:

   ```txt
   Activity ranking:
   rank=1 symbol=XRPUSDT total_trades=80311880 total_quote_volume=912345678.22
   rank=2 symbol=BTCUSDT total_trades=73422311 total_quote_volume=812345678.44
   ```

7. Analyze activity by time using the time features. Find the busiest hour and busiest date by `trade_count` and `quote_volume`, then explain when market activity was highest in the cleaned dataset. **4 marks**

   Example output:

   ```txt
   Busiest hour by trades:
   trade_hour=14 total_trades=2834412

   Busiest date by quote volume:
   trade_date=2026-05-04 total_quote_volume=734567890.55
   ```

### Very hard task

8. Build a final ranked market summary table with one row per symbol. Include total records, average volume, total trades, average percent change, average price range, up/down/flat candle counts, volatility rank, activity rank, and a short interpretation for Zehra. The final table should help Zehra quickly see which symbols were most active, most volatile, and most important to mention in the report. Save this result as `results/spark_market_summary.csv`. **8 marks**

   Example output:

   ```txt
   Final ranked market summary created
   Rows in summary: 10
   Saved: results/spark_market_summary.csv

   Top activity symbol: XRPUSDT
   Top volatility symbol: BTCUSDT
   Interpretation: XRPUSDT had the highest trading activity, while BTCUSDT had the widest average price range.
   ```

Your Spark work must include:

- at least six Spark SQL queries
- grouped analytics with `GROUP BY`
- sorted results with `ORDER BY`
- at least one time-based query using `trade_hour` or `trade_date`
- a saved final summary file: `results/spark_market_summary.csv`
- `spark.stop()` at the end

Your Spark results should connect to the small pandas sample analysis from Team 2, but they must go further. Team 3 should include at least three analyses that are not part of the Team 2 sample check:

- volatility ranking
- activity ranking
- time-based activity analysis
- final ranked market summary

Example of the difference:

| Question | Team 2 pandas sample | Team 3 Spark full analytics |
| --- | --- | --- |
| Average close price by symbol | calculated from 50 sample rows | calculated from all cleaned rows |
| Candle direction counts | quick sample check | full count by symbol in the ranked summary |
| Most active symbol | optional sample result | required activity ranking using total `trade_count` and `quote_volume` |
| Busiest trading hour | not required | required time-based Spark analysis |
