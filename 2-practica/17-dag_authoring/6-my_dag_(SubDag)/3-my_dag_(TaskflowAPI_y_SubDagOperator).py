from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task, dag
from airflow.operators.subdag import SubDagOperator 

from datetime import datetime, timedelta
from subdags.subdag_factory_parte2 import subdag_factory

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

    process_tasks = SubDagOperator(
        task_id="process_tasks",
        subdag=subdag_factory("my_dag", "process_tasks", default_args),

        # En primer lugar, hay que saber que el "Subdag Operator" es un sensor detrás de escena, 
        # lo que significa que espera a que las tareas dentro del SubDag se completen antes de 
        # avanzar y también puedes especificar, por ejemplo, un "poke_interval", por ejemplo, si 
        # quieres comprobar que las tareas dentro del SubDag se completan cada 15 segundos, entonces 
        # puedes poner "poke_interval=15".
        poke=15,

        # También para evitar acabar con el bloqueo, puedes usar el "mode reschedule". 
        mode='reschedule'
    )

    extract() >> process_tasks

my_dag()