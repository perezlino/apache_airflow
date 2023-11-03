# Ahora debemos realizar los mismos pasos anteriores pero para las tareas
# "transform". Crearemos un nuevo subdag "subdag_transforms" dentro de la 
# carpeta "subdags".

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.subdag import SubDagOperator # Importamos SubDagOperator
from subdags.subdag_downloads import subdag_downloads # Importamos la función
from subdags.subdag_transforms import subdag_transforms # Importamos la función

from datetime import datetime

with DAG('group_dag', start_date=datetime(2022,1,1), 
            schedule_interval='@daily', catchup=False) as dag:
    
    # Definimos el objeto "args" con los parámetros de start_date, schedule_interval 
    # y catchup del Parent DAG que vamos a utilizar en el SubDAG
    args = {'start_date':dag.start_date, 'schedule_interval':dag.schedule_interval, 
                'catchup':dag.catchup}

    # Eliminamos las tareas "download_x" y las reemplazamos por la tarea SubDagOperator
    downloads = SubDagOperator(
        task_id = 'downloads',
        subdag = subdag_downloads(dag.dag_id,'downloads',args)
    )

    check_files = BashOperator(
        task_id = 'check_files',
        bash_command = 'sleep 10'
    )

    # Eliminamos las tareas "transform_x" y las reemplazamos por la tarea SubDagOperator
    transforms = SubDagOperator(
        task_id = 'transforms',
        subdag = subdag_transforms(dag.dag_id,'transforms',args)
    )

    # Modifico la nueva dependencia "downloads" y "transforms"
    downloads >> check_files
    check_files >> transforms