from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task, dag
from airflow.operators.subdag import SubDagOperator # Importamos

from datetime import datetime, timedelta
from subdags.subdag_factory_parte2 import subdag_factory # Importamos

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

    # Ya no utilizamos 'partner_settings' dado que genera errores
    # partner_settings = extract()

    process_tasks = SubDagOperator(
        task_id="process_tasks",

        # Una vez que ejecutemos el DAG en Airflow UI aparecerá un error, un "error de importación", y 
        # dado que estamos intentando establecer relaciones entre tareas en más de un DAG, entre el 
        # "sub dag" y el "parent dag". ¿Por qué se produce este error? Pues porque estamos utilizando 
        # la Taskflow API. Así que en "partner_settings=extract()", es en realidad igual a los "XCom args" 
        # correspondientes a los diferentes XComs que has empujado, "partner_name" y "partner_path". 
        # Recordemos que la Taskflow API intentará hacer las dependencias automáticamente por ti. Y al 
        # pasar los "XCom args" a la función "subdag_factory" se estará tratando de crear relaciones, 
        # dependencias entre las tareas de su DAG y las tareas de su SubDag, y esto no es posible hacerlo 
        # en Airflow. No se pueden definir dependencias entre una tarea de un DAG y otra tarea de otro DAG. 
        # Por tanto, eliminamos el argumento "partner_settings" de subdag:
 
        subdag=subdag_factory("my_dag", "process_tasks", default_args)
    )

    extract() >> process_tasks

my_dag()