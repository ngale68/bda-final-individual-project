# Big Data Analytics Final Project

## Your First Week at Owl Analytics

This repository contains the final project brief and starter folder structure.

Start here:

1. [Welcome](01_Welcome.md)
2. [Team 1: Data Collection](02_Team1_Data_Collection.md)
3. [Team 2: Data Quality](03_Team2_Data_Quality.md)
4. [Team 3: Analytics](04_Team3_Analytics.md)
5. [Report and Reflection](05_Report_and_Reflection.md)
6. [Submission Guidelines](06_Submission_Guidelines.md)
7. [Rubric](07_Rubric.md)

## Starter Structure

The repository includes folders for the files you will generate:

```txt
data/clean/
data/messy/
results/
reports/
```

Your datasets, logs, notebooks, reports, and result files should be created by your own code during the project. Do not commit a `.venv/` folder.

### Provided Scripts

The `scripts/` folder already contains small helper scripts:

- `get_one_record.py`: tests the Binance API by downloading one `BTCUSDT` record.
- `save_dictionary_to_csv.py`: shows how to save one Python dictionary as a CSV row.
- `mess_my_data.py`: creates the messy dataset for Team 2 after you complete Team 1.

Run the first two scripts before building `part1_build_dataset.py`. Run `mess_my_data.py` only after you have created `data/clean/clean_market_data.csv`.
