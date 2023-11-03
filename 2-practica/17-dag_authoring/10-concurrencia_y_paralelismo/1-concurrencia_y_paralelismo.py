from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.decorators import task, dag
from airflow.operators.subdag import SubDagOperator 
from airflow.utils.task_group import TaskGroup
from airflow.operators.dummy import DummyOperator

from datetime import datetime, timedelta
from groups.process_tasks_parte2a import process_tasks

partners = {
    "partner_snowflake":
    {
        "name":"snowflake",
        "path":"/partners/snowflake"
    },
    "partner_netflix":
    {
        "name":"netflix",
        "path":"/partners/netflix"
    },
    "partner_astronomer":
    {
        "name":"astronomer",
        "path":"/partners/astronomer"
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
    
''' ¿Y si quieres modificar la "concurrencia" a nivel de DAG? Bueno, puedes hacerlo con 
dos parámetros, y el primero es "concurrency". Así que, si estableces la concurrencia a "2", 
por ejemplo, estás diciendo que puedes ejecutar como máximo dos tareas a la vez en todos los 
DagRuns de un DAG dado. Así que, de nuevo, aquí no estás diciendo que tendrás dos tareas 
ejecutándose al mismo tiempo para cada DagRun, sino que tendrás dos tareas ejecutándose al 
mismo tiempo a través de todos los DagRuns de ese DAG.

Y el otro parámetro que puedes usar es "max_active_runs" igual a "1". Si quieres decir, quiero 
ejecutar un DagRun a la vez para ese DAG específico, o si quieres ejecutar "2" DagRuns a la 
vez para ese DAG específico, puedes especificar "max_active_runs" a "2"
'''

@dag(description="DAG in charge of processing customer data",
     default_args=default_args, schedule_interval='@daily',
     dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
     catchup=False, concurrency=2, max_active_runs=2)

def my_dag():

    '''Ahora está el último nivel, y es el "nivel de tarea" y hay realmente dos parámetros para 
    eso, donde el primero es "task_concurrency", así que por ejemplo, digamos que quieres ejecutar 
    sólo una instancia de "start" a la vez a través de todos los DagRuns de tu DAG. Bien, de nuevo, 
    sólo tienes que especificar "task_concurrency" igual a "1", y entonces no tendrás más de una 
    instancia de tarea correspondiente a "start" ejecutándose a la vez para todos los DagRuns de 
    este DAG.'''
    
    start = DummyOperator(task_id='start', trigger_rule='dummy', task_concurrency=1)

    choosing_partner_based_on_day = BranchPythonOperator(
        task_id='choosing_partner_based_on_day',
        python_callable=_choosing_partner_based_on_day
    )

    stop = DummyOperator(task_id='stop')

    storing = DummyOperator(task_id='storing', trigger_rule='none_failed_or_skipped')

    choosing_partner_based_on_day >> stop

    for partner, details in partners.items():
        @task.python(task_id=f'extract_{partner}',do_xcom_push=False, multiple_outputs=True)

        def extract(partner_name, partner_path): 
            return {
                    "partner_name":partner_name, 
                    "partner_path":partner_path
                }
        extracted_values = extract(details['name'], details['path'])

        start >> choosing_partner_based_on_day >> extracted_values
        process_tasks(extracted_values)

my_dag()