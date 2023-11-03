'''
Imaginemos que para este data pipeline quieres ejecutar primero "extract_partner_netflix", 
luego la tarea "extract_partner_snowflake" y finalmente quieres ejecutar la tarea 
"extract_partner_astronomer".  

¿Cómo puede hacerlo? Bueno, una cosa que hay que saber es que cualquier operador en airflow 
tiene un argumento llamado "priority_weight", y este argumento se establece en "1" por defecto, 
lo que significa que, si usted tiene algunas tareas en el mismo nivel y utiliza el "Sequential executor" 
para ejecutar una tarea a la vez, el scheduler elegirá al azar una tarea entre todas esas tareas. 
¿Por qué? Porque todas tienen el mismo peso de prioridad. Ahora, puedes modificar esto cambiando este 
argumento, así que veamos cómo hacerlo. En su editor de código, vamos a añadir una nueva key para cada 
uno de sus partners llamado "priority":
'''


from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.decorators import task, dag
from airflow.operators.subdag import SubDagOperator 
from airflow.utils.task_group import TaskGroup
from airflow.operators.dummy import DummyOperator

from datetime import datetime, timedelta
from groups.process_tasks_parte2a import process_tasks
import time

# Así que una cosa que hay que saber es que cuanto mayor sea el número, mayor prioridad tiene la 
# tarea.
partners = {
    "partner_snowflake":
    {
        "name":"snowflake",
        "path":"/partners/snowflake",
        "priority":2

    },
    "partner_netflix":
    {
        "name":"netflix",
        "path":"/partners/netflix",
        "priority":3
    },
    "partner_astronomer":
    {
        "name":"astronomer",
        "path":"/partners/astronomer",
        "priority":1
    }
}

default_args = {
     'start_date':datetime(2021, 1, 1)
}

def _choosing_partner_based_on_day(execution_date) :
    day = execution_date.day_of_week
    if (day == 1):
        return 'extract_partner_snowflake'
    if (day == 3):
        return 'extract_partner_netflix'
    if (day == 5):
        return 'extract_partner_astronomer'
    return 'stop'
    
@dag(description="DAG in charge of processing customer data",
     default_args=default_args, schedule_interval='@daily',
     dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
     catchup=False, max_active_runs=1)

def my_dag():

    start = DummyOperator(task_id='start')

    storing = DummyOperator(task_id='storing', trigger_rule='none_failed_or_skipped')

    for partner, details in partners.items():
        
        # Si esas tareas "snowflake", "netflix" y "astronomer" se ejecutan en el orden definido por 
        # las prioridades, primero "netflix", "snowflake" y finalmente "astronomer", eso es porque 
        # comparten el mismo pool. Si tienen diferentes pools, entonces no funcionará.

        # Tener en cuenta que las prioridades sólo funcionan si se aplican con el mismo pool. Y por 
        # cierto, "si disparas tu DAG manualmente, las prioridades de tus tareas no se tendrán en cuenta".

        # Una última cosa que puedes hacer para asegurarte de que un DAG se prioriza frente a otro DAG, es 
        # definir dentro del argumento por defecto de tu DAG, "priority weights" y establecerlo en 99, por 
        # ejemplo. Ok, así todas las tareas de tu DAG tendrán un peso de prioridad más alto que el otro DAG 
        # que se establecerá en "1" por defecto
        
        @task.python(task_id=f'extract_{partner}', priority_weight=details['priority'], do_xcom_push=False, 
                        pool='partner_pool', multiple_outputs=True)

        def extract(partner_name, partner_path): 

            time.sleep(3)
            return {
                    "partner_name":partner_name, 
                    "partner_path":partner_path
                }
        extracted_values = extract(details['name'], details['path'])
        start >> extracted_values
        process_tasks(extracted_values)

my_dag()