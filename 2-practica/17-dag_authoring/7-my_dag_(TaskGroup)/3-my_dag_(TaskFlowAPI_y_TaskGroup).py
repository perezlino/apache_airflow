'''
Esta es una continuación del dag 2-my_dag_(TaskFlowAPI_y_TaskGroup).py.

Ahora, ¿qué pasa si quieres tener un taskgroup dentro de un taskgroup? ¿puedes hacer eso? 
Sí, se puede. Sólo tienes que volver a "process_tasks", y digamos que, además de esas tareas, 
tienes "checking tasks", así que vamos a crear esas tareas.
'''

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task, dag
from airflow.operators.subdag import SubDagOperator 
from airflow.utils.task_group import TaskGroup # Importamos

from datetime import datetime, timedelta
from groups.process_tasks_parte2a import process_tasks

@task.python(task_ID='extract_partners',do_xcom_push=False, multiple_outputs=True)
def extract(): 
    partner_name="netflix"
    partner_path='/partners/netflix'
    return {
            "partner_name":partner_name, 
            "partner_path":partner_path
           }

default_args = {
     'start_date':datetime(2021, 1, 1)
}

@dag(description="DAG in charge of processing customer data",
     default_args=default_args, schedule_interval='@daily',
     dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
     catchup=False, max_active_runs=1)

def my_dag():

    partner_settings = extract()

    process_tasks(partner_settings)

my_dag()