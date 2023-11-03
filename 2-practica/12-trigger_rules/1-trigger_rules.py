'''
=============
Trigger rules
=============

all_success
===========
'all_success' es la trigger rule por defecto definida para sus tareas. Básicamente, si 
las tarea(s) upstream ha(n) tenido éxito, entonces la tarea siguiente se dispara.  

all_failed
==========
A diferencia de "all_success", una tarea se activará sólo si sus tareas upstream están 
en estado failed o upstream_failed. Si uno de los padres ha tenido éxito, entonces la 
tarea con la trigger rule "all_failed" será omitida (skipped).  

all_done
========
Como puedes adivinar por su nombre, esta regla disparará tu tarea cuando cada tarea upstream 
haya sido ejecutada sea cual sea su estado. No obstante, con la regla 'all_done', la tarea
no se disparará mientras una de sus tareas upstream siga en ejecución.  

one_failed
==========
Activar una tarea tan pronto como 'al menos una' tarea upstream haya fallado. Tenga en cuenta 
que la tarea con la trigger rule 'one_failed' se ejecutará sin esperar a que sus padres terminen,
siempre y cuando al menos uno de los padres haya fallado. La tarea no se disparará y se 'omitirá' 
si todas las tareas upstream han tenido éxito. 

one_success
===========
Activar una tarea tan pronto como 'al menos una' tarea upstream haya tenido éxito. Tenga en cuenta 
que la tarea con la trigger rule 'one_success' se ejecutará sin esperar a que sus padres terminen, 
siempre y cuando al menos uno de los padres haya tenido éxito. La tarea no se disparará y se 'omitirá' 
si todas las tareas upstream han fallado.  

none_failed
===========
En este caso, la tarea se ejecutará sólo si todos los padres no han fallado. Por ejemplo, si un padre
ha tenido éxito y otro se ha omitido, entonces la tarea será capaz de ejecutar. Pero, si alguno de los 
padres está en estado fallido o upstream_failed, entonces la tarea también estará en estado 
upstream_failed.

none_skipped
============
La última trigger rule es "none_skipped", lo que significa que, si ningún padre se encuentra en estado 
omitido, se activará la tarea. De lo contrario, si uno de los padres ha sido omitido, entonces la tarea 
se establecerá con el estado upstream_failed.   

none_failed_or_skipped
======================
Con "non_failed_min_one_success", este es muy útil porque si una de las tareas ha tenido éxito y las otras 
han sido saltadas, entonces task C se dispara. Antes conocida como "none_failed_or_skipped" (antes de 
Airflow 2.2), con esta regla de activación, su tarea se activa si todas las tareas anteriores no han fallado 
y al menos una ha tenido éxito.

dummy
=====
Que en realidad no hace nada, lo que significa que tu tarea se dispara de inmediato. 

'''
import airflow
import requests
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator

default_args = {
    'owner': 'Airflow',
    'start_date': airflow.utils.dates.days_ago(1),
}

def download_website_a():
    print("download_website_a")
    #raise ValueError("error")

def download_website_b():
    print("download_website_b")
    #raise ValueError("error")

def download_failed():
    print("download_failed")
    #raise ValueError("error")

def download_succeed():
    print("download_succeed")
    #raise ValueError("error")

def process():
    print("process")
    #raise ValueError("error")

def notif_a():
    print("notif_a")
    #raise ValueError("error")

def notif_b():
    print("notif_b")
    #raise ValueError("error")

with DAG(dag_id='trigger_rule_dag', 
    default_args=default_args, 
    schedule_interval="@daily") as dag:

    download_website_a_task = PythonOperator(
        task_id='download_website_a',
        python_callable=download_website_a,
        trigger_rule="all_success"
    )

    download_website_b_task = PythonOperator(
        task_id='download_website_b',
        python_callable=download_website_b,
        trigger_rule="all_success"    
    )

    download_failed_task = PythonOperator(
        task_id='download_failed',
        python_callable=download_failed,
        trigger_rule="all_failed"
    )

    download_succeed_task = PythonOperator(
        task_id='download_succeed',
        python_callable=download_succeed,
        trigger_rule="all_success"
    )

    process_task = PythonOperator(
        task_id='process',
        python_callable=process,
        trigger_rule="one_success"
    )

    notif_a_task = PythonOperator(
        task_id='notif_a',
        python_callable=notif_a,
        trigger_rule="none_failed"
    )

    notif_b_task = PythonOperator(
        task_id='notif_b',
        python_callable=notif_b,
        trigger_rule="one_failed"
    )

    # a >> b        : b depende de a
    # [a, b] >> c    : c depende de a y b

    [download_failed_task, download_succeed_task] >> process_task
    [download_website_a_task, download_website_b_task] >> download_failed_task 
    [download_website_a_task, download_website_b_task] >> download_succeed_task
    process_task >> [notif_a_task , notif_b_task]