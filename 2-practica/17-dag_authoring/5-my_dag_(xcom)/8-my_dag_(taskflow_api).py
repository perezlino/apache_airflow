from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator

from datetime import datetime
from typing import Dict

@dag(start_date=datetime(2021,1,1), catchup=False)

def my_etl():

    @task
    def extract() -> Dict[str, str]:
        return {
            'path':'/tmp/data',
            'filename':'data.csv'
        }

    process = BashOperator(
        task_id='process',
        bash_command="echo '{{ti.xcom_pull(key='path', task_ids=['extract'])}}'"
    )

    extract() >> process

my_etl() 

# La tarea process obtiene el siguiente resultado --> 
# [2023-01-07, 17:53:11 UTC] {subprocess.py:86} INFO - Output:
# [2023-01-07, 17:53:11 UTC] {subprocess.py:93} INFO - [/tmp/data]