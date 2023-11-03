'''
Pools
=====

El concepto de pool es extremadamente simple, tienes un pool con un número de worker 
slots y cada vez que una tarea se está ejecutando entonces esa tarea toma un worker 
slot hasta que la tarea se completa y entonces ese slot se libera. Así es como funciona, 
es tan simple como eso. Y por defecto, todas tus tareas se ejecutan dentro del mismo 
pool llamado "default_pool". ¿Cómo se puede comprobar esto? En Airflow UI, si vas a 
Admin > Pools. Puedes ver el "default_pool", "default_pool" con 128 slots, lo que significa 
que puedes ejecutar como máximo 128 slots al mismo tiempo en toda tu instancia de airflow. 
Obviamente puedes modificar ese número, pero, ¿qué número deberías poner ahí? Eso depende 
de tus recursos y de tus casos de uso, pero tienes que saber que por defecto, siempre que 
una tarea se está ejecutando, si no has especificado ningún pool entonces tu tarea se está 
ejecutando dentro de ese pool. Y como puedes ver tienes "Running slots" y "Queued slots". 
Así que básicamente, si el pool se llena, la siguiente tarea a ejecutar se pondrá en cola y 
verás que el número de "Queued slots" aumenta y tan pronto como la tarea se completa, el 
worker slot se libera y entonces una de las tareas en cola tomará ese worker slot para 
ejecutarse. Así es como funciona. 

¿Y ahora por qué necesitas pools? 

Bueno, porque con los pools puedes definir la "concurrencia", el número de tareas que se 
ejecutan al mismo tiempo para un conjunto específico de tareas. 
'''
'''
En tu data pipeline, imaginemos que quieres extraer datos para Snowflake sólo si el día 
actual es lunes. Luego, para Netflix, quieres extraer los datos sólo si el día actual es 
miércoles y para Astronomer quieres extraer los datos sólo si el día actual es viernes. 
¿Cómo se puede hacer eso, ya que el data pipeline está programado (scheduled) @daily? 
Bueno en ese caso una cosa que puedes hacer es usar el BranchPythonOperator.
'''
'''
Ejemplo
=======

Digamos que esas tareas, "extract_partner_snowflake", "extract_partner_netflix" y 
"extract_partner_astronomer", consumen muchos recursos. Así que una cosa que puedes 
querer es ejecutar una tarea a la vez, pero sólo para este conjunto de tareas (sólo para 
estas tres tareas). 

Mientras que, aún quieres ejecutar tantas tareas como puedas en paralelo, que son 16 por 
defecto para la otra tarea de tu DAG. ¿Cómo hacerlo? Bien, aquí es donde necesitas crear 
un "pool". Creas un nuevo pool con un worker slot, y asignas ese pool a todas esas tareas 
"extract_partner_snowflake", "extract_partner_netflix" y "extract_partner_astronomer". 
Así que el primer paso es crear ese pool en Airflow UI:

    - pool: partner_pool
    - slots: 1
    - description: Pool for extract tasks

pool_slots
==========

Adicionalmente, notas importantes sobre los pools. La primera es que hay un argumento que 
puedes usar en cualquier operador que se llama "pool_slots" con el valor por defecto fijado 
en "1", y este argumento define el número de worker slots que toma una tarea dada.

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
    

@dag(description="DAG in charge of processing customer data",
     default_args=default_args, schedule_interval='@daily',
     dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
     catchup=False, max_active_runs=1)

def my_dag():

    start = DummyOperator(task_id='start')

    # choosing_partner_based_on_day = BranchPythonOperator(
    #     task_id='choosing_partner_based_on_day',
    #     python_callable=_choosing_partner_based_on_day
    # )

    # stop = DummyOperator(task_id='stop')

    storing = DummyOperator(task_id='storing', trigger_rule='none_failed_or_skipped')

    # choosing_partner_based_on_day >> stop

    for partner, details in partners.items():

        # Haciendo esto, en lugar de ejecutar "extract" dentro del pool "default_pool", vas a ejecutar 
        # "extract" dentro del pool "partner_pool", que tiene un worker slot y así tendrás una tarea 
        # ejecutándose a la vez. Sólo para comprobar si funciona, necesitas comentar algunas líneas aquí, 
        # así que primero comenta "choosing_partner_based_on_day" ya que quieres ejecutar todas las tareas 
        # extract. Lo mismo para "stop".

        @task.python(task_id=f'extract_{partner}', pool_slots=3, do_xcom_push=False, pool='partner_pool', 
                        multiple_outputs=True)

        def extract(partner_name, partner_path): 

            # Entonces la última cosa que puedes hacer es usar "sleep" para que realmente puedas ver si tus 
            # tareas se ejecutan de una en una, de lo contrario, será demasiado rápido. Así que primero 
            # importa time y utiliza "sleep".
            time.sleep(3)
            return {
                    "partner_name":partner_name, 
                    "partner_path":partner_path
                }
        extracted_values = extract(details['name'], details['path'])
        start >> extracted_values
        process_tasks(extracted_values)

my_dag()