# Package a DAG en un archivo ZIP

# ¿Cómo podemos modificar este DAG para empaquetarlo en un archivo zip y hacer el 
# código más limpio? 

# Una cosa que podríamos hacer es eliminar las tres funciones de python del código 
# del DAG y ponerlas en un archivo externo que importaremos si es necesario. Así, 
# en la carpeta dags, creamos una nueva carpeta con el nombre "functions" por ejemplo, 
# y creamos un nuevo archivo python en ella llamado helpers.py, así. Luego, copiamos 
# y eliminamos las tres funciones python del DAG packaged_dag, y las pegamos en 
# helpers.py.

# Además, otro archivo python que debemos crear en la carpeta "functions" es 
# __init__.py. El archivo __init__.py hace que Python trate los directorios que lo 
# contienen como módulos. También es el primer archivo que se carga en un módulo, por 
# lo que se puede utilizar para ejecutar el código que se quiera ejecutar cada vez que se 
# cargue un módulo. Básicamente, sin este archivo, no podríamos importar nuestras funciones 
# del DAG. Notar que el archivo quedará vacío.

# Luego desde la CLI y ubicados en la ruta correcta, enviamos la siguiente linea de comando:
# "zip -rm package_dag.zip packaged_dag.py functions/"

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from functions.helpers import first_task, second_task, third_task

from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2019, 1, 1),
    'owner': 'Airflow'
}

with DAG(dag_id='packaged_dag', schedule_interval="0 0 * * *", default_args=default_args) as dag:

    # Task 1
    python_task_1 = PythonOperator(task_id='python_task_1', python_callable=first_task)

    # Task 2
    python_task_2 = PythonOperator(task_id='python_task_2', python_callable=second_task)

    # Task 3
    python_task_3 = PythonOperator(task_id='python_task_3', python_callable=third_task)

    python_task_1 >> python_task_2 >> python_task_3

