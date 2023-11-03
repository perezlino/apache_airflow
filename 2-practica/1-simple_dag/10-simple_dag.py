from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor 
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.models.baseoperator import cross_downstream # Importamos cross_downstream

from datetime import datetime, timedelta

default_arg = {
    'retry':5,
    'retry_delay': timedelta(minutes=5)
}

def _downloading_data():
    with open('/tmp/mi_archivo.txt','w') as archivo:
        archivo.write('mis_datos')

def _checking_data():
    print('check data')


with DAG(dag_id='simple_dag', default_args = default_arg, schedule_interval='@daily', 
        start_date=days_ago(3), catchup=False) as dag:

    downloading_data = PythonOperator(
        task_id='downloading_data',
        python_callable=_downloading_data
    )

    checking_data = PythonOperator(
        task_id = 'checking_data',
        python_callable = _checking_data
    )

    waiting_for_data = FileSensor(
        task_id='waiting_for_data',
        fs_conn_id='fs_defaults',
        filepath='mi_archivo.txt'
    )

    processing_data = BashOperator(
        task_id='processing_data',
        bash_command='exit 0'
    )

# CROSS DOWNSTREAM
''' Digamos que queremos ejecutar "downloading_data" y "checking_data" antes de "waiting_data". 
Además, queremos ejecutar "downloading_data" y "checking_data" antes de "proccesing_data". Así 
que básicamente, queremos crear dependencias entre "downloading_data", "checking_data" y 
"waiting_for_data" y "proccesing_data". Así que "waiting_for_data" depende de "checking_data" y 
"downloading_data" y "proccesing_data" depende de "checking_data" y "downloading_data". 
¿Cómo se pueden crear estas dependencias cruzadas (cross_dependencies)? '''

cross_downstream([downloading_data, checking_data], [waiting_for_data, processing_data])