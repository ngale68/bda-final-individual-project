# Submission Guidelines

## GitHub repository

Use this template repository to create a **new private GitHub repository** for this final project.

Share the private repository with:

```txt
steliosot@msn.com
```

Your repository link must be included in your main `README.md`.

## Tools to use

Use **VSCode** for:

- Team 1: Data Collection
- Team 2: Data Quality
- Python scripts
- pandas cleaning work
- local CSV/log/result files

Use **Google Colab** for:

- Team 3: Spark analytics
- PySpark setup
- Spark SQL queries
- full-dataset analytics

After finishing the Spark notebook in Colab:

1. Go to `File`.
2. Choose `Download`.
3. Download the notebook as `.ipynb`.
4. Add the downloaded notebook to your private GitHub repository.

## Organizing Your Work

You may organize your files in the way that makes most sense to you. You can improvise.

The only rule is that your work must be clear to review. Your main `README.md` should explain where everything is.

A simple suggested structure is:

```txt
final_project/
├── README.md
├── part1_build_dataset.py
├── part2_clean_with_pandas.ipynb
├── part3_spark_analytics.ipynb
├── scripts/
│   ├── get_one_record.py
│   ├── save_dictionary_to_csv.py
│   └── mess_my_data.py
├── reports/
│   ├── report_to_stelios.md
│   └── reflection.md
├── data/
│   ├── clean/
│   │   ├── clean_market_data.csv
│   │   └── cleaned_market_data.csv
│   └── messy/
│       └── messy_market_data.csv
└── results/
    ├── api_download.log
    ├── pandas_sample_results.csv
    ├── runtime_comparison.csv
    └── spark_market_summary.csv
```

You may add more folders, for example:

```txt
notebooks/
scripts/
docs/
reports/
```

## Main README requirement

Your private repository must contain one main `README.md`.

This single README should include:

- your name
- repository link
- a short explanation of the company scenario
- how to run Team 1 code
- how to run Team 2 code
- where to find the Team 3 Colab notebook
- a link to the final report to Stelios
- a link to the reflection
- a list of submitted files

The README does not need to contain all of your code or the full report text. It should explain the project clearly and point to the correct files. Put the repository link, report link, reflection link, and file list directly in this one README.

## Report files

Create a `reports/` folder for written work.

Your report and reflection may be submitted as:

- Markdown files, for example `reports/report_to_stelios.md`
- Word files, for example `reports/report_to_stelios.docx`
- plain text files, for example `reports/report_to_stelios.txt`

Use clear file names so the reviewer can easily find the report and reflection.

## What to submit

Before submitting, check that your private GitHub repository contains:

- `README.md` with repository link, report link, and reflection link
- `scripts/` folder containing `get_one_record.py`, `save_dictionary_to_csv.py`, and `mess_my_data.py`
- `part1_build_dataset.py`
- Team 2 pandas cleaning notebook or script
- downloaded Team 3 Spark `.ipynb` notebook from Colab
- `reports/` folder containing the report and reflection
- `data/clean/clean_market_data.csv` with 10,000 records
- `data/messy/messy_market_data.csv`
- `data/clean/cleaned_market_data.csv`
- `results/api_download.log`
- `results/runtime_comparison.csv`
- `results/pandas_sample_results.csv`
- `results/spark_market_summary.csv`
- data-quality report, either inside the Team 2 notebook/script output or saved in `reports/`
- at least six Spark SQL queries
- ranked market summary table

## Final checklist

Before you finish:

- The repository is private.
- The repository is shared with `steliosot@msn.com`.
- The main `README.md` is complete.
- The report to Stelios is included in `reports/`.
- The reflection is included in `reports/`.
- The README links to the report and reflection files.
- Part 1 runs in VSCode.
- Part 2 runs in VSCode.
- Part 3 was completed in Colab.
- The Colab notebook was downloaded as `.ipynb`.
- All required CSV and result files are present.
- The files are organized clearly.
- No `.venv/` folder is committed.
- No very large unnecessary dataset files are committed.
