'''
Digamos que tienes un DAG que está programado (scheduled) para ejecutarse a la 1:00 AM y por 
algunas razones quieres retrasar la ejecución de una tarea hasta que la hora actual (current 
datetime) sea las 10:00 AM. 

¿Cómo puedes hacerlo sin tener que crear dos DAGs diferentes? 

DateTimeSensor
==============
Bueno, aquí es donde mediante el uso de un sensor se puede lograr esto, y más específicamente, 
es necesario importar el "DatetimeSensor". El objetivo del "DatetimeSensor" es esperar una 
hora (datetime) determinada antes de seguir adelante. 

poke_interval
============
Ahora, hay otros argumentos que puedes usar en todos tus sensores, y el primero es "poke_interval", 
que está establecido en 60 segundos por defecto. Y este argumento define la frecuencia con la que 
su sensor comprobará si su condición es verdadera o no. 

mode
====
Otro argumento que es extremadamente útil es "mode". Y por defecto está definido como "poke". 
¿Cuál es el objetivo de "mode"? Bueno, en primer lugar, tienes que saber que cada vez que una tarea 
se está ejecutando en airflow, entonces se toma un worker slot del "default pool" hasta que se 
complete esa tarea, y como sabes, hay un número limitado de workers slots, y por lo tanto un número 
de tareas que se pueden ejecutar al mismo tiempo. Pero, con el sensor, estás esperando algo, pero si 
ese algo nunca sucede, entonces esperarás para siempre y en realidad la mayor parte del tiempo el 
sensor no hace nada, ¿verdad? Se limita a esperar. Así que estás desperdiciando tus recursos y tu 
tiempo y otras tareas tendrán que esperar hasta que algunos worker slot sean liberados por tus 
sensores, es decir, estás desperdiciando un montón de recursos aquí. Así que por eso siempre que 
estés esperando que el sensor esté tardando más de, digamos 5 minutos o 10 minutos, podría ser útil 
para ti definir ese "mode" a "reschedule", y con ese modo cada hora, en ese caso, el sensor 
comprobará si la condición es cierta o no, si no, el worker slot será liberado para que otra tarea 
pueda ser activada, y 60 minutos más tarde, el sensor tomará un worker slot de nuevo y comprobará la 
condición. 

timeout
=======
Este argumento se establece en "7 dias (seven days)" por defecto. Así que esta es la cosa, ¿qué pasa 
si su condición nunca es verdadera? Bueno, su sensor esperará hasta que se agote el tiempo después de 
siete días. Eso es lo que significa. Y esto es realmente significa un gran problema, porque, si us
tenemos un gran número de sensores a la espera de cosas diferentes, o tal vez la misma cosa, pero su 
condición nunca es verdadera, en algún momento podriamos terminar con un estancamiento, se podría 
terminar en un caso en el que habria capacidad de ejecutar más tareas en toda su instancia de Airflow, 
porque todos sus worker slots serán tomados por sus sensores.

Diferencia entre execution_timeout y timeout
============================================
No debemos confundirnos con el argumento "execution_timeout" que está disponible para cualquier operador, 
y este "no tiene valor por defecto". Entonces, ¿cuál es la diferencia entre "timeout" (que es específico 
de los sensores) y "execution_timeout"? Que en realidad "execution_timeout" está disponible para todos 
los operadores y "timeout" es especifico de los sensors.

soft_fail
=========
Se utiliza en combinación con 'timeout'. Cuando se establece "soft_fail" a "True", tan pronto como su sensor 
se agote (times out), de acuerdo con el timeout (tiempo de espera) especificado, entonces su sensor no fallará, 
pero será omitido. El "execution_timeout", que está disponible para cualquier operador, no tiene en cuenta 
"soft_fail".

exponential_backoff
===================
Finalmente, el último argumento que puede ser útil para usted es "exponential_backoff". Y este cuando se 
establece en "True", aumentará el tiempo de espera entre cada intervalo de tiempo, entre cada "poke interval". 
Así, en lugar de esperar 60 segundos, por ejemplo, en el siguiente intervalo de tiempo, usted esperará tal vez 
70 segundos y así sucesivamente. ¿Por qué esto puede ser útil para usted? Bueno, si usted está, por ejemplo, 
utilizando el HTTPSensor y comprobar si una API está disponible o no, usted no desea enviar una tonelada de 
solicitudes a la misma. Así que, en ese caso, "exponential_backoff" podría ser una buena cosa a utilizar. 
Ahora ya sabes todo lo que necesitas sobre los sensores y no olvides siempre, siempre definir el timeout.

'''
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.decorators import task, dag
from airflow.operators.subdag import SubDagOperator 
from airflow.utils.task_group import TaskGroup
from airflow.operators.dummy import DummyOperator
from airflow.sensors.date_time import DateTimeSensor # Importamos

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

    delay = DateTimeSensor(
        task_id='delay',
        target_time='{{ execution_date.add(hours=9) }}',

        # Aquí está verificando cada 60 segundos si la hora actual (current datetime) es a 
        # las 10:00 AM o no. Podriamos verificar cada hora también, es decir, "poke_interval=60 * 60"
        poke_interval=60 * 60,

        mode = 'reschedule',

        # Como estamos esperando que la hora de la fecha actual (current datetime) debe ser a las 10:00 AM, 
        # en algún momento, entonces podemos decir que estos sensores deben "agotar su tiempo de espera 
        # (timeout)" tan pronto como se está ejecutando durante más de 10 horas. Así que podemos especificar 
        # "60 * 60 * 10". 
        timeout=60 * 60 * 10, 
        soft_fail=True,
        exponential_backoff=True
    )

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