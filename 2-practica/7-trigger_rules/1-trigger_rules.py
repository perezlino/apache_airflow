# Utilizaremos el dag del directorio "branch_dag" y crearemos una cuarta tarea.
# Agreguemos una nueva tarea 't4' después de "t2" y "t3", para que esa tarea 
# dependa de "t2" y "t3". Pero ahora si se ejecuta el DAG la tarea 't4' será 
# 'saltada (skipped)' también. Por qué sucede esto? Porque todas las tareas que 
# están posteriormente (upstream tasks) a una tarea que se ha saltado también se 
# saltan. Así que la pregunta es, ¿cómo se puede evitar esto?. Cómo puedes decir 
# que quieres ejecutar "t2", pero también quieres ejecutar "t4" sea cual sea el 
# resultado de la tarea Branch. Para eso utilizaremos las llamadas "Trigger rules".

from airflow import DAG
from airflow.operators.python import PythonOperator,BranchPythonOperator
from airflow.operators.bash import BashOperator

from datetime import datetime

def _t1(ti):
    ti.xcom_push(key='my_key', value=100)

def _t2(ti):
    ti.xcom_pull(key='my_key', task_ids='t1')

def _branch(ti):
    value = ti.xcom_pull(key='my_key', task_ids='t1')
    if (value == 100):
        return 't2'
    return 't3'

with DAG('xcom_dag', start_date=datetime(2022,1,1), 
            schedule_interval='@daily', catchup=False) as dag:
    
    t1 = PythonOperator(
        task_id = 't1',
        python_callable = _t1
    )

    branch = BranchPythonOperator(
        task_id='branch',
        python_callable = _branch
    )

    t2 = PythonOperator(
        task_id = 't2',
        python_callable = _t2
    )

    t3 = BashOperator(
        task_id = 't3',
        bash_command ="echo ''"
    )

    # Agregamos una cuarta tarea, pero al disparar el DAG esta tarea
    # sera saltada (skipped)
    t4 = BashOperator(
        task_id = 't4',
        bash_command ="echo ''"    
    )

    # Modificamos las dependencias
    t1 >> branch >> [t2, t3] >> t4