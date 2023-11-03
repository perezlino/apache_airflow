'''
==================
ExternalTaskSensor
==================

Un sensor es un tipo especial de operador que espera a que algo suceda. Pues eso es 
exactamente lo que hace el ExternalTaskSensor pero esta vez espera a que una tarea externa 
termine antes de pasar a las siguientes tareas, y así es como se pueden crear dependencias 
entre DAGs. Primero, necesitamos dos DAGs, DAG 1 (con las tareas t1,t2 y t3) y DAG 2 (con las
tareas sensor,t4 y t5). Ambos DAGs tienen el mismo "schedule_interval". Esto es importante de 
entender. El ExternalTaskSensor asume que ambos DAGs están en el misma execution date. Si tus 
DAGs no tienen la misma "execution date", pero, aun así, tienen el mismo "schedule_interval", 
aún puedes usar el sensor modificando los parámetros "execution_delta" y "execution_date_fn". 
Por lo tanto, ambos DAGs tienen los mismos schedule intervals y se están ejecutando. En este 
ejemplo, el DAG 2 esperará a que termine la última tarea del DAG 1 para pasar a las siguientes. 
¿Cómo? Usando el ExternalTaskSensor como primera tarea esperando a que la tarea t3 del DAG 1 
tenga éxito. Así que después de un tiempo, t1 y t2 del DAG 1 tuvieron éxito, ahora t3 se está 
ejecutando mientras que la tarea del sensor está esperando que t3 tenga éxito también. Cada 
minuto, el sensor comprueba si el estado de t3 ha cambiado. En algún momento, t3 termina, el 
sensor se da cuenta de este nuevo estado y entonces el DAG 2 puede continuar con las siguientes 
tareas t4 y t5 hasta que el DAGRun termine también.  

'''
import pprint as pp
import airflow.utils.dates
from airflow import DAG
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta

default_args = {
        "owner": "airflow", 
        "start_date": airflow.utils.dates.days_ago(1)
    }

'''Como puedes ver, el ExternalTaskSensor se instancia con los parámetros "external_dag_id" y 
"external_task_id". Como puedes adivinar, el primero corresponde al dag id donde está la tarea 
que estamos vigilando y el segundo corresponde al task id de esa tarea. En resumen, estamos 
esperando a que termine la tarea 't2' en el dag "sleep_dag" para iniciar la siguiente tarea 
"last_task" en este DAG. '''

with DAG(dag_id="externaltasksensor_dag", default_args=default_args, 
            schedule_interval="@daily") as dag:
    sensor = ExternalTaskSensor(
        task_id='sensor',
        external_dag_id='sleep_dag',
        external_task_id='t2'    
    )

    last_task = DummyOperator(task_id="last_task")

    sensor >> last_task