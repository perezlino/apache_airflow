'''
Consideraremos un pequeño ejemplo. Imaginemos que tenemos un servicio que rastrea el 
comportamiento de los usuarios en nuestro sitio web y nos permite analizar a qué páginas 
accedieron los usuarios (identificados por una dirección IP). Para fines de marketing, nos 
gustaría saber a cuántas páginas diferentes acceden los usuarios y cuánto tiempo pasan 
durante cada visita. Para tener una idea de cómo cambia este comportamiento a lo largo del 
tiempo, queremos calcular estas estadísticas diariamente, ya que esto nos permite comparar 
los cambios en diferentes días y en períodos de tiempo más amplios.

Por razones prácticas, el servicio de seguimiento externo no almacena los datos durante más 
de 30 días, por lo que tenemos que almacenar y acumular estos datos nosotros mismos, ya que 
queremos conservar nuestro historial durante períodos de tiempo más largos. Normalmente, 
dado que los datos en bruto pueden ser bastante grandes, tendría sentido almacenar estos 
datos en un servicio de almacenamiento en la nube, como S3 de Amazon o Cloud Storage de Google, 
ya que combinan una alta durabilidad con costes relativamente bajos. Sin embargo, para simplificar, 
no nos preocuparemos por estas cosas y guardaremos nuestros datos localmente.

Para simular este ejemplo, hemos creado una sencilla API (local) que nos permite recuperar los 
eventos del usuario. Por ejemplo, podemos recuperar la lista completa de eventos disponibles de 
los últimos 30 días utilizando la siguiente llamada al API:

curl -o /tmp/events.json http://localhost:5000/events

Esta llamada devuelve una lista (codificada en JSON) de eventos de usuarios que podemos analizar 
para calcular nuestras estadísticas de usuarios.

'''
from datetime import datetime
from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

'''
NOTA: Preste atención al hecho de que Airflow inicia las tareas de un intervalo al final 
del mismo. Si se desarrolla un DAG el 1 de enero de 2019 a las 13:00 horas, con una 
"start_date" de 01-01-2019 y un intervalo @daily, esto significa que primero comienza a 
ejecutarse a medianoche. Al principio, no pasará nada si se ejecuta el DAG el 1 de enero 
a las 13:00, si no, esperará hasta que se alcance la medianoche.
'''
dag = DAG(
    dag_id="01_unscheduled", 
    start_date=datetime(2019, 1, 1), 
    end_date=datetime(2019, 1, 5),
    # schedule_interval=None --> Sin programación
    schedule_interval="@daily" # Programación diaria a medianoche
    # schedule_interval=datetime.timedelta(days=3) --> se ejecutara cada tres días después de la start_date 
    #                                                  (los días 4, 7, 10, etc. de enero de 2019)
)

# Se crea el directorio "/data/events" y se descargan los datos de la API en el archivo "events.json"
fetch_events = BashOperator(
    task_id="fetch_events",
    bash_command=(
        "mkdir -p /data/events && "

        # Estamos recuperando todos los eventos de los últimos 30 dias
        "curl -o /data/events.json http://localhost:5000/events"
    ),
    dag=dag,
)

def _calculate_stats(input_path, output_path):
    """Calculates event statistics."""

    # Crear el directorio "/data/" si no existe 
    Path(output_path).parent.mkdir(exist_ok=True)

    events = pd.read_json(input_path)
    '''
    print(events)

                               date            user
    0     2018-12-06 00:00:00+00:00   53.152.21.233
    1     2018-12-06 00:00:00+00:00    59.17.167.79
    2     2018-12-06 00:00:00+00:00   53.152.21.233
    3     2018-12-06 00:00:00+00:00  142.97.103.133
    4     2018-12-06 00:00:00+00:00   9.129.175.199
    ...                         ...             ...
    40597 2019-01-04 00:00:00+00:00    8.180.86.150
    40598 2019-01-04 00:00:00+00:00    97.251.44.93
    40599 2019-01-04 00:00:00+00:00    98.249.72.36
    40600 2019-01-04 00:00:00+00:00  15.159.120.196
    40601 2019-01-04 00:00:00+00:00  15.159.120.196

    [40602 rows x 2 columns]
    '''
    
    stats = events.groupby(["date", "user"]).size().reset_index()
    '''
    print(events)

                              date             user   0
    0    2018-12-06 00:00:00+00:00   102.214.136.11  14
    1    2018-12-06 00:00:00+00:00   111.118.61.234  10
    2    2018-12-06 00:00:00+00:00     113.61.175.1   4
    3    2018-12-06 00:00:00+00:00  122.200.185.202   8
    4    2018-12-06 00:00:00+00:00  123.184.108.180  10
    ...                        ...              ...  ..
    2131 2019-01-04 00:00:00+00:00    73.129.42.201  16
    2132 2019-01-04 00:00:00+00:00     8.180.86.150  22
    2133 2019-01-04 00:00:00+00:00   81.131.240.108  21
    2134 2019-01-04 00:00:00+00:00     97.251.44.93  18
    2135 2019-01-04 00:00:00+00:00     98.249.72.36  24

    [2136 rows x 3 columns]
    '''

    stats.to_csv(output_path, index=False)


calculate_stats = PythonOperator(
    task_id="calculate_stats",
    python_callable=_calculate_stats,
    op_kwargs={
        "input_path": "/data/events.json", 
        "output_path": "/data/stats.csv"
    },
    dag=dag,
)

fetch_events >> calculate_stats