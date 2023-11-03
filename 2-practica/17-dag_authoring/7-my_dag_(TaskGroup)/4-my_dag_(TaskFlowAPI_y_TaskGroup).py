'''
¿Qué pasa si tienes el siguiente caso de uso en el que quieres extraer datos de diferentes 
partners, por ejemplo, el partner A, B y C. La cosa es que la forma de extraer datos de tus 
diferentes partners es realmente similar. ¿Tienes que implementar la misma tarea para cada 
uno de tus partners? ¿Qué pasa si tienes como 50 partners diferentes? Obviamente, en algún 
momento podría ser realmente difícil hacer eso y absolutamente no es adecuado, ya que será 
difícil mantener esas tareas. Por lo tanto, una manera es crear esas tareas dinámicamente y 
que sean realmente similares entre sí y sólo poner las pocas diferencias en el diccionario, 
por ejemplo. Así que aquí tendrías un bucle encargado de crear esas tareas dinámicamente, y 
entonces terminarás con la tarea, extract A, luego extract B y extract C. Pero no vas a 
implementar cada tarea una por una. Esas tareas se generarán dinámicamente en base al 
diccionario. 

Ahora aquí está la cosa, tienes que recordar que la creación de tareas de forma dinámica es 
posible sólo si los valores ya se conocen. Airflow necesita conocer de antemano la estructura 
de su Dag, lo que significa que no es capaz de crear tareas dinámicas basadas en la salida de 
una tarea. Puede crear tareas dinámicas basadas en un diccionario o en una variable, o incluso 
en algunas conexiones que tenga en su base de datos, pero todos esos valores ya son conocidos. 
Si tratas de crear tareas dinámicas basadas en la salida de una tarea, por ejemplo, el XCom o 
una SQL request, eso no funcionará, eso cambiará en el futuro, pero ahora mismo es así como 
funciona.

'''
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task, dag
from airflow.operators.subdag import SubDagOperator 
from airflow.utils.task_group import TaskGroup
from airflow.operators.dummy import DummyOperator

from datetime import datetime, timedelta
from groups.process_tasks_parte2a import process_tasks

# Así que, en primer lugar, es necesario definir ese diccionario, que contiene los diferentes 
# valores de acuerdo con el partner con el que se quiere tratar. En ese caso, vamos a crear un 
# diccionario "partners":

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

@dag(description="DAG in charge of processing customer data",
     default_args=default_args, schedule_interval='@daily',
     dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
     catchup=False, max_active_runs=1)

def my_dag():

    # Entonces, por último, pero no menos importante, vamos a añadir una tarea ficticia como el 
    # punto de partida de tu data pipeline
    start = DummyOperator(task_id='start')

    # Definimos el bucle encargado de crear las diferentes tareas "extract" correspondientes a 
    # "snowflake", "netflix" y "astronomer". 
    for partner, details in partners.items():
        @task.python(task_id=f'extract_{partner}',do_xcom_push=False, multiple_outputs=True)

        # Añadimos estos dos argumentos a la función 'extract':
        def extract(partner_name, partner_path): 
            return {
                    "partner_name":partner_name, 
                    "partner_path":partner_path
                }
        extracted_values = extract(details['name'], details['path'])
        start >> extracted_values
        process_tasks(extracted_values)

my_dag()