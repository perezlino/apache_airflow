from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from datetime import datetime, timedelta

default_arg = {
    'retry':5,
    'retry_delay':timedelta(minutes=5)
}

# Creamos una función para utilizarla en el operador PythonOperator
def _downloading_data():
    print('Esto es una prueba')

with DAG(dag_id='simple_dag', default_args = default_arg, schedule_interval='@daily', 
        start_date=days_ago(3), catchup=False) as dag:

# Utilizamos el operador PythonOperator
    downloading_data = PythonOperator(
        task_id='downloading_data',
        python_callable=_downloading_data
    )