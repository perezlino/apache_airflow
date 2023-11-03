from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.models.baseoperator import cross_downstream, chain

from datetime import datetime

default_args = {
    'start_date':datetime(2020,1,1)
}

with DAG('dependency', schedule_interval='@daily',
            default_args=default_args, catchup=False) as dag:

    t1 = DummyOperator(task_id='t1')
    t2 = DummyOperator(task_id='t2')
    t3 = DummyOperator(task_id='t3')
    t4 = DummyOperator(task_id='t4')
    t5 = DummyOperator(task_id='t5')
    t6 = DummyOperator(task_id='t6')
    t7 = DummyOperator(task_id='t7')

    t1.set_downstream(t2)
    t2.set_upstream(t1)

    t1 >> t2
    t2 << t1

    # Ahora imaginemos que queremos decir que [t1, t2, t3] son las tareas upstream 
    # de "t4". ¿Puedes hacerlo? Claro que sí.
    [t1, t2, t3] >> t4

    # ¿Y si quieres decir que [t4, t5, t6] son ahora las tareas downstream de las 
    # tareas upstream [t1, t2, t3]. ¿Funciona? Pues no, porque Airflow no sabe exactamente 
    # lo que quieres, es decir, si quieres que "t4" dependa de "t1, t2 y t3" o si quieres 
    # que "t4" dependa de "t1". Es decir, no lo sabe, así que no eres capaz de crear 
    # dependencias entre listas como esa.
    [t1, t2, t3] >> [t4, t5, t6] # =============>> ERRONEO

    # ¿Qué más puedes hacer? Bueno, si vuelves a tu editor de código, ¿qué pasa si quieres 
    # crear dependencias cruzadas? Por ejemplo, quieres decir que "t4" depende de "t1, t2 y t3", 
    # "t5" depende de "t1, t2 y t3" y "t6" depende de "t1, t2 y t3". Una forma es escribiendo:
    [t1, t2, t3] >> t4
    [t1, t2, t3] >> t5
    [t1, t2, t3] >> t6

    # Para crear dependencias cruzadas entre dos listas de tareas, una forma es utilizando una 
    # función súper útil llamada "cross_downstream". 
    cross_downstream([t1, t2, t3], [t4, t5, t6])

    cross_downstream([t1, t2, t3], [t4, t5, t6]) >> t7 # ERRONEO

    # ¿Cómo puedes crear dependencias en cadena (chain dependencies)? Imaginemos que quieres tener 
    # "t1" primero y luego quieres ejecutar "t2" y "t3" en la misma línea, así que quieres tener 
    # "t2" depende de "t1", y "t3" depende de "t1" y luego quieres tener "t5" depende de "t3", y 
    # "t4" depende de "t2". ¿Cómo se puede representar esto con "chain"? ¿cómo puedes crear dependencias 
    # en cadena (chain dependencies)? Imaginemos que quieres tener "t1" primero y luego quieres ejecutar 
    # "t2" y "t3" en la misma línea, así que quieres tener "t2" depende de "t1", y "t3" depende de "t1" 
    # y luego quieres tener "t5" depende de "t3", y "t4" depende de "t2". ¿Cómo se puede representar 
    # esto con "chain"? 

    # Tienes que asegurarte de que la otra lista junto a la primera lista tiene el mismo tamaño de la 
    # primera lista. Si la primera lista tiene un tamaño diferente de la segunda lista, no funcionará. 
    # Entonces puedes decir "t6" como la última tarea.
    chain(t1, [t2, t3], [t4, t5], t6)

