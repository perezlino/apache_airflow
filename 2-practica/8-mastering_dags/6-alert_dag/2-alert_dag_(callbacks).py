# Además de tener un timeout, quizás quisieras o hacer algo si el DAGRun ha fallado o ha 
# tenido éxito. Bueno, podríamos añadir los callbacks on_failure_callback así como 
# on_success_callback.

# Hagamos esto. Justo encima de la definición del DAG, creamos dos funciones denominadas 
# respectivamente on_success_dag y on_failure_dag pero puedes darle los nombres que quieras. 
# No olvides que estos dos callbacks toman un "diccionario de contexto" en parámetros que 
# vamos a mostrar en la salida estándar, añadiendo una instrucción print para cada uno. 
# Podemos añadir otro print para saber a qué callback se llama. Finalmente, añadimos los 
# parámetros on_success_callback y on_failure_callback a la definición del DAG que asignamos 
# a las funciones que acabamos de hacer.

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2019, 1, 1),
    'owner': 'Airflow'
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
    t1 = BashOperator(task_id='t1', bash_command="echo 'first task'")
    
    # Tarea 2
    t2 = BashOperator(task_id='t2', bash_command="echo 'second task'")

    t1 >> t2