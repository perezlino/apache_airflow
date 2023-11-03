from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator 
from airflow.providers.postgres.operators.postgres import PostgresOperator # Importamos

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
def _extract(partner_name):
    print(partner_name)   # INFO - partner_a
    
with DAG("my_dag", description="DAG in charge of processing customer data",
         start_date=datetime(2021, 1, 1), schedule_interval='@daily',
         dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
         catchup=False, max_active_runs=1) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=_extract,

        # Hay una mejor manera de obtener el valor de la variable json y es utilizando
        # templates.
        op_args = ['{{var.json.my_dag_partner.name}}']
    )

    fetching_data = PostgresOperator(
        task_id="fetching_data",

        # Como una mejor práctica no deberiamos poner nuestra sentencia SQL directamente en el 
        # PostgresOperator, en su lugar deberiamos tener un archivo SQL y poner nuestro SQL request 
        # en él, para que mantengas separado tu DAG de nuestras sentencias SQL, y eso hará tu DAG 
        # mucho más limpio.
        sql="sql/my_request.sql"
    )