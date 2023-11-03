# Vamos a ejecutar un Spark job desde el data pipeline. Recordar esto, Airflow es un 
# orquestrador, por lo que no se debe procesar terabytes o gigabytes de datos en Airflow, 
# en el operador python. En su lugar, deberiamos desencadenar (trigger) un Spark job donde 
# el procesamiento de terabytes de datos está hecho, proceso hecho en spark, y Airflow te 
# permite desencadenar (trigger) ese Spark job. Pero no debemos procesar terabytes de datos 
# en Airflow. De lo contrario, terminará con un error de desbordamiento de memoria 
# (memory overflow error). Y de nuevo, Airflow es un orquestador, el cual es el mejor 
# orquestador, pero no confundirlo con un framework de procesamiento. Aquí está el script 
# que vas a desencadenar (trigger) en Spark. No voy a entrar en detalles aquí, pero 
# básicamente creas una 'SparkSession', luego lees el archivo 'forex_rates.json' de tu HDFS 
# y luego haces algo de procesamiento en él para finalmente insertar los datos procesados 
# en la "forex rate hive table" que has creado en el vídeo anterior. Pero ten en cuenta que 
# este script te permite insertar los datos de tu archivo 'forex_rates.json', en la tabla Hive 
# que has creado.


from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.apache.hive.operators.hive import HiveOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator # Importamos

from datetime import datetime, timedelta
import csv
import requests
import json

default_args = {
    "owner": "airflow",
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "admin@localhost.com",
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

def download_rates():
    BASE_URL = "https://gist.githubusercontent.com/marclamberti/f45f872dea4dfd3eaa015a4a1af4b39b/raw/"
    ENDPOINTS = {
        'USD': 'api_forex_exchange_usd.json',
        'EUR': 'api_forex_exchange_eur.json'
    }
    with open('/opt/airflow/dags/files/forex_currencies.csv') as forex_currencies:
        reader = csv.DictReader(forex_currencies, delimiter=';')
        for idx, row in enumerate(reader):
            base = row['base']
            with_pairs = row['with_pairs'].split(' ')
            indata = requests.get(f"{BASE_URL}{ENDPOINTS[base]}").json()
            outdata = {'base': base, 'rates': {}, 'last_update': indata['date']}
            for pair in with_pairs:
                outdata['rates'][pair] = indata['rates'][pair]
            with open('/opt/airflow/dags/files/forex_rates.json', 'a') as outfile:
                json.dump(outdata, outfile)
                outfile.write('\n')

def _get_message() -> str:
    return "Hi from forex_data_pipeline"

with DAG("forex_data_pipeline", start_date=datetime(2021, 1 ,1), 
    schedule_interval="@daily", default_args=default_args, catchup=False) as dag:

    is_forex_rates_available = HttpSensor(
        task_id="is_forex_rates_available",
        http_conn_id="forex_api",
        endpoint="marclamberti/f45f872dea4dfd3eaa015a4a1af4b39b",
        response_check=lambda response: "rates" in response.text,
        poke_interval=5,
        timeout=20
    )

    is_forex_currencies_file_available = FileSensor(
        task_id="is_forex_currencies_file_available",
        fs_conn_id="forex_path",
        filepath="forex_currencies.csv",
        poke_interval=5,
        timeout=20
    )

    downloading_rates = PythonOperator(
        task_id="downloading_rates",
        python_callable=download_rates
    )

    saving_rates = BashOperator(
        task_id="saving_rates",
        bash_command="""
            hdfs dfs -mkdir -p /forex && \
            hdfs dfs -put -f $AIRFLOW_HOME/dags/files/forex_rates.json /forex
        """
    )

    creating_forex_rates_table = HiveOperator(
        task_id="creating_forex_rates_table",
        hive_cli_conn_id="hive_conn",
        hql="""
            CREATE EXTERNAL TABLE IF NOT EXISTS forex_rates(
                base STRING,
                last_update DATE,
                eur DOUBLE,
                usd DOUBLE,
                nzd DOUBLE,
                gbp DOUBLE,
                jpy DOUBLE,
                cad DOUBLE
                )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
        """
    )

    # Aquí están los pocos parámetros que tiene que especificar. Primero, el 'task_id', 
    # como siempre, como cualquier otro operator, tienes que especificar el task_id. 
    # El segundo parámetro es 'application', application es la ruta del script que vas 
    # a ejecutar. Luego el 'connection_id', el id de la conexión para interactuar con 
    # Spark. Por último, puedes especificar 'verbose = False' para evitar producir 
    # demasiados logs. De lo contrario, será más difícil buscar la información que 
    # queremos de los logs. Así que pon 'verbose = False'.
    
    forex_processing = SparkSubmitOperator(
        task_id="forex_processing",
        application="/opt/airflow/dags/scripts/forex_processing.py",
        conn_id="spark_conn",
        verbose=False
    )