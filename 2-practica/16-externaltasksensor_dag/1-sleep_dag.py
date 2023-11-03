import pprint as pp
import airflow.utils.dates
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta

default_args = {
        "owner": "airflow", 
        "start_date": airflow.utils.dates.days_ago(1)
    }

''' "t1" no hace nada y "t2" ejecuta el bash command sleep para pausar el DAG durante 
30 segundos. Antes de programar los DAGs, observa que "start_date" y "schedule_dag" 
son iguales en ambos Dags'''

with DAG(dag_id="sleep_dag", default_args=default_args, 
            schedule_interval="@daily") as dag:

    t1 = DummyOperator(task_id="t1")

    t2 = BashOperator(
            task_id="t2",
            bash_command="sleep 30"
        )
    
    t1 >> t2