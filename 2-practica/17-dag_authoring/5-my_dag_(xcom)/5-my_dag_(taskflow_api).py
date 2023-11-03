from airflow import DAG
from airflow.operators.python import PythonOperator

# También existe un "dag decorator", así que aquí podemos importarlo escribiendo "dag" 
from airflow.decorators import task, dag

from datetime import datetime, timedelta

# También podemos llamar sólo el decorador @task para utilizar el PythonOperator detrás 
# de escena. Ahora bien, como mejor práctica, te recomiendo encarecidamente que uses siempre 
# "@task", luego "." y "el decorador" que quieras, en ese caso python o virtualenv: 

@task.python
def extract():
    partner_name="netflix"
    partner_path='/partners/netflix'
    return {
            "partner_name":partner_name, 
            "partner_path":partner_path
           }

@task.python
def process():
    print("process")


# y luego crear tu DAG con @dag, quitar el DAG ID "my_dag", así también "as dag". 

@dag(description="DAG in charge of processing customer data",
         start_date=datetime(2021, 1, 1), schedule_interval='@daily',
         dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
         catchup=False, max_active_runs=1)

# Luego define una función "def my_dag" y pones tus tareas, así como tus dependencias, 
# dentro de esa función y "my_dag", aquí, es el DAG ID de tu DAG. Finalmente, llama a la 
# función "my_dag" y eso es todo. 

def my_dag():

    extract() >> process()

my_dag()