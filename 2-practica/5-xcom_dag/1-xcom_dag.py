from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from datetime import datetime

# Existen dos maneras de compartir un valor: Utilizando un "return" con el valor
# que se quiere compartir y la otra es utilizando "xcom_push"
def _t1(ti):
    ti.xcom_push(key='my_key', value=100)

# Si se utiliza "xcom_push" para compartir, debemos utilizar "xcom_pull" para
# tomar el valor compartido
def _t2(ti):
    ti.xcom_pull(key='my_key', task_ids='t1')

with DAG('xcom_dag', start_date=datetime(2022,1,1), 
            schedule_interval='@daily', catchup=False) as dag:
    
    t1 = PythonOperator(
        task_id = 't1',
        python_callable = _t1
    )

    t2 = PythonOperator(
        task_id = 't2',
        python_callable = _t2
    )

    t3 = BashOperator(
        task_id = 't3',
        bash_command ="echo ''"
    )

    t1 >> t2 >> t3