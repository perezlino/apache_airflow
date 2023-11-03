# El proceso de Backfilling le permite ejecutar o volver a ejecutar DAG Runs pasados 
# no disparados o ya disparados. Por ejemplo, imaginemos que hemos cometido un error en 
# nuestro DAG. Pues bien, planteamos nuestro DAG, digamos que durante cinco días y tan 
# pronto como arreglamos el problema, queremos empezar a programar (scheduling) las tareas 
# de nuevo. Obviamente durante este periodo de tiempo, terminamos con DAG Runs no disparados. 
# Por defecto, tan pronto como empezemos a programar (scheduling) nuestro DAG de nuevo, todos 
# los DAG Runs no disparados durante ese periodo de tiempo serán automáticamente 
# disparados por Airflow.

# Hay dos maneras de configurar el parámetro catchup. O bien decides establecerlo 
# localmente en la instanciación de tu DAG. O bien decides cambiar el valor por 
# defecto desde el archivo de configuración "airflow.cfg" en el parámetro llamado 
# catchup_ by_default, que por defecto, es igual a True, catchup_ by_default = True.

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2019, 1, 1),
    'owner': 'Airflow'
}

with DAG(dag_id='backfill', schedule_interval="0 0 * * *", default_args=default_args, 
            catchup=False) as dag:
    
    # Task 1
    bash_task_1 = BashOperator(task_id='bash_task_1', bash_command="echo 'first task'")
    
    # Task 2
    bash_task_2 = BashOperator(task_id='bash_task_2', bash_command="echo 'second task'")

    bash_task_1 >> bash_task_2