from os.path import expanduser, join, abspath

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json

warehouse_location = abspath('spark-warehouse')

# Inicializar sesión Spark
spark = SparkSession \
    .builder \
    .appName("Forex processing") \
    .config("spark.sql.warehouse.dir", warehouse_location) \
    .enableHiveSupport() \
    .getOrCreate()

# Leer el archivo forex_rates.json del HDFS
df = spark.read.json('hdfs://namenode:9000/forex/forex_rates.json')

# Elimina las filas duplicadas en función de las columnas base y last_update
forex_rates = df.select('base', 'last_update', 'rates.eur', 'rates.usd', 'rates.cad', 'rates.gbp', 'rates.jpy', 'rates.nzd') \
    .dropDuplicates(['base', 'last_update']) \
    .fillna(0, subset=['EUR', 'USD', 'JPY', 'CAD', 'GBP', 'NZD'])

# Exporta el dataframe a la tabla Hive forex_rates
forex_rates.write.mode("append").insertInto("forex_rates")