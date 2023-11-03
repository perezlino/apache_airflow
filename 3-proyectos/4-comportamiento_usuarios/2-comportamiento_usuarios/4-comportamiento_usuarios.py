import datetime as dt
from datetime import timedelta
from pathlib import Path

import pandas as pd

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id="07_templated_query_ds",
    schedule_interval=timedelta(days=3),
    start_date=dt.datetime(year=2019, month=1, day=1),
    end_date=dt.datetime(year=2019, month=1, day=5),
)

fetch_events = BashOperator(
    task_id="fetch_events",
    bash_command=(
        "mkdir -p /data/events && "

        # Aunque nuestra nueva tarea fetch_events ahora obtiene eventos de forma incremental 
        # para cada nuevo schedule interval, notamos que para cada nueva tarea simplemente 
        # se sobrescribe el resultado del día anterior, lo que significa que efectivamente 
        # no estamos construyendo ningún historial. Un enfoque es dividir nuestro data set 
        # en lotes diarios (daily batches) escribiendo la salida de la tarea en un archivo 
        # que lleve el nombre de la execution date correspondiente.

        "curl -o /data/events/{{ds}}.json "
        "http://events_api:5000/events?"
        "start_date={{ds}}&"
        "end_date={{next_ds}}"
    ),
    dag=dag,
)

def _calculate_stats(input_path, output_path):
    """Calculates event statistics."""

    events = pd.read_json(input_path)
    stats = events.groupby(["date", "user"]).size().reset_index()

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)


calculate_stats = PythonOperator(
    task_id="calculate_stats",
    python_callable=_calculate_stats,
    op_kwargs={
        "input_path": "/data/events.json", 
        "output_path": "/data/stats.csv"},
    dag=dag,
)

fetch_events >> calculate_stats