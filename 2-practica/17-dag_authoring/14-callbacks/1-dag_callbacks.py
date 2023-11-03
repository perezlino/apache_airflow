'''
CALLBACKS A NIVEL DE DAG
========================

on_success_callback
on_failure_callback

'''
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.decorators import task, dag
from airflow.operators.subdag import SubDagOperator 
from airflow.utils.task_group import TaskGroup
from airflow.operators.dummy import DummyOperator
from airflow.sensors.date_time import DateTimeSensor

from datetime import datetime, timedelta
from groups.process_tasks_parte2a import process_tasks
import time

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

# Creamos las dos funciones que seran llamadas
def _success_callback(context):
    print(context)

def _failure_callback(context):
    print(context)

# Agregamos los callback a nivel de DAG
@dag(description="DAG in charge of processing customer data",
     default_args=default_args, schedule_interval='@daily',
     dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
     catchup=False, on_success_callback=_success_callback, on_failure_callback=_failure_callback)

def my_dag():

    start = DummyOperator(task_id='start', pool='default_pool', execution_timeout=timedelta(minutes=10))

    delay = DateTimeSensor(
        task_id='delay',
        target_time='{{ execution_date.add(hours=9) }}',
        poke_interval=60 * 60,
        mode = 'reschedule',
        timeout=60 * 60 * 10, 
        soft_fail=True,
        exponential_backoff=True
    )

    storing = DummyOperator(task_id='storing', trigger_rule='none_failed_or_skipped')

    for partner, details in partners.items():
        
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