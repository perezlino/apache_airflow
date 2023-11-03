'''
=====================
TriggerDagRunOperator
=====================

Este operador permite activar otro DAG a partir de un DAG. Más concretamente, activa un 
DAGRun para un dag id especificado, cuando se cumple una condición. ¿Cómo funciona? Pues 
es bastante sencillo.  Tienes un DAG que es el controlador y otro DAG que es el target. 
Desde el controlador, necesitas instanciar una tarea con el TriggerDagRunOperator. Este 
operador espera múltiples argumentos como un "DAG id" correspondiente al DAG que quieres 
disparar, una función "python callable" donde se comprobará la condición si el DAG target 
puede ser disparado o no y algunos "parámetros" que podrás enviar desde el controlador al 
DAG target. 

Aunque el DAG target se dispare desde el DAG controlador, los dos DAG permanecen independientes.  
El controlador no esperará a que el target termine antes de terminar él mismo. Tener en cuenta 
este comportamiento, ya que puede no ser lo que se desea. Además, dado que el target se dispara 
por el scheduler, es necesario activar su toggle para programarlo (schedule it), de lo contrario, 
sólo se iniciará el DagRun mientras que las tareas esperarán. A diferencia del SubDagOperator 
donde se puede visualizar las tareas ejecutadas de nuestro DAG en la "Graph View", esto no es 
posible hacerlo con el TriggerDagRunOperator. No veremos las tareas ejecutadas del DAG target 
desde Graph View del DAG controlador. Por último, como mejor práctica, se recomienda mantener el 
scheduler interval de sus DAGs target a 'None'.  

'''
import pprint as pp
import airflow.utils.dates
from airflow import DAG
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.operators.dummy_operator import DummyOperator

default_args = {
        "owner": "airflow", 
        "start_date": airflow.utils.dates.days_ago(1)
    }

'''Este DAG se compone de dos tareas que son "trigger_dag" y "last_task". Así que vamos a centrarnos 
en "trigger_dag". Como puedes ver, tenemos los diferentes parámetros "trigger_dag_id" con el dag id 
"triggerdagop_target_dag", que corresponde al task id del DAG target. "provide_context" se establece 
en "True" para proporcionar el contexto necesario para la función python callable "conditionally_trigger". 
Y, por último, "params" con dos pares clave-valor, "condition_param" y "message". Si echamos un vistazo 
a la función "conditionally_trigger" dada por el TriggerDagRunOperator, tenemos un nuevo parámetro 
llamado "dag_run_object". Este parámetro es dado automáticamente por el TriggerDagRunOperator y 
corresponde a una clase simple compuesta por un "run_id" y un "payload". El "payload" permite enviar 
datos desde el DAG controlador al DAG target. Eso es lo que puedes ver aquí. Al atributo payload se le 
asigna un diccionario con un mensaje de par clave-valor que tiene el valor dado desde el parámetro 
"Hi from the controller". Si el valor de "condition_param" es igual a "True" como muestra la condición 
aquí, entonces el "dag_run_object" es retornado y el "triggerdagop_target_dag" del DAG target es disparado.  
La futura versión de Airflow será mucho más fácil utilizar el TriggerDagRunOperator. De hecho, no será 
necesario utilizar un "dag_run_object" para pasar el mensaje, ya que se ha añadido un parámetro llamado 
"conf". También el parámetro "provide_context" será "True" por defecto, así que no necesitaremos definirlo 
más. '''

def conditionally_trigger(context, dag_run_obj):
    if context['params']['condition_param']:
        dag_run_obj.payload = {
                'message': context['params']['message']
            }
        pp.pprint(dag_run_obj.payload)
        return dag_run_obj

with DAG(dag_id="triggerdagop_controller_dag", default_args=default_args, 
            schedule_interval="@once") as dag:
            
    trigger = TriggerDagRunOperator(
        task_id="trigger_dag",
        
        # task id del DAG target
        trigger_dag_id="triggerdagop_target_dag",
        provide_context=True,
        python_callable=conditionally_trigger,
        params={
            'condition_param': True, 
            'message': 'Hi from the controller'
        },
    )

    last_task = DummyOperator(
        task_id="last_task"
    )

    trigger >> last_task