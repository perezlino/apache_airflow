'''
emails, email_on_failure y email_on_retry
==========================================
Bien, ya hemos visto cómo reintentar una tarea, vamos a añadir una dirección de correo 
electrónico para que podamos recibir un email cuando una tarea no haya tenido éxito. En 
los argumentos por defecto, añadimos la key "emails" con una lista de emails. Por ejemplo, 
owner@test.com. Si realmente quieres recibir un email en caso de fallo o reintento, tienes 
que poner tu dirección de email así como configurar el servidor SMTP en airflow.cfg como 
hicimos en el pipeline de datos FOREX. Por defecto los argumentos 'email_on_failure' y 
'email_on_retry' están configurados a True. Podemos añadirlos en el diccionario así, y 
sólo mantener 'email_on_failure' establecido a True.

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
    'email_on_retry':False
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