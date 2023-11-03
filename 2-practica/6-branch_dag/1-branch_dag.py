# utilizando el DAG "xcom_dag" lo que haremos será trabajar con un Branch Operator 
# para utilizar una tarea u otra según una condición. Y el primer paso es importar 
# el BranchPythonOperator, ya que, es el operator que vamos a utilizar. Te permite 
# ejecutar una función python y en esa función python te devuelve el task ID de la 
# siguiente tarea que quieres ejecutar en base a tu condición.

from airflow import DAG
from airflow.operators.python import PythonOperator,BranchPythonOperator # Importamos el operador
from airflow.operators.bash import BashOperator

from datetime import datetime

# Existen dos maneras de compartir un valor: Utilizando un "return" con el valor
# que se quiere compartir y la otra es utilizando "xcom_push"
def _t1(ti):
    ti.xcom_push(key='my_key', value=100)

# Si se utiliza "xcom_push" para compartir, debemos utilizar "xcom_pull" para
# tomar el valor compartido
def _t2(ti):
    ti.xcom_pull(key='my_key', task_ids='t1')

# Creamos la función "_branch" y retornará un Task ID en base a una condición especifica
def _branch(ti):
    value = ti.xcom_pull(key='my_key', task_ids='t1')
    if (value == 100):
        return 't2'
    return 't3'

with DAG('xcom_dag', start_date=datetime(2022,1,1), 
            schedule_interval='@daily', catchup=False) as dag:
    
    t1 = PythonOperator(
        task_id = 't1',
        python_callable = _t1
    )

    # Creamos una nueva tarea utilizando el operador BranchPythonOperator
    branch = BranchPythonOperator(
        task_id='branch',
        python_callable = _branch
    )

    t2 = PythonOperator(
        task_id = 't2',
        python_callable = _t2
    )

    t3 = BashOperator(
        task_id = 't3',
        bash_command ="echo ''"
    )

    # Modificamos las dependencias
    t1 >> branch >> [t2, t3]