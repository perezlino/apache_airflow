'''
Tratar en lo posible de obtener nuestras variables dentro de tareas o mediante el uso 
del templates engine.

Si obtenemos nuestras variables (Variable.get) fuera, cada vez que nuestro DAG sea
analizado (cada 30 segundos), se creará una conexión inútil para obtener la variable, 
incluso si no la usamos en ese momento, incluso si nuestro DAG no se está ejecutando 
todavía. Y esto es un gran problema porque si tenemos muchos DAGs y manejamos muchas 
variables, vamos a crear una tonelada de conexiones inútiles a la meta database y tu 
base de datos podría terminar con algunos problemas.
'''
from airflow import DAG
from airflow.models import Variable  # Importamos
from airflow.operators.python import PythonOperator # Importamos

from datetime import datetime, timedelta

'''Luego de crear en Airflow UI la variable: 
        * key: my_dag_partner
        * val: partner_a 

   Luego si queremos "ocultar el valor" de una key, debemos adjuntar al nombre "_secret"
        * key: my_dag_partner_secret
        * val: partner_a 
    De esta forma al llamarla de una tarea no se visualizará y solo aparecerán ****

'''
def _extract():
    partner = Variable.get("my_dag_partner_secret") # Vamos a obtener el valor de la variable
    print(partner)

with DAG("my_dag", description="DAG in charge of processing customer data",
         start_date=datetime(2021, 1, 1), schedule_interval='@daily',
         dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
         catchup=False, max_active_runs=1) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=_extract
    )