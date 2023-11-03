'''
retries y retry_delay
=====================
Puedes definirlos en los argumentos por defecto para que todas las tareas tengan 
la misma configuración de reintento (retry settings), o puedes definirlos en la 
definición del operator para que sólo esa tarea sea reintentada. La elección de 
la primera forma o la segunda depende realmente de tu caso de uso. 

'''

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2019, 1, 1),
    'owner': 'Airflow',
    'retries':3,
    'retry_delay':timedelta(seconds=60)
}

def on_success_dag(dict):
    print('on_success_dag')
    print(dict)

def on_failure_dag(dict):
    print('on_failure_dag')
    print(dict)

with DAG(dag_id='alert_dag', schedule_interval="0 0 * * *", default_args=default_args, 
            catchup=True, dagrun_timeout=timedelta(seconds=45),
            on_success_callback=on_success_dag, on_failure_callback=on_failure_dag) as dag:
    
    # Tarea 1
    # A continuación, cambiamos el bash_command de la tarea t1 para que el scheduler piense 
    # que la tarea ha fallado. Elimine el comando "echo" y escriba "exit 1". Como sabrás, 
    # cuando un programa devuelve un valor distinto de 0, significa que ese programa ha 
    # fallado. Eso es lo que estamos simulando al devolver 1 desde el BashOperator.
    t1 = BashOperator(task_id='t1', bash_command="exit 1")
    
    # Tarea 2
    t2 = BashOperator(task_id='t2', bash_command="echo 'second task'")

    t1 >> t2