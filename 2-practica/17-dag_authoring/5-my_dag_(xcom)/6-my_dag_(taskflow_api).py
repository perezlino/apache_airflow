from airflow import DAG
from airflow.operators.python import PythonOperator

from airflow.decorators import task, dag

from datetime import datetime, timedelta

@task.python
def extract():
    partner_name="netflix"
    partner_path='/partners/netflix'

    # Digamos, en lugar del valor JSON, sólo queremos devolver "partner_name":
    return partner_name

# Ahora, ¿cómo podemos recuperarlo desde "process"? ¿Cómo puedes sacar ese XCom desde "process"? 
# ¿Vamos a usar xcom_pull? No, no lo vamos a hacer, ya no. Lo único que tenemos que hacer es 
# especificar el nombre del XCom, así que, por ejemplo, aquí podemos escribir "partner_name", 
# pero podemos llamarlo como queramos, y entonces vamos a imprimir "partner_name":
@task.python
def process(partner_name):
    print(partner_name)

@dag(description="DAG in charge of processing customer data",
         start_date=datetime(2021, 1, 1), schedule_interval='@daily',
         dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
         catchup=False, max_active_runs=1)

def my_dag():

    '''Ahora es el momento de hablar de XCom args, el segundo componente de la Taskflow API, 
    y esto es realmente hermoso, porque ahora ya no usaremos estas dependencias: '''
    #extract() >> process()

    '''Y ahora te preguntarás, bueno, esto es genial, tengo "partner_name" pero ¿cómo puedo 
    extraer (pull) ese XCom? Pues bien, sólo tienes que llamar a "process" y como argumento de 
    "process", le pasas "extract()". Y al hacer esto, no sólo se puede extraer (pull) el XCom 
    automáticamente, que es empujado (pushed) por "extract", sino que también las dependencias 
    entre esas dos tareas, se generan automáticamente. '''
    process(extract())

my_dag()