from airflow import DAG
from airflow.models import Variable  # Importamos
from airflow.operators.python import PythonOperator # Importamos

from datetime import datetime, timedelta
'''
    Ahora también podemos tener multiples valores utilizando json:
        * key: my_dag_partner
        * val: {
                "name":"partner_a",
                "api_secret":"mysecret",
                "path":"/tmp/partner_a"
               }
    Como puedes ver aquí tenemos tres valores diferentes en una sola variable y por lo tanto 
    vamos a crear una sola conexión para obtener todos esos valores.
'''
def _extract(my_dag_partner):
    print(my_dag_partner)
    '''
    [2023-01-07, 19:46:40 UTC] {logging_mixin.py:137} INFO - {'name': 'partner_a', 'api_secret': 'mysecret', 'path': '/tmp/partner_a'}
    '''
    print(type(my_dag_partner))
    # INFO - <class 'str'>
    
with DAG("my_dag", description="DAG in charge of processing customer data",
         start_date=datetime(2021, 1, 1), schedule_interval='@daily',
         dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
         catchup=False, max_active_runs=1) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=_extract,

        # Creamos un "op_arg" la cual obtendra el nombre del partner y se lo entregará
        # como parámetro a la función _extract.
        op_args = ['{{var.json.my_dag_partner}}']
    )