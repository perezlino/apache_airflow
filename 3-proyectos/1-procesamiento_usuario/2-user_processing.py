# Es momento de extraer los datos de esa API. Y para ello vamos a utilizar el "SimpleHttpOperator"
# Debemos importar ese operador y también necesitamos importar JSON.

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator

import json

from datetime import datetime

with DAG('user_processing', start_date=datetime(2022,12,22),
            schedule_interval='@daily', catchup=False) as dag:
    
    create_table = PostgresOperator(
        task_id = 'create_table',
        postgres_conn_id = 'postgres',
        sql = '''
            CREATE TABLE IF NOT EXISTS users (
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                country TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL
            );
             '''
        )

    # Sensor que comprobará si la API está disponible o no.
    is_api_available = HttpSensor(
        task_id = 'is_api_available',
        http_conn_id = 'user_api',
        endpoint = 'api/'
    )

    extract_user = SimpleHttpOperator(
        task_id = 'extract_user',
        http_conn_id = 'user_api',
        endpoint = 'api/',
        method = 'GET',
        # Trae la información en formato String (response.text) y luego la transformamos a un
        # diccionario python (json.loads(response.text)) y queda almacenado en la variable 'response'
        response_filter = lambda response: json.loads(response.text),
        # Luego, por último, pero no menos importante, queremos registrar (log) la respuesta para que 
        # usted sea capaz de ver la respuesta que se obtiene en los logs en la interfaz de usuario.
        log_response = True
    )