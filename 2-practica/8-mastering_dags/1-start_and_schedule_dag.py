from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator

from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2019, 3, 29, 1),
    'owner': 'Airflow'
}

with DAG(dag_id='start_and_schedule_dag', schedule_interval="0 * * * *", default_args=default_args) as dag:
    
    # Task 1
    dummy_task_1 = DummyOperator(task_id='dummy_task_1')
    
    # Task 2
    dummy_task_2 = DummyOperator(task_id='dummy_task_2')
    
    dummy_task_1 >> dummy_task_2

'''
¿Qué ocurre en Airflow?

La start date es el 29 de marzo de 2019 a las 01:00 horas y el schedule interval es de 1 hora. 

Entonces, ¿qué ocurre? 

Todavía nada. De hecho, Airflow espera 1 hora y no es hasta las 02:00 horas cuando se crea 
y se ejecuta el DAG Run. En cuanto el DAG Run se completa, el 29 de marzo de 2019 a las 02:00 
horas se convierte en la "Execution date". La "Execution date" es el inicio de este periodo, 
del scheduled period. Y entonces las 02:00 a.m. se convierte en la "Start date".

¿Qué es lo que sigue?

Pues bien, de nuevo, Airflow espera 1 hora y, a continuación, a las 03:00 horas, se crea y 
se ejecuta el DAG Run, el segundo DAG Run, el DAG Run 2. En cuanto se completa el DAG Run 2, 
la "Execution date" para ese DAG Run específico, el DAG Run 2, pasa a ser el 29 de marzo de 2019 a las 02:00 
las 02:00 horas. Y la nueva Start date es las 03:00 a.m.

Así es como funciona. Recuerda que cada DAG Run tiene una execution date y esta execution date 
corresponde al inicio del scheduled period para ese DAG Run específico.

Entonces:

start_date = 29/03/2019 01:00:00 UTC
schedule_interval = cada 1 hora
1° DAG effectively run = 29/03/2019 02:00:00 UTC

execution_date = 29/03/2019 01:00:00 UTC
start_date = 29/03/2019 02:00:00 UTC
schedule_interval = cada 1 hora
2° DAG effectively run = 29/03/2019 03:00:00 UTC

execution_date = 29/03/2019 02:00:00 UTC
start_date = 29/03/2019 03:00:00 UTC
schedule_interval = cada 1 hora
3° DAG effectively run = 29/03/2019 04:00:00 UTC

Y así sucesivamente ...

'''