from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor 
from airflow.operators.bash import BashOperator # Agregamos BashOperator
from airflow.utils.dates import days_ago

from datetime import datetime, timedelta

default_arg = {
    'retry':5,
    'retry_delay': timedelta(minutes=5)
}

def _downloading_data():
    with open('/tmp/mi_archivo.txt','w') as archivo:
        archivo.write('mis_datos')

with DAG(dag_id='simple_dag', default_args = default_arg, schedule_interval='@daily', 
        start_date=days_ago(3), catchup=False) as dag:

    downloading_data = PythonOperator(
        task_id='downloading_data',
        python_callable=_downloading_data
    )

    waiting_for_data = FileSensor(
        task_id='waiting_for_data',
        fs_conn_id='fs_default',
        filepath='mi_archivo.txt'
    )

    '''Tenemos que especificar el comando Bash que queremos ejecutar. Para ello añadimos el 
    parámetro "bash_command" igual a "exit 0". Lo que significa que esta tarea sale con el 
    código escrito 0 y por lo tanto tiene éxito.'''

    processing_data = BashOperator(
        task_id='processing_data',
        bash_command='exit 0'
    )