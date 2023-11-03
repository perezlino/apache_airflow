# En este punto se ha creado con éxito una función "subdag_downloads" que devuelve 
# un DAG, el SubDAG con las tareas "download" que se quiere agrupar. Y este es 
# realmente el primer paso para crear un SubDAG. El siguiente paso es hacer la primera 
# importación, que es el "SubDagOperator". El "SubDagOperator" es el encargado de llamar 
# al SubDAG que acabas de crear, "subdag_downloads" que se encuentra en la carpeta
# "subdags". 

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.subdag import SubDagOperator # Importamos SubDagOperator
from subdags.subdag_downloads import subdag_downloads # Importamos la función

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

    # Modifico la nueva dependencia "downloads"
    downloads >> check_files
    check_files >> [transform_a, transform_b, transform_c]