# Lo que se busca es agrupar las tareas, como una tarea downloads para download_a, 
# download_b, y download_c, y una tarea transforms para transform_a, transform_b, 
# y transform_c. Para ello utilizamos "SubDAGs"

from airflow import DAG
from airflow.operators.bash import BashOperator

from datetime import datetime

with DAG('group_dag', start_date=datetime(2022,1,1), 
            schedule_interval='@daily', catchup=False) as dag:
    
    # Definimos el objeto "args" con los parámetros de start_date, schedule_interval 
    # y catchup del Parent DAG que vamos a utilizar en el SubDAG
    args = {'start_date':dag.start_date, 'schedule_interval':dag.schedule_interval, 
                'catchup':dag.catchup}

    download_a = BashOperator(
        task_id = 'download_a',
        bash_command = 'sleep 10'
    )

    download_b = BashOperator(
        task_id = 'download_b',
        bash_command = 'sleep 10'
    )

    download_c = BashOperator(
        task_id = 'download_c',
        bash_command = 'sleep 10'
    )

    check_files = BashOperator(
        task_id = 'check_files',
        bash_command = 'sleep 10'
    )

    transform_a = BashOperator(
        task_id = 'transform_a',
        bash_command = 'sleep 10'
    )

    transform_b = BashOperator(
        task_id = 'transform_b',
        bash_command = 'sleep 10'
    )

    transform_c = BashOperator(
        task_id = 'transform_c',
        bash_command = 'sleep 10'
    )

    [download_a, download_b, download_c] >> check_files
    check_files >> [transform_a, transform_b, transform_c]