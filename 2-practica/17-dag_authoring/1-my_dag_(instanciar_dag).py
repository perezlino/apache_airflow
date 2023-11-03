'''
dagrun_timeout
==============
Este argumento indica que si su DAG tarda más de, por ejemplo, 10 minutos en completarse, 
entonces falla. De forma predeterminada, no hay un tiempo de espera (timeout) predeterminado 
para su DAG. ¿Y por qué es un problema? Porque si su DAG tarda más de 10 minutos en completarse 
y su "schedule_interval" está establecido en 10 minutos, su primer DAG seguirá ejecutándose y 
se activará el siguiente DAGRun, por lo que terminará con dos DAG ejecutándose incluso si el 
primero todavía no ha terminado, y es posible que no queramos eso. Porque si nuestro DAG tarda más 
de 10 minutos y nosotros esperamos que nuestro DAG se complete en 10 minutos, eso significa que 
hay un problema con nuestro DAG, por lo que debemos solucionar dicho problema. Por lo tanto, 
siempre debemos especificar un 'dagrun_timeout' que corresponda aproximadamente a la herramienta 
de programación (schedule tool) que tiene, por ejemplo, si tiene un 'schedule_interval' establecido 
en 10 minutos, podría ser interesante establecer un 'dagrun_timeout' en 12 minutos. Entonces, 
especificamos timedelta(minutes = 10). Obviamente, necesitamos importar el objeto timedelta. Así 
que siempre haga eso, tenga en cuenta que Airflow no omitirá el próximo DAGRun, sino que activará el 
próximo DAGRun incluso si la actual aún se está ejecutando. 

tags
====
Este argumento es bastante básico, pero bastante útil. Por ejemplo, digamos que tiene diferentes 
equipos trabajando en su DAG, por ejemplo, el equipo de DataScience o el equipo de DataEngineer, 
puede especificar etiquetas para este DAG y luego usará esas etiquetas para filtrar sus DAG en la 
interfaz de usuario. Entonces, por ejemplo, digamos que pertenecen al equipo "data_science" y además 
se pueden agregar muchas etiquetas a nuestro DAG.

Diferencia entre "Cron" y "timedelta"
=====================================

start_date = 1 de Enero de 2023 a las 10:00 am
schedule_interval = @daily             ---> Se ejecuta el 2 de Enero de 2023 a las 00:00 am
schedule_interval = 0 0 * * * (Cron)   ---> Se ejecuta el 2 de Enero de 2023 a las 00:00 am
schedule_interval = timedelta(days=1)  ---> Se ejecuta el 2 de Enero de 2023 a las 10:00 am

max_active_runs
===============
Si queremos evitar tener una tonelada de DAG Runs corriendo al mismo tiempo, podemos usar un argumento 
dentro del dag definition object que es 'max_active_runs' y por ejemplo configurarlo en 1. Así que en 
ese caso, significa que no tendrás más de un DAG Run corriendo a la vez para ese DAG, desde my_dag.

catchup
=======
- Una cosa que es absolutamente necesario recordar es que incluso si el parametro 'catchup' se establece 
en 'False' todavía se puede utilizar el proceso de backfilling. Básicamente, desde el Airflow CLI con el 
comando "airflow dags backfill" .

- Otro punto importante es que incluso si el parámetro "catchup" se establece en "False", tenga en cuenta 
que siempre se ejecuta el DAG Run más reciente no disparado. Si por ejemplo, nos dirigimos a Airflow UI,
activamos el toggle de un DAG y actualizamos la página, es probable que haya un DAG Run ejecutándose 
correspondiente al último, al más reciente DAG Run no disparado. Así que incluso con el 'catchup' establecido 
en 'False' podriamos tener un DAG Run tan pronto como empecemos a programar (scheduling) nuestro data pipeline.

'''
from airflow import DAG

from datetime import datetime, timedelta

with DAG("my_dag", description="DAG in charge of processing customer data",
         start_date=datetime(2021, 1, 1), schedule_interval='@daily',
         dagrun_timeout=timedelta(minutes=10), tags=['data_science','customers'],
         catchup=False, max_active_runs=1) as dag:

         None