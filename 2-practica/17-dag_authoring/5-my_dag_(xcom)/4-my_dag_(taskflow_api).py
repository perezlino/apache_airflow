'''
Taskflow API
============

Crear DAGs una y otra vez puede llevar mucho tiempo y en algún momento ser realmente aburrido 
y como ingeniero no nos gusta repetir y escribir el mismo código una y otra vez. Por eso se ha 
introducido la "Taskflow API" desde Airflow 2.0. Con la Taskflow API puedes crear data pipelines 
de una manera mucho más fácil y rápida. Veamos en qué consiste exactamente. En primer lugar, se 
puede dividir la Taskflow API en dos partes diferentes, donde la primera parte son los "decorators" 
y la segunda parte son los “XCom args". ¿Cuál es el objetivo de los decorators? Bueno, el objetivo 
de los decorators es ayudarle a crear DAGs de una manera más fácil y rápida que la forma clásica de 
crear sus DAGs. Por ejemplo, digamos que quieres crear una tarea con el operador Python, en lugar de 
instanciar el operador Python, y luego llamar a tu función Python, puedes usar el decorator 
"@task.python". Y mediante el uso de ese decorador en la parte superior de nuestra función de Python, 
que deseamos ejecutar, automáticamente Airflow creará el PythonOperator por nosotros y vamos a llamar 
a esa función. De igual manera existe "@task.virtualenv", con el fin de ejecutar su función de Python 
dentro de un entorno virtual. Y por último, pero no menos importante, tenemos "@task_group", que nos 
permite agrupar múltiples tareas. Así que tenemos esos decoradores y obviamente vendrán nuevos 
decoradores, pero con esos decoradores somos capaces de crear hermosos DAGs de una manera mucho más 
rápida.

El otro componente de la Taskflow API es el "XCom args". Básicamente, cada vez que una tarea comparte 
datos con otra tarea, esas dos tareas crean una dependencia, porque, por ejemplo, tienes la tarea A, 
B y C, y C necesita datos procedentes de la tarea A. Tenemos una dependencia entre esas dos tareas, pero, 
estas dependencias están implícitas en la interfaz de usuario, es decir, no seremos capaz de ver que 
la tarea C necesita los datos procedentes de la tarea A, sólo veremos las dependencias tarea A, luego tarea 
B, luego tarea C. Así que con la Taskflow API, automáticamente Airflow hará esta dependencia entre la tarea 
C y la tarea A explícita. Creará la dependencia por nosotros. Estos son los dos componentes de la Taskflow 
API. El primero son los "decoradores" que nos permiten crear DAGs de una manera mucho más rápida y el 
segundo son los "XCom args" que nos permiten compartir datos entre nuestras tareas sin tener que llamar a 
"XCom push" y "XCom pull" y también nos ayuda a explicitar las dependencias implícitas creadas por los XComs. 

'''
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task

from datetime import datetime, timedelta

# Empecemos con los "decoradores", en tu data pipeline, tienes dos tareas "extract" y "process". Ambas 
# utilizan el operador Python, así que vamos a ver cómo se puede aprovechar la Taskflow API, para no tener 
# que instanciar el operador Python, con el fin de ejecutar una función de Python. Así que, primero haz la 
# importación de los decoradores, así que necesitas escribir "from airflow.decorators import task" y luego 
# el segundo paso es simplemente añadir el decorador correspondiente, así que añade @task.python, ya que 
# quieres usar el operador Python para llamar a esa función "_extract": 

# Entonces puedes quitar el "_" de la función "_extract". Así, esta función Python que ahora se llama 
# "extract" se convierte en el nombre de tu tarea "extract". 

@task.python
def extract():
    partner_name="netflix"
    partner_path='/partners/netflix'
    return {
            "partner_name":partner_name, 
            "partner_path":partner_path
           }

# Hacemos lo mismo con la función "_process":

@task.python
def process():
    print("process")

    
with DAG("my_dag", description="DAG in charge of processing customer data",
         start_date=datetime(2021, 1, 1), schedule_interval='@daily',
         dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
         catchup=False, max_active_runs=1) as dag:

    extract() >> process()