import datetime as dt
from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id="05_query_with_dates",
    schedule_interval="@daily",
    start_date=dt.datetime(year=2019, month=1, day=1),
    end_date=dt.datetime(year=2019, month=1, day=5),
)

fetch_events = BashOperator(
    task_id="fetch_events",
    bash_command=(
        "mkdir -p /data/events && "
        "curl -o /data/events.json "

        # Queremos recuperar solo los eventos entre las fechas '2019-01-01' y '2019-01-02'. 
        # Tenga en cuenta que en este ejemplo start_date es inclusivo, mientras que end_date es 
        # exclusivo, lo que significa que estamos recuperando eventos que ocurren entre 
        # 2019-01-01 00:00:00 y 2019-01-01 23:59:59.

        # curl -O http://localhost:5000/events?start_date=2019-01-01&end_date=2019-01-02

        "http://events_api:5000/events?"
        "start_date=2019-01-01&"
        "end_date=2019-01-02"
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