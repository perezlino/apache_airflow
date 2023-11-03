'''
Primero creamos dos nuevas funciones que llamaremos "on_success_task" y "on_failure_task". 
De nuevo, no olvides que el contexto dado en los parámetros trae información sobre la 
instancia de la tarea. Entonces voy a imprimir el parámetro de contexto, pero puedes hacer 
lo que quieras en estas callbacks. Como hicimos para el DAG, también imprimimos si estamos 
en el success o failure callback. Yo sólo imprimo información, pero como usamos Python, 
podríamos usar un módulo y notificar a un sistema externo como una base de datos si quieres. 
Como mejor práctica, nuestros callbacks deberían ser muy ligeros, como empujar una 
notificación o limpiar un estado. No debemos poner un proceso pesado, ya que, podría 
ralentizar nuestra aplicación. Realmente depende de nosotros y de nuestro caso de uso el 
saber qué debemos implementar. A continuación, en los argumentos por defecto (default_args), 
añadimos los parámetros 'on_failure_callback' y 'on_success_callback' y asignamos sus 
correspondientes funciones 'on_failure_task' y 'on_success_task'. Por último, añadimos el 
parámetro 'execution_timeout' con un objeto timedelta de 60 segundos. Fíjate que no es 
recomendable utilizar execution timeout así, ya que cada tarea puede tener un execution time 
diferente. Es mejor utilizar este parámetro cuando se define la tarea en la definición del 
operator. Muy bien, ahora eres capaz de reintentar una tarea y ser avisado cuando algo va mal.
'''
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2019, 1, 1),
    'owner': 'Airflow',
    'retries':3,
    'retry_delay':timedelta(seconds=60),
    'emails':['owner@test.com'],
    'email_on_failure':True,
    'email_on_retry':False,
    'on_failure_callback':on_failure_task,
    'on_success_callback':on_success_task,
    'execution_timeout':timedelta(seconds=60)
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
    
    t1 = BashOperator(task_id='t1', bash_command="exit 1")
    
    # Tarea 2
    t2 = BashOperator(task_id='t2', bash_command="echo 'second task'")

    t1 >> t2