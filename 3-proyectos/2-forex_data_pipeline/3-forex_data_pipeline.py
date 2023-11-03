# Esta vez vas a añadir una nueva tarea encargada de comprobar si un archivo específico está disponible 
# o no en tu sistema de archivos (file system). Déjame darte un ejemplo. Digamos que quieres verificar 
# si un archivo o carpeta existe en una ubicación específica de tu sistema de archivos. ¿Cómo puede hacerlo?
# Usando el "FileSensor", el cuál comprobará cada 60 segundos por defecto si un archivo o una carpeta 
# existe en una ubicación específica en el sistema.

from airflow import DAG
from airflow.sensors.http_sensor import HttpSensor
from airflow.sensors.filesystem import FileSensor

from datetime import datetime, timedelta

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
        # Es una referencia a una conexión, y esa conexión es, de hecho, la ruta donde 
        # debe existir el archivo o la carpeta
        fs_conn_id="forex_path",
        # Es el nombre del archivo o la carpeta que estás esperando
        filepath="forex_currencies.csv",
        # Cada cinco segundos va a verificar si la ruta, si el 'forex_path' está disponible o no.
        poke_interval=5,
        # Significa que después de 20 segundos que el sensor se está ejecutando, recibirá un timeout
        timeout=20
    )