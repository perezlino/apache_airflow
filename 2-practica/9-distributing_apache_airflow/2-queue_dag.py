'''
Enviando tareas a un worker específico con queues
=================================================
Antes de comenzar, para utilizar workers debemos estar trabajando con el Celery
Executor. Para la creación de workers y la configuración tecnica de como enviar
tareas a un worker especifico revisar mis apuntes de Airflow.

El último paso que hay que hacer es establecer el atributo "queue" de la tarea que se 
quiere enviar. Todos los Operadores tienen un atributo llamado "queue".  Por defecto 
está establecido en "default". Si vas a tu editor de código, abre el archivo airflow.cfg 
y busca el parámetro llamado "default_queue".  Puedes ver que la queue por defecto 
donde las tareas se asignan y los workers escuchan es "default". Para realizar más 
detalle acerca de estas modificaciones técnicas revisar mis apuntes de Airflow.

Con respecto a este DAG, podemos decir que es bastante simple. Ejecuta 7 tareas donde 6 
de ellas se pueden ejecutar en paralelo. La tarea 7 depende de todas ellas. Además, cada 
tarea tiene un sufijo, _io, _cpu, _spark para indicar la queue a la que se debe enviar 
una tarea determinada. Debemos mencionar que dentro de las configuraciones tecnicas, se 
crearon 3 workers: "worker_ssd", "worker_cpu" y "worker_spark". Para revisar con más 
detalle como se realizó esto, revisar mis apuntes de Airflow.

Entonces, ¿cómo podemos enviar cada tarea a la queue adecuada para que la ejecute el worker 
correcto? Pues bien, sólo tenemos que añadir el argumento "queue" al operador de tarea. 
Por ejemplo, para la tarea t_1_ssd, escribimos 'queue="worker_ssd"'. 

Para finalizar, tenemos que definir qué cola debe consumir cada worker. Para ello se debe
realizar ciertas configuraciones técnicas, las cuales puedo revisar en mis apuntes de 
Airflow.

'''


from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator

from datetime import datetime

default_args = {
    'start_date': datetime(2019, 1, 1),
    'owner': 'Airflow',
    'email': 'owner@test.com'
}

with DAG(dag_id='queue_dag', schedule_interval='0 0 * * *', 
            default_args=default_args, catchup=False) as dag:
    
    t_1_ssd = BashOperator(
        task_id='t_1_ssd', 
        bash_command='echo "I/O intensive task"',
        queue = 'worker_ssd'
    )

    t_2_ssd = BashOperator(
        task_id='t_2_ssd', 
        bash_command='echo "I/O intensive task"',
        queue = 'worker_ssd'
    )

    t_3_ssd = BashOperator(
        task_id='t_3_ssd', 
        bash_command='echo "I/O intensive task"',
        queue = 'worker_ssd'
    )

    t_4_cpu = BashOperator(
        task_id='t_4_cpu', 
        bash_command='echo "CPU instensive task"',
        queue = 'worker_cpu'
    )

    t_5_cpu = BashOperator(
        task_id='t_5_cpu', 
        bash_command='echo "CPU instensive task"',
        queue = 'worker_cpu'
    )

    t_6_spark = BashOperator(
        task_id='t_6_spark', 
        bash_command='echo "Spark dependency task"',
        queue = 'worker_spark')

    task_7 = DummyOperator(
        task_id='task_7'
    )

    [t_1_ssd, t_2_ssd, t_3_ssd, t_4_cpu, t_5_cpu, t_6_spark] >> task_7