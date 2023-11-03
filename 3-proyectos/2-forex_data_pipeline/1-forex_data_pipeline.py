from airflow import DAG

from datetime import datetime, timedelta

# Diccionario donde vas a especificar los atributos comunes de las tareas 
default_args = {
    "owner": "airflow",        # El "owner" de todas las tareas que vas a implementar en ese DAG es Airflow
    "email_on_failure": False, # Para especificar si quieres recibir un correo electrónico en caso de fallo. 
                               # Si una tarea falla. 
    "email_on_retry": False,   # Para especificar si quieres un correo electrónico, cada vez que una tarea es 
                               # reintentada por Airflow.
    "email": "admin@localhost.com", # Indico el correo al cual serán enviadas las alertas
    "retries": 1, # Si escribe 'retry' y pone uno, eso significa que si su tarea falla, esa tarea será 
                  # reintentada por Airflow al menos una vez antes de terminar con el estado “failure”.
    "retry_delay": timedelta(minutes=5) # Aquí se especifica un objeto timedelta con minutos iguales a cinco. 
                                        # Así que estás diciendo, quiero reintentar mi tarea una vez, pero antes 
                                        # de reintentar mi tarea, quiero esperar cinco minutos.
}

with DAG("forex_data_pipeline", start_date=datetime(2021, 1 ,1), 
    schedule_interval="@daily", default_args=default_args, catchup=False) as dag:
    None