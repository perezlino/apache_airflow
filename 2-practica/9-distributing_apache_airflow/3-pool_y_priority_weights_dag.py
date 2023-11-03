'''
========================
Pools y priority_weights
========================

Un pool es una gran manera de limitar el número de instancias concurrentes de un 
tipo específico de tarea para evitar saturar el origen o el destino. Por ejemplo, 
digamos que tienes tres nodos worker, donde en total se pueden ejecutar tres tareas 
en paralelo.  

Explicación desarrollo de nuestro DAG
=====================================
Ahora, en tu DAG, tienes tres tareas para extraer datos de una API REST en paralelo, 
pero esta API sólo puede solicitarse una vez cada vez. La pregunta es, ¿cómo puede 
limitar el número de solicitudes a 1 sin tener que modificar los parámetros de su 
instancia de Airflow?  Pues bien, ahí es donde los pools vienen a salvarnos. Utilizando 
pools, podemos limitar el número de tareas que solicitan la API definiendo un número de 
"slots", que en nuestro caso es 1, y asignar las tres tareas a este pool. Al hacerlo, 
las tres tareas se ejecutarán secuencialmente una tras otra. 

Así pues, tenemos tres tareas que son tres "SimpleHttpOperators" que solicitarán una 
forex API para obtener las 'rates' de una divisa determinada (rates of a given 
currency). La tarea "get_forex_rate_EUR" obtiene los tipos del EUR, luego 
"get_forex_rate_USD" obtiene los tipos del USD, y tenemos la misma tarea para el JPY. 
El resultado de cada petición (request) se almacenará utilizando XComs. Eso es lo que 
se puede ver por el parámetro 'xcom_push'. Al final del DAG, tenemos una tarea llamada 
"show_data" que obtendrá las 'rates' almacenadas en la metadata database de Airflow y 
las mostrará en la salida. En el comando bash se está haciendo un bucle a través de las 
diferentes tareas del DAG para obtener los datos que almacenan. Por último, para poner 
en marcha el DAG, tenemos que crear una conexión llamada "forex_api" como se define aquí.  

Se debe crear una conexión en Airflow UI:

- conn_id: forex_api
- conn type: HTTP
- host: api.exchangeratesapi.io

Luego se debe crear un pool en Airflow UI:

- pool: forex_api_pool
- slots: 1
- description: pool para limitar el número de requests a la API

Entonces tenemos el nuevo pool "forex_api_pool".  El "default_pool" es el pool por defecto 
usado por tus tareas limitando el número de tareas concurrentes a 128. Esto significa que, 
si estableces el número de slots de ese pool a 1, podrás ejecutar 1 tarea a la vez. Ok ahora 
tenemos nuestro pool definido, tenemos que mover a las tareas dentro de él. Para cada tarea 
"get_rate", añade el parámetro "pool='forex_api_pool'".

Así que los pools son útiles para limitar el número de tareas concurrentes en un ámbito 
concreto que tú definas.

priority_weights
================
Me gustaría mostrar cómo se puede dar prioridad a las tareas en nuestro pool. En realidad, 
hay un parámetro que puede añadir a cualquier operador que es "priority_weight". Este 
parámetro nos permite definir el orden en la queue y que tareas se ejecutan primero como 
slots abiertos en el pool. Por defecto, este "priority_weight" está establecido en 1. Lo que 
podemos hacer, es cambiar este valor a cualquier número para establecer el orden en el que 
las tareas van a ser ejecutadas dentro del pool. Para la tarea "get_forex_rate_EUR" definimos 
el "priority_weight" a 1. Luego, para la tarea "get_forex_rate_USD" establecemos el parámetro 
a 2. Y finalmente, para la tarea "get_forex_rate_JPY", establecemos el parámetro al valor 3.  
De este modo, obtendremos primero los tipos de cambio del JPY (rates of JPY), después los del 
USD y finalmente los del EUR. 

'''
from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.bash_operator import BashOperator

from datetime import datetime

default_args = {
    'start_date': datetime(2019, 1, 1),
    'owner': 'Airflow',
    'email': 'owner@test.com'
}

with DAG(dag_id='pool_dag', schedule_interval='0 0 * * *', 
            default_args=default_args, catchup=False) as dag:
    
    # obtiene los forex rates de EUR y los empuja a XCOM
    get_forex_rate_EUR = SimpleHttpOperator(
        task_id='get_forex_rate_EUR',
        method='GET',
        priority_weight=1,
        pool='forex_api_pool',
        http_conn_id='forex_api',
        endpoint='/latest?base=EUR',
        xcom_push=True
    )
 
    # obtiene los forex rates de USD y los empuja a XCOM
    get_forex_rate_USD = SimpleHttpOperator(
        task_id='get_forex_rate_USD',
        method='GET',
        priority_weight=2,
        pool='forex_api_pool',
        http_conn_id='forex_api',
        endpoint='/latest?base=USD',
        xcom_push=True
    )
 
    # obtiene los forex rates de JPY y los empuja a XCOM
    get_forex_rate_JPY = SimpleHttpOperator(
        task_id='get_forex_rate_JPY',
        method='GET',
        priority_weight=3,
        pool='forex_api_pool',
        http_conn_id='forex_api',
        endpoint='/latest?base=JPY',
        xcom_push=True
    )
 
    # Templated command with macros
    bash_command="""
        {% for task in dag.task_ids %}
            echo "{{ task }}"
            echo "{{ ti.xcom_pull(task) }}"
        {% endfor %}
    """

    # Show rates
    show_data = BashOperator(
        task_id='show_result',
        bash_command=bash_command
    )

    [get_forex_rate_EUR, get_forex_rate_USD, get_forex_rate_JPY] >> show_data