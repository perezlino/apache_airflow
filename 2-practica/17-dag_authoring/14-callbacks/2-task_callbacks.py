'''
CALLBACKS A NIVEL DE TAREA
==========================

on_success_callback
on_failure_callback
on_retry_callback

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

def _success_callback(context):
    print(context)

def _failure_callback(context):
    print(context)

def _extract_callback_success(context):
    print('SUCCESS CALLBACK')

'''¿Qué pasa si quieres identificar si tu tarea no tuvo éxito en el "on_failure_callback" 
debido a un "timeout"?
Podemos echar un vistazo a el diccionario "context" y si la tarea no tuvo éxito debido a un "timeout" 
o en realidad debido a un "Error", entonces recibirás una "exception". Así que el primer paso es echar 
un vistazo a el diccionario "context" y si la key "exception" existe. Si es así, entonces puedes filtrar 
en esa excepción. Por ejemplo, si "context["exception"]" es una instancia de AirflowTaskTimeout. Y si 
es así, significa que nuestra tarea no tuvo éxito debido a un timeout. O podemos filtrar la misma 
"exception", pero esta vez, si es un sensor. De nuevo, tienes "AirflowSensorTimeout" y así sucesivamente.

'''
from airflow.exceptions import AirflowTaskTimeout, AirflowSensorTimeout
def _extract_callback_failure(context):
    if (context['exception']):
        if (isinstance(context['exception'], AirflowTaskTimeout)):
            print('FAILURE CALLBACK BECAUSE TIMEOUT')
        if (isinstance(context['exception'], AirflowSensorTimeout)):
            print('FAILURE CALLBACK BECAUSE SENSOR TIMEOUT')

'''La segunda cosa de la que me gustaría hablar es, digamos que quieres saber el número de reintentos que 
ha habido, digamos que quieres saber el número de veces que tu tarea ha sido reintentada en tu callback 
"retry". Bueno, puedes hacer eso. Lo único que tienes que hacer es acceder al objeto instancia de la tarea 
(task instance object) y más concretamente a la propiedad "try_numbers". Así que aquí se podría decir:
'''
def _extract_callback_retry(context):
    if (context['ti'].try_number > 2):
        print('RETRY CALLBACK IS MORE THAN 2')

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
        
        # Agregamos los callbacks a la tarea 'extract'
        @task.python(task_id=f'extract_{partner}', on_success_callback=_extract_callback_success,
                        on_failure_callback=_extract_callback_failure, on_retry_callback=_extract_callback_retry,
                        priority_weight=details['priority'], do_xcom_push=False, pool='partner_pool', 
                        multiple_outputs=True)

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