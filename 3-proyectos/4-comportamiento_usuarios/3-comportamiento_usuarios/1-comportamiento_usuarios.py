import datetime as dt
from pathlib import Path

import pandas as pd

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id="08_templated_path",
    schedule_interval="@daily",
    start_date=dt.datetime(year=2019, month=1, day=1),
    end_date=dt.datetime(year=2019, month=1, day=5),
)

fetch_events = BashOperator(
    task_id="fetch_events",
    bash_command=(
        "mkdir -p /data/events && "
        "curl -o /data/events/{{ds}}.json "
        "http://events_api:5000/events?"
        "start_date={{ds}}&"
        "end_date={{next_ds}}"
    ),
    dag=dag,
)

'''Esta práctica de dividir un data set en trozos más pequeños y manejables es una 
estrategia común en los sistemas de almacenamiento y procesamiento de datos y se conoce 
comúnmente como "partición", siendo los trozos más pequeños de un data set las particiones. 
La ventaja de dividir nuestro data set por "execution date" se hace evidente cuando 
consideramos la segunda tarea de nuestro DAG (calculate_stats), en la que calculamos las 
estadísticas de los eventos de usuario de cada día. En nuestra implementación anterior, 
cargábamos todo el data set y calculábamos las estadísticas de todo nuestro historial de 
eventos, cada día. Sin embargo, utilizando nuestro data set con particiones, podemos 
calcular estas estadísticas más eficientemente para cada partición separada cambiando las 
rutas de entrada y salida (input_path y outpath_path) de esta tarea para que apunte a los 
datos de eventos con particiones y a un archivo de salida (output file) con particiones.
'''

def _calculate_stats(**context):
    """Calculates event statistics."""
    input_path = context["templates_dict"]["input_path"]     # Modificamos 
    output_path = context["templates_dict"]["output_path"]   # Modificamos

    events = pd.read_json(input_path)
    stats = events.groupby(["date", "user"]).size().reset_index()

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)


calculate_stats = PythonOperator(
    task_id="calculate_stats",
    python_callable=_calculate_stats,
    templates_dict={
        "input_path": "/data/events/{{ds}}.json",  # Modificamos
        "output_path": "/data/stats/{{ds}}.csv",   # Modificamos
    },
    # Requerido en Airflow 1.10 para acceder a "templates_dict", obsoleto (deprecated) en Airflow 2+.
    # "provide_context=True"
    dag=dag,
)


fetch_events >> calculate_stats