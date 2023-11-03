# Una vez que eres capaz de extraer el usuario de la API, el siguiente paso es procesar ese 
# usuario. Y para ello vas a crear una nueva tarea con PythonOperator. Primero importamos el 
# operador python y a continuación importamos "json_normalize", ya que vamos a normalizar unos 
# datos. 

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator # Importamos este operador

import json
from pandas import json_normalize # Importamos json_normalize de la libreria Pandas
from datetime import datetime

def _process_user(ti):
    user = ti.xcom_pull(task_ids="extract_user")
    user = user['results'][0]
    processed_user = json_normalize({
        'firstname':user['name']['first'],
        'lastname':user['name']['last'],
        'country':user['location']['country'],
        'username':user['login']['username'],
        'password':user['login']['password'],
        'email':user['email']
    })
    processed_user.to_csv('/tmp/processed_user.csv', index=None, header=False)

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

    process_user = PythonOperator(
        task_id = 'process_user',
        python_callable = _process_user
    )