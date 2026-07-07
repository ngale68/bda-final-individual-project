import os
import subprocess
import sys
from pathlib import Path


def configure_java() -> str:
    candidates = []
    if os.environ.get('JAVA_HOME'):
        candidates.append(os.environ['JAVA_HOME'])

    candidates.extend([
        '/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home',
        '/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home',
        '/Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home',
        '/Library/Java/JavaVirtualMachines/jdk-21.jdk/Contents/Home',
        '/usr/lib/jvm/java-17-openjdk',
        '/usr/lib/jvm/default-java',
    ])

    for candidate in candidates:
        if not candidate:
            continue
        java_home = Path(candidate).expanduser()
        java_bin = java_home / 'bin' / 'java'
        if java_bin.exists():
            os.environ['JAVA_HOME'] = str(java_home)
            os.environ['PATH'] = f"{java_home / 'bin'}:{os.environ.get('PATH', '')}"
            return str(java_home)

    raise RuntimeError('No compatible Java runtime was found. Install Java 17 or 21 and retry.')


project_root = Path(__file__).resolve().parent.parent
input_path = project_root / 'data' / 'clean' / 'cleaned_market_data.csv'
output_path = project_root / 'results' / 'spark_market_summary.csv'

if not input_path.exists():
    raise FileNotFoundError(f'Could not find the cleaned dataset at {input_path}')

configure_java()

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark = (
    SparkSession.builder.master('local[*]')
    .appName('market-data-spark-analytics')
    .config('spark.sql.shuffle.partitions', '2')
    .getOrCreate()
)

print('Spark session started')
print(f'Loaded file: {input_path}')

df = (
    spark.read.option('header', True)
    .option('inferSchema', True)
    .csv(str(input_path))
)

for col in ['open_time', 'close_time']:
    if col in df.columns:
        df = df.withColumn(col, F.to_timestamp(F.col(col)))

for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume', 'trade_count']:
    if col in df.columns:
        df = df.withColumn(col, F.col(col).cast('double'))

if 'price_range' not in df.columns:
    df = df.withColumn('price_range', F.col('high') - F.col('low'))
if 'price_change' not in df.columns:
    df = df.withColumn('price_change', F.col('close') - F.col('open'))
if 'percent_change' not in df.columns:
    df = df.withColumn('percent_change', (F.col('price_change') / F.col('open')) * 100)
if 'candle_direction' not in df.columns:
    df = df.withColumn(
        'candle_direction',
        F.when(F.col('close') > F.col('open'), 'up')
         .when(F.col('close') < F.col('open'), 'down')
         .otherwise('flat')
    )

df = df.withColumn('trade_date', F.date_format('open_time', 'yyyy-MM-dd'))
df = df.withColumn('trade_hour', F.hour('open_time'))
df = df.withColumn('day_of_week', F.date_format('open_time', 'EEE'))

df.createOrReplaceTempView('market_data')

print('Temporary SQL view created: market_data')
print('Row count:', df.count())

# Task 2/3/4 evidence
print('Test query returned rows:', spark.sql('SELECT * FROM market_data LIMIT 10').count())
print('Created/verified columns: price_range, price_change, percent_change, candle_direction')
print('Created time features: trade_date, trade_hour, day_of_week')

volatility = spark.sql('''
SELECT symbol,
       AVG(price_range) AS avg_price_range,
       STDDEV(price_range) AS stddev_price_range
FROM market_data
GROUP BY symbol
ORDER BY avg_price_range DESC, stddev_price_range DESC
''')
volatility = volatility.withColumn('volatility_rank', F.row_number().over(Window.orderBy(F.desc('avg_price_range'))))

activity = spark.sql('''
SELECT symbol,
       SUM(trade_count) AS total_trades,
       SUM(quote_volume) AS total_quote_volume,
       AVG(volume) AS avg_volume
FROM market_data
GROUP BY symbol
ORDER BY total_trades DESC, total_quote_volume DESC
''')
activity = activity.withColumn('activity_rank', F.row_number().over(Window.orderBy(F.desc('total_trades'))))

summary = spark.sql('''
SELECT symbol,
       COUNT(*) AS total_records,
       AVG(volume) AS avg_volume,
       SUM(trade_count) AS total_trades,
       AVG(percent_change) AS avg_percent_change,
       AVG(price_range) AS avg_price_range,
       SUM(CASE WHEN candle_direction = 'up' THEN 1 ELSE 0 END) AS up_count,
       SUM(CASE WHEN candle_direction = 'down' THEN 1 ELSE 0 END) AS down_count,
       SUM(CASE WHEN candle_direction = 'flat' THEN 1 ELSE 0 END) AS flat_count
FROM market_data
GROUP BY symbol
''')

summary = summary.join(volatility.select('symbol', 'volatility_rank'), 'symbol', 'left')
summary = summary.join(activity.select('symbol', 'activity_rank', 'total_quote_volume'), 'symbol', 'left')
summary = summary.orderBy(F.desc('total_trades'), F.desc('avg_price_range'))

summary = summary.withColumn(
    'interpretation',
    F.concat_ws(' ', F.lit('Activity:'), F.col('symbol'), F.lit('was active and ranked by volatility'), F.col('volatility_rank'))
)

summary_df = summary.toPandas()
summary_df.to_csv(output_path, index=False)

print(f'Final ranked market summary created')
print(f'Rows in summary: {summary_df.shape[0]}')
print(f'Saved: {output_path}')

activity_symbol = activity.orderBy(F.desc('total_trades')).first().symbol
volatility_symbol = volatility.orderBy(F.desc('avg_price_range')).first().symbol
print(f'Top activity symbol: {activity_symbol}')
print(f'Top volatility symbol: {volatility_symbol}')
print(f'Interpretation: {activity_symbol} had the highest trading activity, while {volatility_symbol} had the widest average price range.')

spark.stop()
