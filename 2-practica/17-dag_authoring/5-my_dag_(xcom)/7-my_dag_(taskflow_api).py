from airflow import DAG
from airflow.operators.python import PythonOperator

from airflow.decorators import task, dag

from datetime import datetime, timedelta

'''Si recuerdas volvemos a esta tarea "extract", donde queremos compartir múltiples 
valores con la tarea "process". Y así, con el fin de empujar (push) múltiples valores 
al mismo tiempo, se creó este diccionario con los valores "partner_name" y "partner_path".

Pero ahora, al devolver este diccionario, va a crear un XCom para todos sus valores. Pero 
qué pasa si quieres tener un XCom para un valor, un XCom para "partner_name" y un XCom 
para "partner_path", sin usar "xcom_push" dos veces. Pues bien, aquí es donde tienes que 
utilizar la Taskflow API. Una cosa que debes saber es que puedes pasar algunos argumentos 
a tus decoradores, por ejemplo, imaginemos que en lugar de tener el "task ID" por defecto 
correspondiente al nombre de tu función, quieres tener otro "task ID". En ese caso, puedes 
pasar el siguiente argumento a tu decorador "task_ID=extract_partners". 
 
'''
@task.python(task_ID='extract_partners',do_xcom_push=False, multiple_outputs=True)
# Con "task_ID" como argumento cambiemos el nombre de la tarea que anteriormente tomaba el 
# nombre de la función.

# Al especificar el parámetro "multiple_outputs" a "True", estás diciendo que este XCom no 
# debería ser un XCom con su diccionario como valor, sino que debería tener "dos XComs", un 
# XCom con la key "partner_name" y el valor "partner_name" y otro XCom con la key "partner_path" 
# con el valor "partner_path".

# Al especificar el parámetro "do_xcom_push" (que está activado por defecto a "True") a False, 
# no permitiremos que se cree un XCom con la "key: return_value" y el valor: {"partner_name":"netflix",
# "partner_path":"/partners/netflix"}

def extract(): 
    partner_name="netflix"
    partner_path='/partners/netflix'
    return {
            "partner_name":partner_name, 
            "partner_path":partner_path
           }

# Ahora la pregunta es, ¿cómo obtenemos esos XComs en la tarea "process"? Bueno, esto es super fácil, 
# sólo tenemos que añadir otro argumento, así que vamos a llamarlo "partner_path". Entonces, 
# buscamos imprimir "partner_path" también. 
@task.python
def process(partner_name, partner_path):
    print(partner_name)
    print(partner_path)

@dag(description="DAG in charge of processing customer data",
         start_date=datetime(2021, 1, 1), schedule_interval='@daily',
         dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
         catchup=False, max_active_runs=1)

def my_dag():

    # Y en lugar de pasar directamente "extract" como argumento de "process", se crea una nueva variable, 
    # y la llamamos "partner_settings" igual a "extract()", y entonces decimos, quiero extraer (pull) el 
    # XCom con la key "partner_name" y luego quiero extraer (pull) el XCom con la key "partner_path". Y 
    # al hacer esto, somos capaces de extraer (pull) las XComs especificando la key como se muestra allí:
    partner_settings = extract()
    process(partner_settings['partner_name'], partner_settings['partner_path'])

my_dag()