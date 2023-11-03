# En este punto, usted es capaz de crear una tabla y verificar si la API está disponible o no

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.sensors.http import HttpSensor

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