'''
depends_on_past
===============

- Si quieres ejecutar una tarea determinada sólo si esta tarea ha terminado con 
  éxito o ha sido omitido en el DAGRun anterior, entonces establece 'depends_on_past' 
  a True. Por cierto, este parámetro está establecido en False por defecto.

- Este parámetro se aplica a nivel de tarea, por lo que puede definir específicamente 
  una tarea para que dependa de su instancia anterior, o puede aplicar el parámetro a 
  todas las tareas utilizando el diccionario 'default_args.

- Si se aplica 'depends_on_past' a una tarea, y la misma tarea en el DagRun anterior
  falló, la tarea actual no se ejecutará y NO TENDRÁ STATUS.

- Y dado que las tareas no tienen ningún estado, no terminan con un fallo o algo así, 
  nada, es por eso que siempre debes especificar un "timeout" de lo contrario, tu DagRun 
  seguirá corriendo para siempre. 

- Si disparas tu DagRun manualmente, entonces "depends_on_past" será evaluado, es decir, 
funciona también para DagRuns disparados manualmente.
'''
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator

from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2019, 1, 1),
    'owner': 'Airflow'
}

def second_task():
    print('Hello from second_task')
    #raise ValueError("Esto convertirá la tarea python en estado 'failed'")

def third_task():
    print('Hello from third_task')
    #raise ValueError("Esto convertirá la tarea python en estado 'failed'")

# Entendiendo que el Schedule_interval está configurado para ejecutarse cada medianoche 
# a partir del 01/01/2019:
with DAG(dag_id='depends_task', schedule_interval="0 0 * * *", default_args=default_args) as dag:
    
    # Tarea 1
    bash_task_1 = BashOperator(
      task_id='bash_task_1', 
      bash_command="echo 'first task'"
    )
    
    # Tarea 2
    # Agregamos a la tarea python_task_2 la dependencia depends_on_past=True
    python_task_2 = PythonOperator(
      task_id='python_task_2', 
      python_callable=second_task,
      depends_on_past=True
    )

    # Tarea 3
    python_task_3 = PythonOperator(
      task_id='python_task_3', 
      python_callable=third_task
    )

    bash_task_1 >> python_task_2 >> python_task_3