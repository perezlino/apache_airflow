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
# Ahora si queremos empujar multiples XComs desde una función, podemos utilizar json, de la
# siguiente manera:

def _extract(ti):
    partner_name="netflix"
    partner_path='/partners/netflix'
    return {
            "partner_name":partner_name, 
            "partner_path":partner_path
           }

# Y haciendo esto empujas el XCom con el JSON value y así múltiples valores dentro de ese XCom, 
# lo cual es definitivamente mucho más optimizado.

# Para recuperar ese XCom, sigue funcionando como antes, pero ahora es "partner_settings". Y si 
# por ejemplo, queremos traer el valor del partner_name:

def _process(ti):
    partner_settings = ti.xcom_pull(task_ids="extract")
    print(partner_settings['partner_name'])

    
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

    extract >> process