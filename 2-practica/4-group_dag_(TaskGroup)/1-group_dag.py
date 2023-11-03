# A veces es bastante complicado agrupar tus tareas, y por eso están obsoletas desde 
# Airflow 2.2, en su lugar vas a utilizar un nuevo concepto, que es el concepto de 
# TaskGroups.

from airflow import DAG
from airflow.operators.bash import BashOperator
from groups.group_downloads import download_tasks
from groups.group_transforms import transform_tasks

from datetime import datetime

with DAG('group_dag', start_date=datetime(2022,1,1), 
            schedule_interval='@daily', catchup=False) as dag:

    # Eliminamos las tareas "download_x" y las reemplazamos por la tarea downloads
    downloads = download_tasks()

    check_files = BashOperator(
        task_id = 'check_files',
        bash_command = 'sleep 10'
    )

    # Eliminamos las tareas "transform_x" y las reemplazamos por la tarea transforms
    transforms = transform_tasks()

    # Modifico la nueva dependencia "downloads" y "transforms"
    downloads >> check_files >> transforms