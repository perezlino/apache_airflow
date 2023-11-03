'''
Limitaciones de los XComs
=========================

Lo primero que tienes que saber es que los XComs tienen un tamaño limitado. ¿Qué tamaño? 
Esto depende de tu meta database:

* Con SQLite estás limitado a 2 gigabytes para un XCom determinado. 
* Con Postgres estás limitado a 1 GB para un XCom dado 
* Con MySQL entonces eres capaz de almacenar como máximo 64 kilobytes en un XCom dado. 

Por eso tienes que tener mucho cuidado con el tamaño de los datos que compartes entre tus 
tareas y, de hecho, como mejor práctica deberías usar XComs sólo para compartir una pequeña 
cantidad de dato.

'''
from airflow import DAG
from airflow.operators.python import PythonOperator 

from datetime import datetime, timedelta

'''Tienes un valor en "extract", digamos, partner_name="netflix", digamos 
que netflix es tu partner y entonces quieres compartir estos datos con tu tarea "process". 
Para hacer eso, necesitas crear tu XCom, y para crear ese XCom necesitas acceder al "task 
instance" object. Así que al utilizar el PythonOperator, para acceder al "task instance" 
object, sólo tienes que escribir "ti".

Y si te preguntas qué es el "task instance" object, pues básicamente cada vez que disparas tu 
tarea en Airflow esa tarea se convierte en un "task instance". Y con su "task instance" object, 
puede acceder al contexto de la tarea y al mecanismo XCom.

'''
# En el DAG anterior empujamos (push) el XCom con "xcom_push" accediendo al "task instance" 
# object, bastante simple. Pero, lo podemos hacer aún más simple que eso. Podemos simplemente 
# retornar un valor, así, por ejemplo, "return partner_name" como queremos compartir "partner_name" 
# y al hacer esto vamos a empujar el XCom con el valor "partner_name" y la key "return_value", 
# que es la key por defecto, cada vez que se crea el XCom así:

def _extract(ti):
    partner_name="netflix"
    return partner_name

# Es absolutamente lo mismo que antes, pero esta vez la key es "return_value". Así que para 
# recuperar este XCom de la meta database en la tarea "process" tienes que modificar la key con 
# "return_value":

def _process(ti):
    partner_name = ti.xcom_pull(key="return_value", task_ids="extract")
    print(partner_name)

# o simplemente eliminar esa key y usar solo el task ID. 
# def _process(ti):
#     partner_name = ti.xcom_pull(task_ids="extract")
#     print(partner_name)
    
with DAG("my_dag", description="DAG in charge of processing customer data",
         start_date=datetime(2021, 1, 1), schedule_interval='@daily',
         dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
         catchup=False, max_active_runs=1) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=_extract
    )

    process = PythonOperator(
        task_id="process",
        python_callable=_process
    )