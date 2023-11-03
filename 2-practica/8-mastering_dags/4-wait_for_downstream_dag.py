'''
wait_for_downstream
===================

- Este parámetro le permite imponer que una tarea X determinada, espere a que, tanto 
  "la misma tarea X" como "la tarea(s) inmediatamente posterior" a su instancia anterior 
  terminen con éxito antes de ejecutarse. 

  Tarea inmediatamente posterior de A será B:               A --> B --> C
  Tareas inmediatamente posterior de A serán B y C:         A --> [B, C] --> D

- Este parámetro se aplica a nivel de tarea, por lo que puede definir específicamente 
  una tarea para que dependa de su instancia anterior, o puede aplicar el parámetro a 
  todas las tareas utilizando el diccionario 'default_args.

- 'wait_for_downstream' es realmente útil cuando tienes múltiples DAGRuns con la misma 
  tarea X trabajando al mismo tiempo y esta es utilizada por tareas posteriores (downstream).

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
    # Agregamos a la tarea bash_task_1 la dependencia wait_for_downstream=True
    bash_task_1 = BashOperator(
      task_id='bash_task_1', 
      bash_command="echo 'first task'",
      wait_for_downstream=True
    )
    
    # Tarea 2
    python_task_2 = PythonOperator(
      task_id='python_task_2', 
      python_callable=second_task,
    )

    # Tarea 3
    python_task_3 = PythonOperator(
      task_id='python_task_3', 
      python_callable=third_task
    )

    bash_task_1 >> python_task_2 >> python_task_3