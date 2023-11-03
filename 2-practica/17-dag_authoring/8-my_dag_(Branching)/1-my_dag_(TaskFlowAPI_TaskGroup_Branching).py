'''
En tu data pipeline, imaginemos que quieres extraer datos para Snowflake sólo si el día 
actual es lunes. Luego, para Netflix, quieres extraer los datos sólo si el día actual es 
miércoles y para Astronomer quieres extraer los datos sólo si el día actual es viernes. 
¿Cómo se puede hacer eso, ya que el data pipeline está programado (scheduled) @daily? 
Bueno en ese caso una cosa que puedes hacer es usar el BranchPythonOperator.
'''

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

# Necesitas especificar el task ID de la siguiente tarea que quieres ejecutar de acuerdo 
# a tu condición. Ahora, una cosa que tienes que saber es que siempre debes "retornar (return)" 
# algo. Con BranchPythonOperator si no devuelves un task ID, entonces terminarás con un error. 
# Así que aquí vas a tener un problema para los demás días. Entonces, ¿cómo puedes resolver esto? 
# Bueno, hay diferentes maneras. En primer lugar, puedes modificar el "scheduling interval" de tu 
# "data pipeline", de forma que sólo se active los lunes, miércoles y viernes. O puedes añadir 
# otra tarea, por ejemplo, llamémosla "stop"

def _choosing_partner_based_on_day(execution_date) :
    day = execution_date.day_of_week
    if (day == 1):
        return 'extract_partner_snowflake'
    if (day == 3):
        return 'extract_partner_netflix'
    if (day == 5):
        return 'extract_partner_astronomer'
    # y entonces básicamente vas a ejecutar esa tarea si el día actual no es viernes, miércoles o lunes:
    return 'stop'
    

@dag(description="DAG in charge of processing customer data",
     default_args=default_args, schedule_interval='@daily',
     dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
     catchup=False, max_active_runs=1)

def my_dag():

    start = DummyOperator(task_id='start')

    choosing_partner_based_on_day = BranchPythonOperator(
        task_id='choosing_partner_based_on_day',
        python_callable=_choosing_partner_based_on_day
    )

    # Creamos la tarea "stop"
    stop = DummyOperator(task_id='stop')

    storing = DummyOperator(task_id='storing', trigger_rule='none_failed_or_skipped')

    # Creamos la dependencia
    choosing_partner_based_on_day >> stop

    for partner, details in partners.items():
        @task.python(task_id=f'extract_{partner}',do_xcom_push=False, multiple_outputs=True)

        def extract(partner_name, partner_path): 
            return {
                    "partner_name":partner_name, 
                    "partner_path":partner_path
                }
        extracted_values = extract(details['name'], details['path'])

        # Creamos la dependencia
        start >> choosing_partner_based_on_day >> extracted_values
        process_tasks(extracted_values)

my_dag()