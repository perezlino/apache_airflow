from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor 
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.models.baseoperator import cross_downstream

from datetime import datetime, timedelta

default_arg = {
    'retry':5,
    'retry_delay': timedelta(minutes=5)
}

# ----------------------------------------------------------------------------------------------------------------------------

def _downloading_data():
    with open('/tmp/mi_archivo.txt','w') as archivo:
        archivo.write('mis_datos')
        return 50  # <== return value 

def _checking_data(ti):
    mi_xcom = ti.xcom_pull(key='return_value', task_ids=['downloading_data']) # Extraigo el xcom desde "_downloading_data"
    print(mi_xcom) # Imprimo el valor extraido desde "_downloading_data"

'''Así es como puedes compartir datos entre tus tareas utilizando XComs. Usted empuja (push) el XCom usando 
la palabra clave "return" y luego obtiene el XCom de la meta database de Airflow usando "xcom_pull" '''

# Otra forma de empujar (push) su XCom es usando "xcom_push":

# def _downloading_data(ti):
#     with open('/tmp/mi_archivo.txt','w') as archivo:
#         archivo.write('mis_datos')
#     ti.xcom_push(key='mi_key', value='100')

# def _checking_data(ti):
#     mi_xcom = ti.xcom_pull(key='mi_key', task_ids=['downloading_data']) # Extraigo el xcom desde "_downloading_data"
#     print(mi_xcom) # Imprimo el valor extraido desde "_downloading_data"

# ----------------------------------------------------------------------------------------------------------------------------

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

downloading_data >> waiting_for_data >> processing_data