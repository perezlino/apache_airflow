from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from datetime import datetime, timedelta

default_arg = {
    'retry':5,
    'retry_delay':timedelta(minutes=5)
}

# Obtenemos el contexto de nuestro DagRun (DagRun context)
def _downloading_data(**context):
    print(context)

with DAG(dag_id='simple_dag', default_args = default_arg, schedule_interval='@daily', 
        start_date=days_ago(3), catchup=False) as dag:

    downloading_data = PythonOperator(
        task_id='downloading_data',
        python_callable=_downloading_data
    )