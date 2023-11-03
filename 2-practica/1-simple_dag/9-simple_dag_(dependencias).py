from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor 
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.models.baseoperator import chain

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
        fs_conn_id='fs_defaults',
        filepath='mi_archivo.txt'
    )

    processing_data = BashOperator(
        task_id='processing_data',
        bash_command='exit 0'
    )

# DEPENDENCIAS
''' Digamos que queremos ejecutar primero la tarea "downloading_data" luego "waiting_for_data" 
y finalmente "proccesing_data" '''

# Forma 1
# downloading_data.set_downstream(waiting_for_data)
# waiting_for_data.set_downstream(processing_data)

# Forma 2 => Obtenemos el mismo resultado anterior
# processing_data.set_upstream(waiting_for_data)
# waiting_for_data.set_upstream(downloading_data)

# Forma 3 => Obtenemos el mismo resultado anterior
# downloading_data >> waiting_for_data >> processing_data

''' Ahora, ¿qué pasa si tenemos dos tareas que queremos ejecutar al mismo tiempo? Digamos que 
queremos ejecutar "waiting_for_data" y "proccesing_data" tan pronto como "downloading_data" haya 
terminado. Para poner varias tareas en el mismo nivel, lo que significa ejecutar varias tareas 
al mismo tiempo, hay que ponerlas en una lista '''

# downloading_data >> [waiting_for_data, processing_data]

''' Digamos que quieres ejecutar “downloading_data”, luego “waiting_for_data” y finalmente 
“processing_data”. Para ello primero importamos la función: <<chain>>. El resultado final es
equivalente a las depedencias anteriores. '''

# chain[downloading_data, waiting_for_data, processing_data]