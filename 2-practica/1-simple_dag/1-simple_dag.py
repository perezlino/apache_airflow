from airflow import DAG
from airflow.operators.dummy import DummyOperator

from datetime import datetime

with DAG(dag_id='simple_dag', schedule_interval='*/10 * * * *', start_date=datetime(2021,1,1)) as dag:

    task_1 = DummyOperator(
        task_id='task_1'
    )