# ==================================== EJEMPLO 1 ====================================
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from datetime import datetime, timedelta

default_arg = {
    'retry':5,
    'retry_delay': timedelta(minutes=5)
}

'''Obtenemos el valor de la key 'city' de nuestro parámetro "op_kwargs" y la 
"execution date" del contexto de nuestro DagRun (DagRun context)'''

# Forma 1
def _downloading_data(city, ds):
    print(city, ds)  # INFO - Santiago 2022-12-21

with DAG(dag_id='simple_dag', default_args = default_arg, schedule_interval='@daily', 
        start_date=days_ago(3), catchup=False) as dag:

    downloading_data = PythonOperator(
        task_id='downloading_data',
        python_callable=_downloading_data,
        # "provide_context" cuando se establece en true, permite a Airflow pasar un conjunto 
        # de argumentos de palabras clave (keyword arguments) que se pueden utilizar en su 
        # función.  Básicamente, es una manera de obtener información acerca de su DAG, su 
        # tarea y así sucesivamente. Tenga en cuenta que este parámetro se establece por defecto 
        # en True, por lo que no necesitará especificarlo más.
        provide_context = 'True',
        op_kwargs = {'my_param': 1000, 
                     'city':'Santiago'
                     }
    )
# ==================================== EJEMPLO 2 ====================================
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from datetime import datetime

default_args = {
    'start_date': datetime(2019, 1, 1),
    'owner': 'Airflow',
    'email': 'owner@test.com'
}

def process(p1):
    print(p1) # my super parameter
    return 'done'

with DAG(dag_id='parallel_dag', schedule_interval='0 0 * * *', 
            default_args=default_args, catchup=False) as dag:
    
        task_1 = PythonOperator(
        task_id='task_1', 
        python_callable=process, 
        op_args=['my super parameter']
        )
# ==================================== EJEMPLO 3 ====================================
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from datetime import datetime, timedelta

default_arg = {
    'retry':5,
    'retry_delay': timedelta(minutes=5)
}

'''Obtenemos el valor de la key 'city' de nuestro parámetro "op_kwargs" y la 
"execution date" del contexto de nuestro DagRun (DagRun context)'''

# Forma 1
def _downloading_data(**context):
    print(context['params']['city']) # INFO - Santiago
    print(context['ds']) # INFO - 2022-12-31

with DAG(dag_id='simple_dag', default_args = default_arg, schedule_interval='@daily', 
        start_date=days_ago(3), catchup=False) as dag:

    downloading_data = PythonOperator(
        task_id='downloading_data',
        python_callable=_downloading_data,
        provide_context = 'True',
        # Llamando 'params' al parametro podemos trabajarlo asi en la función
        params = {'my_param': 1000,   
                  'city':'Santiago'
                     }
    )
# ==================================== EJEMPLO 4 ====================================
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from datetime import datetime, timedelta

default_arg = {
    'retry':5,
    'retry_delay': timedelta(minutes=5)
}

'''Obtenemos el valor de la key 'city' de nuestro parámetro "op_kwargs" y la 
"execution date" del contexto de nuestro DagRun (DagRun context)'''

# Forma 1
def _downloading_data(input_path, output_path):
    print(input_path)   # INFO - /data/events.json
    print(output_path)  # INFO - /data/stats.csv

with DAG(dag_id='simple_dag', default_args = default_arg, schedule_interval='@daily', 
        start_date=days_ago(3), catchup=False) as dag:

    downloading_data = PythonOperator(
        task_id='downloading_data',
        python_callable=_downloading_data,
        # "provide_context" cuando se establece en true, permite a Airflow pasar un conjunto 
        # de argumentos de palabras clave (keyword arguments) que se pueden utilizar en su 
        # función.  Básicamente, es una manera de obtener información acerca de su DAG, su 
        # tarea y así sucesivamente. Tenga en cuenta que este parámetro se establece por defecto 
        # en True, por lo que no necesitará especificarlo más.
        provide_context = 'True',
        op_kwargs={
            "input_path": "/data/events.json", 
            "output_path": "/data/stats.csv"
    },
    )