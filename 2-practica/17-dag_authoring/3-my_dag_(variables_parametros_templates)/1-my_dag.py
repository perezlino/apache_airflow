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
def _extract():
    # Modifiquemos el nombre de la variable, llamémosla "partner_settings" y aquí lo único que 
    # tienes que añadir es "deserialize_json=True" y entonces vas a obtener el valor JSON como 
    # un diccionario y así podrás acceder a los diferentes valores. 
    partner_settings = Variable.get("my_dag_partner", deserialize_json=True) 
    print(partner_settings) # INFO - {'name': 'partner_a', 'api_secret': 'mysecret', 'path': '/tmp/partner_a'}

with DAG("my_dag", description="DAG in charge of processing customer data",
         start_date=datetime(2021, 1, 1), schedule_interval='@daily',
         dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
         catchup=False, max_active_runs=1) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=_extract
    )