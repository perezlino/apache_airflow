from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago

from datetime import datetime, timedelta

# Argumentos que podemos utilizar de manera transversal en todas las tareas
default_arg = {
    'retry':5,
    'retry_delay':timedelta(minutes=5)
}

with DAG(dag_id='simple_dag', default_args = default_arg, schedule_interval='@daily', 
        start_date=days_ago(3), catchup=False) as dag:

    task_1 = DummyOperator(
        task_id='task_1'
    )

    task_2 = DummyOperator(
        task_id='task_2'
        retry = 3 # En este caso, retry=3 tendrá prioridad sobre retry=5.
    )

    task_3 = DummyOperator(
        task_id='task_3'
    )