from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from datetime import datetime, timedelta

default_arg = {
    'retry':5,
    'retry_delay': timedelta(minutes=5)
}

# Obtenemos la "execution date" del contexto de nuestro DagRun (DagRun context)

# Forma 1
def _downloading_data(ds):
    print(ds)  # INFO - 2022-12-21

# # Forma 2
# def _downloading_data(**context):
#     print(context['ds'])


with DAG(dag_id='simple_dag', default_args = default_arg, schedule_interval='@daily', 
        start_date=days_ago(3), catchup=False) as dag:

    downloading_data = PythonOperator(
        task_id='downloading_data',
        python_callable=_downloading_data
    )