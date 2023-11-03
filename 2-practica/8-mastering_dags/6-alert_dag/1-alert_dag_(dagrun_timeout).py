# Dado que Airflow es el orquestador de sus data pipelines, es crítico ser advertido 
# cuando una tarea no tuvo éxito o si uno de nuestros DAGs está siendo más lento en 
# terminar y así sucesivamente. Lo bueno es que Airflow nos ofrece muchas formas de 
# monitorizar nuestros DAGs y asegurarnos de que todo funciona como debería. 

# Hay dos niveles de detección de fallos, uno para los DAGs y otro para las tareas.

# DAG failure detections:
#   - dagrun_timeout
#   - max_active_runs
#   - sla_miss_callback
#   - on-failure_callback
#   - on_success_callback

# Task failure detections
#   - email_on_failure
#   - email_on_retry
#   - retries
#   - retry_delay
#   - retry_exponential_backoff
#   - on-failure_callback
#   - on_success_callback
#   - on_retry_callback

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2019, 1, 1),
    'owner': 'Airflow'
}

# Fijamos el dagrun_timeout en 45 segundos. En caso de que el DagRun supere este tiempo
# fallará.

# En primer lugar, aunque este DAGRun haya fallado, el siguiente podrá seguir ejecutándose. 
# No hay una forma estándar de evitar que Airflow programe una DAGRun si el anterior ha fallado. 
# Además, si estableces una de las tareas con el parámetro 'depends_on_past', esta tarea podrá 
# seguir ejecutándose para el siguiente DAGRun ya que su instancia anterior tuvo éxito aunque 
# el DAGRun esté marcado como fallido. Finalmente, si recuerdas, dije que el parámetro 
# 'dagrun_timeout' se aplica si el número de DAGRuns activos es igual al número de 
# 'max_active_runs_per_dag'. Ahora, si echamos un vistazo rápidamente al valor de este parámetro 
# en airflow.cfg, podemos ver que está establecido en 16. Entonces, ¿por qué ha funcionado? 
# Bueno, porque estamos utilizando el "Sequential Executor" y Airflow automáticamente baja este 
# valor a "1".

with DAG(dag_id='alert_dag', schedule_interval="0 0 * * *", default_args=default_args, 
            catchup=True, dagrun_timeout=timedelta(seconds=45)) as dag:
    
    # Tarea 1
    t1 = BashOperator(task_id='t1', bash_command="echo 'first task'")
    
    # Tarea 2
    t2 = BashOperator(task_id='t2', bash_command="echo 'second task'")

    t1 >> t2