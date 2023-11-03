'''
=========
Branching
=========

Branching es la forma de ir por un camino determinado en su DAG basado en una 
condición arbitraria que normalmente está relacionada con algo que sucedió en una 
tarea upstream. Esto se hace utilizando el BranchPythonOperator que devuelve el 
"task_id" de la tarea a ejecutar a continuación.  

depends_on_past y Branching
===========================
Supongamos que todas las tareas "tarea_a", "tarea_b" y "tarea_c" tienen el parámetro 
'depends_on_past' establecido en True.  Ahora, en el primer DAGRun, la tarea branch 
devuelve el id de tarea "task_c".  Por lo tanto, sólo se ejecuta la tarea_c, mientras 
que las tareas "task_b" y "task_a" se omiten. A continuación, en el segundo DAGRun, 
esta vez la tarea branch devuelve "task_b".  Pues bien, según la documentación, como 
esta tarea no se activó en el DAGRun anterior y tiene depends_on_past establecido en 
true, el scheduler no la ejecutará. De nuevo, basándome en mis experimentos, esto no 
es cierto.  La tarea task_b se activará como debería.  Por último, tenga cuidado 
cuando desee omitir una tarea.  

Explicación desarrollo de nuestro DAG
=====================================
Digamos que estás trabajando en una empresa y necesitas localizar direcciones ip 
usando una API de geolocalización IP. Como sabrás, la mayoría de las API tienen 
umbrales de petición por encima de los cuales ya no se pueden hacer peticiones. 
Una forma de utilizar "branching" en Airflow sería crear una tarea con una lista 
de APIs en la que se comprueba cada API para saber si aún puede realizar peticiones. 
Dependiendo del resultado, se ejecutará la siguiente tarea correspondiente a la API 
disponible. A continuación, el resultado se almacenará en una base de datos.  

'''
# ======================================= EJEMPLO 1 =======================================
import airflow
import requests
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator

default_args = {
    'owner': 'Airflow',
    'start_date': airflow.utils.dates.days_ago(2),
}

IP_GEOLOCATION_APIS = {
    'ip-api': 'http://ip-api.com/json/',
    'ipstack': 'https://api.ipstack.com/',
    'ipinfo': 'https://ipinfo.io/json'
}

'''Este DAG se encarga de solicitar diferentes APIs para geolocalizar direcciones ip.  
Aquí se realiza una comprobación desde la función "check_api", donde se realiza una 
petición para cada API y si la petición devuelve datos JSON (JSON data) y que tengan 
el campo "country", entonces se devuelve la API. Este valor devuelto es procesado a 
continuación por el BranchPythonOperator para ejecutar la tarea correspondiente.  
Por ejemplo, si el valor devuelto es "ipstack", se ejecutará la tarea "ipstack" y se 
omitirán las demás tareas.  Si no hay ninguna API disponible, la función check_api 
devuelve "none" y, por tanto, sólo se ejecutará la tarea "none".'''
def check_api():
    for api, link in IP_GEOLOCATION_APIS.items():
        r = requests.get(link)
        try:
            data = r.json()
            if data and 'country' in data and len(data['country']):
                return api
        except ValueError:
            pass
    # Este 'none' siempre es lanzado. En caso de que no haya ninguna API, 'none' será 
    # lanzado y el BranchPythonOperator lo tomará. En caso de que exista una API
    # disponible, tomará el valor devuelto por 'api', dado que es el primer valor
    # devuelto.
    return 'none' 

with DAG(dag_id='branch_dag', 
    default_args=default_args, 
    schedule_interval="@once") as dag:

    '''Cuatro tareas son downstream de la tarea check_api: 'ip-api', 'none', 'ipstack'
    y 'ipinfo', donde cada tarea tiene el nombre de su correspondiente API, así como la 
    tarea 'none'. La última tarea del DAG es "save" y debe ejecutarse siempre.'''
    check_api = BranchPythonOperator(
        task_id='check_api',
        python_callable=check_api
    )

    none = DummyOperator(
        task_id='none'
    )

    '''La última tarea "save" se ha saltado también lo cual no es algo que queramos. Esto 
    está relacionado con el tema sobre las trigger rules. Por defecto, una tarea se dispara 
    sólo si sus padres han tenido éxito. Aquí, debido a que algunas tareas son omitidas, no 
    son consideradas como exitosas y por lo tanto, la "trigger rule" por defecto para la tarea 
    "save" no es respetada. Por eso la tarea no se ejecuta. ¿Cómo podemos solucionarlo? Es por
    eso, que debemos añadir el parámetro "trigger_rule=one_success".'''
    save = DummyOperator(
        task_id='save',
        trigger_rule='one_success'
    )

    check_api >> none >> save

    # Crea tareas dinámicamente según las APIs
    for api in IP_GEOLOCATION_APIS:
        process = DummyOperator(
            task_id=api
        )
    
        check_api >> process >> save

# ======================================= EJEMPLO 2 =======================================

'''Lo último que me gustaría mostrar es que podemos devolver múltiples task ids para elegir 
varios branches a la vez. Hagamos algunas modificaciones en el DAG que utilizamos. Desde la 
función 'check_api', en lugar de devolver la primera API disponible, vamos a devolver una 
lista con todas las APIs a las que podemos acceder. Para ello, creamos una variable de lista 
vacía llamada "apis". Luego cambiamos la instrucción "return api" por "apis.append (api)".  
Así, cada vez que la API esté disponible, se añadirá a la lista de APIs. Finalmente, si la 
lista contiene al menos una api, la devolvemos, de lo contrario, devolvemos el task_id "none".'''

import airflow
import requests
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator

default_args = {
    'owner': 'Airflow',
    'start_date': airflow.utils.dates.days_ago(2),
}

IP_GEOLOCATION_APIS = {
    'ip-api': 'http://ip-api.com/json/',
    'ipstack': 'https://api.ipstack.com/',
    'ipinfo': 'https://ipinfo.io/json'
}

def check_api():
    apis = [] # Lista vacia
    for api, link in IP_GEOLOCATION_APIS.items():
        r = requests.get(link)
        try:
            data = r.json()
            if data and 'country' in data and len(data['country']):
                apis.append(api) # Agregamos las apis disponibles a la lista
        except ValueError:
            pass
    return apis if len(apis) > 0 else 'none'

with DAG(dag_id='branch_dag', 
    default_args=default_args, 
    schedule_interval="@once") as dag:

    check_api = BranchPythonOperator(
        task_id='check_api',
        python_callable=check_api
    )

    none = DummyOperator(
        task_id='none'
    )

    save = DummyOperator(
        task_id='save',
        trigger_rule='one_success'
    )

    check_api >> none >> save

    # Crea tareas dinámicamente según las APIs
    for api in IP_GEOLOCATION_APIS:
        process = DummyOperator(
            task_id=api
        )
    
        check_api >> process >> save
