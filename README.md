# Big Data Analytics Final Project

## Overview

This repository contains my completed final project for Owl Analytics. The work covers the full data pipeline for a cryptocurrency market-monitoring task: collecting market data from the Binance API, cleaning a deliberately messy dataset, and running full-dataset analytics with Spark.

My name: Nga Le

Repository link: https://github.com/ngale68/bda-final-individual-project

## Company scenario

Owl Analytics wants to understand which cryptocurrency symbols are most active, which are most volatile, and when trading activity is highest. The project was built to show how a data pipeline can move from raw API data to a cleaned dataset and then to a usable analytics summary.

## How to run the project

### Team 1: Data collection

Run the downloader from the repository root:

```bash
python scripts/part1_build_dataset.py
```

This script creates:
- data/clean/clean_market_data.csv
- results/api_download.log
- results/runtime_comparison.csv

### Team 2: Data quality

First create the messy input file, then run the pandas cleaning script:

```bash
python scripts/mess_my_data.py --input data/clean/clean_market_data.csv --output data/messy/messy_market_data.csv
python scripts/part2_clean_with_pandas.py
```

This creates:
- data/messy/messy_market_data.csv
- data/clean/cleaned_market_data.csv
- results/pandas_sample_results.csv
- results/data_quality_report.txt

### Team 3: Spark analytics

The full Spark analysis is available in the notebook:
- scripts/part3_spark_analytics.ipynb

This file is a download from Google Colab. 

This creates:
- results/spark_market_summary.csv

## Final report and reflection

- Report to Stelios: [reports/report_to_stelios.md](reports/report_to_stelios.md)
- Reflection: [reports/reflection.md](reports/reflection.md)

## Submitted files

- [reports/report_to_stelios.md](reports/report_to_stelios.md)
- [reports/reflection.md](reports/reflection.md)
- [results/runtime_comparison.csv](results/runtime_comparison.csv)
- [results/pandas_sample_results.csv](results/pandas_sample_results.csv)
- [results/spark_market_summary.csv](results/spark_market_summary.csv)
- [results/data_quality_report.txt](results/data_quality_report.txt)
- [scripts/part1_build_dataset.py](scripts/part1_build_dataset.py)
- [scripts/part2_clean_with_pandas.py](scripts/part2_clean_with_pandas.py)
- [scripts/run_spark_analytics.py](scripts/run_spark_analytics.py)
- [scripts/part3_spark_analytics.ipynb](scripts/part3_spark_analytics.ipynb)

