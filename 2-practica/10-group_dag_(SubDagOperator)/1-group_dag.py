'''
================================
Agrupando tus tareas con SubDags
================================

Tenemos tres tareas llamadas 'start', 'check' y 'final' con dos SubDags. El primero 
llamado 'subdag-1' entre 'start' y 'check'. Y el segundo llamado 'subdag-2' entre 
'check' y 'final'. Si tomamos la tarea 'subdag-1' como ejemplo, se utiliza un 
SubDagOperator con el parámetro "subdag" tomando el "factory method" que crea el subdag.  
Esta función toma tres parámetros. El primero es el nombre del DAG padre que es 
"group_subdag" definido por la variable "DAG_NAME". El segundo parámetro es el nombre 
del subdag que es "subdag-1". Y el último parámetro corresponde a los parámetros por 
defecto establecidos para el DAG padre que aplicamos también al subdag. ¿Por qué? Porque 
si recuerdas, tenemos que mantener una especie de coherencia entre el padre y el hijo 
con el 'start_date' y 'scheduling_interval' para evitar comportamientos inesperados.  
Entonces, ¿de dónde viene la función factory_method? Si nos fijamos, hemos hecho una 
importación desde el archivo 'subdag'. Así que, si abres este archivo desde la carpeta 
subdags, obtienes el factory method.   

En el archivo 'subdag.py' tenemos los tres parámetros utilizados para instanciar un objeto 
DAG. Por convención, el dag_id de un subdag está compuesto, primero, por el DAG id del 
padre y luego el DAG id del subdag separados por un punto. Luego, el bucle crea 5 tareas 
en el subdag. En resumen, necesitas crear un 'factory method' en un archivo externo encargado 
de devolver un objeto DAG. Entonces, este objeto DAG es tu SubDAG que se adjuntará a tu DAG 
padre con el operador SubDagOperator. Antes de seguir adelante, se estableció el "Sequential 
Executor" para cada SubDagOperator. Ese es el executor por defecto. Si quitas este parámetro 
obtendrás el mismo comportamiento. 

Es importante mencionar que Dado que, por defecto, el SubDagOperator se establece con el 
Sequential Executor, este es el comportamiento normal, incluso si Airflow se está ejecutando 
con el Celery Executor. Entonces, ¿cómo podemos ejecutar múltiples tareas en paralelo incluso 
en SubDags? Bueno, para ello, cambia de 'Sequential Executor' a 'Celery Executor' para ambos 
subdags.  

'''


import airflow
from subdags.subdag import factory_subdag
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.subdag_operator import SubDagOperator
from airflow.executors.sequential_executor import SequentialExecutor
from airflow.executors.celery_executor import CeleryExecutor

DAG_NAME="group_dag"

default_args = {
    'owner': 'Airflow',
    'start_date': airflow.utils.dates.days_ago(2)
}

with DAG(dag_id=DAG_NAME, default_args=default_args, 
            schedule_interval="@once") as dag:
            
    start = DummyOperator(
        task_id='start'
    )

    subdag_1 = SubDagOperator(
        task_id='subdag-1',
        subdag=factory_subdag(DAG_NAME, 'subdag-1', default_args),
        #executor=SequentialExecutor()
        executor=CeleryExecutor()
    )

    some_other_task = DummyOperator(
        task_id='check'
        )

    subdag_2 = SubDagOperator(
        task_id='subdag-2',
        subdag=factory_subdag(DAG_NAME, 'subdag-2', default_args),
        #executor=SequentialExecutor()
        executor=CeleryExecutor()
    )

    end = DummyOperator(
        task_id='final'
    )

    start >> subdag_1 >> some_other_task >> subdag_2 >> end