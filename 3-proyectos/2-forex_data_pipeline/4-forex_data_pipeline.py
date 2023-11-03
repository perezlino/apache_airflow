# Ahora debemos trabajar con el operador Python. ¿Pero que función tendrá? Primero, revisemos 
# el archivo 'forex_currencies.csv', y allí podemos ver, que hay algunas divisas (currencies), 
# como el EURO y el USD, así como algunos pares. Básicamente, lo que vas a hacer con la función 
# python es descargar el par de divisas (pair of currencies) correspondiente, según la divisa base, 
# por ejemplo, si la divisa base es el USD, entonces vas a descargar el par de divisas, USD-EUR, 
# USD-NZD, USD-JPY, USD-GBP y así sucesivamente. Y una vez que tengamos esos pares de divisas, un 
# nuevo archivo, 'forex_currencies.json', contendrá todos los pares de divisas para dos divisas base, 
# EURO y USD. Solo ten en cuenta que, con esta función, vas a descargar los pares de divisas de acuerdo 
# a la moneda base que utilices ya sea USD o EURO.

from airflow import DAG
from airflow.sensors.http_sensor import HttpSensor
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python_operator import PythonOperator # Importamos este operador

from datetime import datetime, timedelta

import csv       # Importamos
import requests  # Importamos
import json      # Importamos

default_args = {
    "owner": "airflow",
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "admin@localhost.com",
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

# Descarga los tipos de cambio (forex rates) según las divisas (currencies) que queremos ver
# descritas en el archivo forex_currencies.csv
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

default_args = {
    "owner": "airflow",
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "admin@localhost.com",
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

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

    # Creamos la nueva tarea con el operador PythonOperator
    downloading_rates = PythonOperator(
            task_id="downloading_rates",
            python_callable=download_rates
    )