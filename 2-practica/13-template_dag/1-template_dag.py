'''
=============================
Variables, Templates y Macros
=============================

Variables
=========
Una variable no es más que un objeto, un valor almacenado en la metadata database 
de airflow. Hay dos formas de crear variables, desde la interfaz de usuario o desde 
la interfaz de línea de comandos.  En nuestro caso, nos quedaremos con la primera 
opción.  Básicamente, una variable se compone de una key y un valor. La key existe 
para poder recuperar la variable de tu DAG especificando esa key. 

Templates
=========
Templating permiten interpolar valores en tiempo de ejecución (at runtime) en archivos 
estáticos como HTML o SQL, colocando en ellos marcadores de posición especiales que 
indican dónde deben estar los valores y cómo deben mostrarse. Piense en templating 
como una forma de rellenar los espacios en blanco de su código con valores externos. 
Templating en Airflow se basa en Jinja que es un motor de templates para Python 
encargado de reemplazar los marcadores de posición con los valores esperados y más.
En Airflow, para indicar un marcador de posición utilizamos 4 llaves {{ }}. Esas llaves 
indican a Jinja que hay algo que interpolar ahí. Una cosa que hay que tener en cuenta 
es que en Airflow no se puede templar todo. Sólo algunos parámetros se pueden utilizar 
con templates.

Macros
======
Las macros son funciones predefinidas por Airflow. En realidad, Airflow le ofrece tanto 
macros predefinidas como variables que puede utilizar dentro de sus templates. Son muy 
útiles ya que le permiten obtener información sobre el DAG o la tarea que se está ejecutando 
en ese momento, por ejemplo. 

---------------------------------------------------------------------------------------------------
Variables y Macros predefinidas
---------------------------------------------------------------------------------------------------
Variables                        | Descripción
---------------------------------------------------------------------------------------------------
{{ ds }}                         |  La execution date del DAG en ejecución como YYYY-MM-DD
---------------------------------------------------------------------------------------------------
{{ prev_ds }}                    | La execution date anterior del DAG en ejecución como YYYY-MM-DD
---------------------------------------------------------------------------------------------------
{{ next_ds }}                    | La próxima execution date del DAG en ejecución como YYYY-MM-DD
---------------------------------------------------------------------------------------------------
{{ dag }}                        | El objeto dag actual
---------------------------------------------------------------------------------------------------
{{ params }}                     | Datos accesibles desde sus operadores
---------------------------------------------------------------------------------------------------
{{ var.value.key_of_your_var}}   | Acceso a las variables almacenadas en la metadatabase
---------------------------------------------------------------------------------------------------

'''
# =========================================== EJEMPLO 1 ===========================================
# Creamos un nuevo directorio y archivo log utilizando variables, macros y un archivo bash templado

import sys
import airflow
from airflow import DAG, macros
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from datetime import datetime, timedelta

# Sería más prolijo añadir la ruta a la variable PYTHONPATH
'''La ruta sys insertada aquí, es sólo una forma rápida de poder importar las funciones python del 
módulo process_logs en la carpeta "scripts".  '''
sys.path.insert(1, '/usr/local/airflow/dags/scripts')

default_args = {
            "owner": "Airflow",
            "start_date": airflow.utils.dates.days_ago(1),
            "depends_on_past": False,
            "email_on_failure": False,
            "email_on_retry": False,
            "email": "youremail@host.com",
            "retries": 1
        }

with DAG(dag_id="template_dag", schedule_interval="@daily", default_args=default_args) as dag:

    t0 = BashOperator(
            task_id="t0",
            # Comando muy simple para mostrar desde el output la execution date del DAG. 
            # bash_command="echo {{ ds }}"

            # Se creo en Airflow UI la siguiente variable: key: CASSANDRA_LOGIN
            #                                              val: my_login                             
            # Podemos recuperar el valor de esta variable.
            # bash_command="echo {{ var.value.CASSANDRA_LOGIN }}"

            # Llamar a una macro en un parámetro templado para modificar un valor dinámicamente.
            # Al escribir "macros." se obtiene un acceso a las macros predefinidas de Airflow. 
            # La macro "ds_format" toma un string de entrada que es otra variable predefinida llamada 
            # "ts_nodash" que corresponde a la execution date del DAG en formato iso, luego, macro 
            # "ds_format" emite (outputs) otro string como se especifica en el formato de salida. Así, 
            # en nuestro caso, la execution date dada sin guiones con el formato definido aquí, se 
            # transformará para que coincida con el formato de salida con guiones.  
            bash_command="echo {{ macros.ds_format(ts_nodash, '%Y%m%dT%H%M%S', '%Y-%m-%d-%H-%M') }}")
        
    '''¿Sabías que tus archivos también pueden ser templados? De hecho, si echamos un vistazo a la 
    documentación de Airflow sobre el BashOperator, puedes ver justo debajo de los parámetros templados, 
    la sección 'template_ext' con dos valores ".sh" y ".bash". Esto significa que, si llamas a un archivo 
    script desde el parámetro de comando bash, también puedes incluir marcadores de posición de template 
    en ese archivo script.'''    
    t1 = BashOperator(
            task_id="generate_new_logs",
            bash_command="./scripts/generate_new_logs.sh",

            # Si abrimos el archivo “generate_new_logs.sh” en la carpeta script, encontraremos el marcador 
            # de posición “params.filename”, que será reemplazado por el valor "log .csv" en tiempo de 
            # ejecución (at runtime). 
            params={'filename': 'log.csv'})

#     t0 >> t1

# =========================================== EJEMPLO 2 ===========================================
# Creamos un nuevo directorio y archivo log utilizando variables, templates y macros

import sys
import airflow
from airflow import DAG, macros
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from datetime import datetime, timedelta

# Sería más prolijo añadir la ruta a la variable PYTHONPATH
'''La ruta sys insertada aquí, es sólo una forma rápida de poder importar las funciones python del 
módulo process_logs en la carpeta "scripts".  '''
sys.path.insert(1, '/usr/local/airflow/dags/scripts')

from process_logs import process_logs_func

TEMPLATED_LOG_DIR = """{{ var.value.source_path }}/data/
                       {{ macros.ds_format(ts_nodash, "%Y%m%dT%H%M%S", "%Y-%m-%d-%H-%M") }}/"""

default_args = {
            "owner": "Airflow",
            "start_date": airflow.utils.dates.days_ago(1),
            "depends_on_past": False,
            "email_on_failure": False,
            "email_on_retry": False,
            "email": "youremail@host.com",
            "retries": 1
        }

with DAG(dag_id="template_dag", schedule_interval="@daily", default_args=default_args) as dag:
    
    # Permite crear el directorio 'data/.... y el archivo log 'log.csv' dentro de ella
    t1 = BashOperator(
            task_id="generate_new_logs",
            bash_command="./scripts/generate_new_logs.sh",
            params={'filename': 'log.csv'})

    # Sólo comprueba si el archivo log ha sido generado dentro del directorio recien creado
    t2 = BashOperator(
           task_id="logs_exist",
           bash_command="test -f " + TEMPLATED_LOG_DIR + "log.csv",
           )
    
    '''PythonOperator proporciona dos parámetros importantes: "provide_context" y "templates_dict". 
    "provide_context" cuando se establece en “True”, permite a Airflow pasar un conjunto de argumentos 
    de palabras clave (keyword arguments) que se pueden utilizar en su función.  Básicamente, es una 
    manera de obtener información acerca de su DAG, su tarea y así sucesivamente, exactamente como lo 
    hacemos con los templates utilizando las variables predefinidas "ds", "ti" y así sucesivamente.  
    Tenga en cuenta que este parámetro se establece por defecto en True, por lo que no necesitará 
    especificarlo más.  El parámetro "templates_dict" es un diccionario donde los valores serán templados 
    por el motor Jinja y estarán disponibles en el contexto proporcionado. Digamos que queremos pasar la 
    ruta TEMPLATED_LOG_DIR que es la ruta del archivo log generado. Para ello, primero tenemos que 
    establecer en “True” el parámetro "provide_context" y luego crear el par clave-valor con la key 
    "log_dir" y el valor correspondiente a la ruta templada.'''

    t3 = PythonOperator(
           task_id="process_logs",
           python_callable=process_logs_func,
           provide_context=True,
           templates_dict={'log_dir':TEMPLATED_LOG_DIR},
           # El parámetro "params" no acepta valor templado.  Así que no intentes poner un placeholder 
           # (marcador de posición) con llaves, no funcionará.
           params={'filename': 'log.csv'}
           )
    
    '''Al ejecutar el DAG se tendrá una nueva carpeta llamada "data/..." con un archivo log generado llamado "log.csv".
    Este archivo ha sido generado por el script “generate_new_logs.sh”. Este archivo tendrá 4 columnas "index", 
    "message", "timestamp" y "ds_airflow". Luego la tarea 't3' utilizando pandas realizará modificaciones al archivo 
    logs.csv como renombrar las columnas y formatear el timestamp. Luego se creará un nuevo archivo "processed_log.csv" 
    dentro del directorio recién creado'''

    t1 >> t2 >> t3