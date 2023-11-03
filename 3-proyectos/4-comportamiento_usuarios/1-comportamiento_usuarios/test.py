from pathlib import Path
import pandas as pd

def _calculate_stats():
    """Calculates event statistics."""

    events = pd.read_json('/github/apache_airflow/20-comportamiento_usuarios/pruebas/events.json')
    # print(events)
    stats = events.groupby(["date", "user"]).size().reset_index()
    print(stats)
    # stats.to_csv('/github/apache_airflow/stats.csv', index=False)

_calculate_stats()