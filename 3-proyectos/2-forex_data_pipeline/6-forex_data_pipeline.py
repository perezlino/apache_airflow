# Una vez que nuestros datos están almacenados en tu HDFS, el siguiente paso es 
# encontrar una forma de interactuar con ellos. Y como nuestros datos están almacenados 
# como un archivo de texto, obviamente no queremos abrir ese archivo y buscar los datos. 
# En su lugar, una cosa que podemos hacer es utilizar Hive. Con Hive vamos a crear una tabla 
# sobre los datos, sobre nuestros archivos, para que podamos consultar nuestros datos 
# ejecutando consultas tipo SQL. 

from airflow import DAG
from airflow.sensors.http_sensor import HttpSensor
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python_operator import PythonOperator
from airflow.providers.apache.hive.operators.hive import HiveOperator # Importamos el operador

from datetime import datetime, timedelta

import csv
import requests
import json

default_args = {
            "owner": "airflow",
            "start_date": datetime(2019, 1, 1),
            "email_on_failure": False,
            "email_on_retry": False,
            "email": "youremail@host.com",
            "retries": 1,
            "retry_delay": timedelta(minutes=5)
        }

# Download forex rates according to the currencies we want to watch
# described in the file forex_currencies.csv
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

with DAG(dag_id="forex_data_pipeline", schedule_interval="@daily", default_args=default_args, catchup=False) as dag:
    
    is_forex_rates_available = HttpSensor(
        task_id="is_forex_rates_available",
        method="GET",
        http_conn_id="forex_api",
        endpoint="latest",
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

    # ¿Qué hace esta tarea? Bueno, 'creating_forex_rates_table' utiliza el 'HiveOperator' 
    # para ejecutar la siguiente consulta 'hql'. Y esa consulta no hace otra cosa que crear 
    # una tabla con las siguientes columnas: base, last update, eur, usd, nzd y demás, 
    # correspondientes exactamente al detalle que tienes en '/forex_rates.json' Una vez que 
    # tienes esto, establece el 'task_id' y se debe crear la conexión 'hive_conn' como se 
    # define aquí. Como vas a interactuar con Hive, necesitas crear la conexión correspondiente.
    # Esta conexión también debe crearse en Airflow UI.

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