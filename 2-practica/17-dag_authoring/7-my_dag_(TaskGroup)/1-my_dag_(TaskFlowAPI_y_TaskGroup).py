'''
Esta es la forma 1 para crear TaskGroup sin la necesidad de crear y utilizar archivos 
externos
'''

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task, dag
from airflow.operators.subdag import SubDagOperator 
from airflow.utils.task_group import TaskGroup # Importamos

from datetime import datetime, timedelta

@task.python(task_ID='extract_partners',do_xcom_push=False, multiple_outputs=True)
def extract(): 
    partner_name="netflix"
    partner_path='/partners/netflix'
    return {
            "partner_name":partner_name, 
            "partner_path":partner_path
           }

@task.python
def process_a(partner_name, partner_path):
    print(partner_name)
    print(partner_path)

@task.python
def process_b(partner_name, partner_path):
    print(partner_name)
    print(partner_path)

@task.python
def process_c(partner_name, partner_path):
    print(partner_name)
    print(partner_path)

default_args = {
     'start_date':datetime(2021, 1, 1)
}

@dag(description="DAG in charge of processing customer data",
     default_args=default_args, schedule_interval='@daily',
     dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
     catchup=False, max_active_runs=1)

def my_dag():

    partner_settings = extract()

    with TaskGroup(group_id='process_task') as process_tasks:

        process_a(partner_settings['partner_name'], partner_settings['partner_path'])
        process_b(partner_settings['partner_name'], partner_settings['partner_path'])
        process_c(partner_settings['partner_name'], partner_settings['partner_path'])

my_dag()