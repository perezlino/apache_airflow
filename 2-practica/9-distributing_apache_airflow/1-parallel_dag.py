'''
===========================================================================
Ejecución de tareas en paralelo con el Local Executor y el Celery Executor
===========================================================================

Podemos modificar la configuración de Airflow para controlar el número de tareas que 
queremos ejecutar en paralelo.En realidad, hay tres parámetros en los que tenemos que 
centrarnos.

-------------------------------- A NIVEL DE AIRFLOW --------------------------------

parallelism
===========
Determina cuántas instancias de tareas se pueden ejecutar activamente en paralelo a 
través de DAGs (número de tareas que se pueden ejecutar al mismo tiempo para toda su 
instancia airflow). Se puede considerar como el máximo global de tareas activas. Se 
establece por defecto en 32.

dag_concurrency
===============
Te permite establecer el número máximo de tareas que se pueden ejecutar por DAG. 
Determina cuántas instancias de tarea puede programar el scheduler a la vez por DAG.
Define el número de tareas que se pueden ejecutar al mismo tiempo para un DAG dado. 
Se establece por defecto en 16. Con esto, estás diciendo que puedes ejecutar como 
máximo 16 tareas al mismo tiempo para todos los DagRuns de un DAG determinado.

max_active_runs_per_dag
=======================
El parámetro 'max_active_runs_per_dag' le dice al scheduler que no ejecute más que el 
número definido de DAGRuns en un momento dado para un DAG específico. Por ejemplo, si 
establecemos el max_active_runs_per_dag a 1, el DAGRun # 1 se ejecuta primero y una vez 
que termina, se dispara el DAGRun # 2. Fíjate que este parámetro establece el número máximo 
de DAGRuns activos por DAG y se aplicará a todos tus DAGs. Se establece en 16 por defecto.
Con esto, estás diciendo que puedes tener como máximo 16 DagRuns ejecutándose al mismo 
tiempo para un DAG dado. Si quieres ser más específico, puedes personalizar este número a 
nivel de DAG estableciendo el parámetro 'max_active_runs' en la definición del objeto DAG. 

===========
==EJEMPLO==
===========

Tenemos dos DAGs, DAG #1 y DAG #2 (Son dos DAGs distintos), donde ambos DAG tienen cinco 
tareas c/u, donde tres de ellas se pueden ejecutar en paralelo. Tarea 1, 2 y 3. La tarea 4 
depende del éxito de las tres tareas, entonces una vez que la tarea 4 se hace, la tarea 5 
se dispara. 

Por ejemplo, si establecemos: 

- parallelism en 3
- dag_concurrency en 2 

Entonces sólo se ejecutarán las tareas 1 y 2 del DAG # 1, y la tarea 1 del DAG # 2. 
¿Por qué? Porque hemos definido que el número máximo de tareas que se pueden ejecutar en 
paralelo por DAG es dos con el parámetro dag_concurrency. Significa que estás limitado 
a ejecutar hasta dos tareas al mismo tiempo por DAGRun. 

Resumiendo, en ese momento teníamos globalmente tres tareas ejecutándose en paralelo con un 
límite de dos por DAGRun.

Celery Executor
===============

worker_concurrency
==================
Este parámetro determina cuántas tareas 'puede' procesar un solo worker. Por defecto se 
establece en 16. 

------------------------------------ A NIVEL DE DAG ------------------------------------

concurrency
===========
Lo mismo que dag_concurrency pero aplicandolo en un DAG especifico

max_active_runs
===============
Lo mismo que max_active_runs_per_dag pero aplicandolo en un DAG especifico


----------------------------------- A NIVEL DE TAREA -----------------------------------

task_concurrency
================

'''

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

from datetime import datetime

default_args = {
    'start_date': datetime(2019, 1, 1),
    'owner': 'Airflow',
    'email': 'owner@test.com'
}

def process(p1):
    print(p1)
    return 'done'

with DAG(dag_id='parallel_dag', schedule_interval='0 0 * * *', 
            default_args=default_args, catchup=False) as dag:
    
    # Tareas 1, 2 y 3 generadas dinámicamente
    tasks = [BashOperator(
        task_id='task_{0}'.format(t), 
        bash_command='sleep 5'.format(t)) for t in range(1, 4)]

    task_4 = PythonOperator(
        task_id='task_4', 
        python_callable=process, 
        op_args=['my super parameter'])

    task_5 = BashOperator(
        task_id='task_5', 
        bash_command='echo "pipeline done"')

    tasks >> task_4 >> task_5  