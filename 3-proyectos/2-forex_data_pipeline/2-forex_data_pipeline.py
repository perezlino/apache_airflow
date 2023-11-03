# Nuestro objetivo ahora es añadir la tarea para comprobar si la URL, la API está disponible o no, 
# si los valores de las divisas (forex rates) están disponibles en ella. Para ello, hay un operador 
# que se puede utilizar, que es el 'HttpSensor'. El HttpSensor permite verificar cada 60 segundos 
# si la URL está disponible o no, y en caso de que lo esté, si el contenido devuelto por esa URL es 
# el esperado o no.

from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor

from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "admin@localhost.com",
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

with DAG("forex_data_pipeline", start_date=datetime(2021, 1 ,1), 
    schedule_interval="@daily", default_args=default_args, catchup=False) as dag:

    is_forex_rates_available = HttpSensor(
        task_id="is_forex_rates_available",
        http_conn_id="forex_api",
        # Básicamente el 'endpoint' es cualquier cosa que tengas después del host
        endpoint="marclamberti/f45f872dea4dfd3eaa015a4a1af4b39b", 
        # La función lambda devolverá un 'True', por tanto, response_check = True.
        # response.text retorna codigo HTML de tipo string, por tanto, se comprueba que la 
        # palabra 'rates' se encuentra en dicha cadena.
        response_check=lambda response: "rates" in response.text, 
        # El argumento 'poke_interval' define la frecuencia con la que tu sensor va a comprobar si 
        # la condición es verdadera o falsa. En ese caso, cada cinco segundos va a verificar si la URL, 
        # si el 'forex_api' está disponible o no.
        poke_interval=5,
        # El último argumento es el 'timeout' es igual a 20. Como se puede adivinar, significa que después 
        # de 20 segundos que el sensor se está ejecutando, recibirá un timeout. Y por lo tanto la tarea 
        # terminará en failure. ¿Por qué es importante especificar el timeout? es porque usted no quiere 
        # mantener su sensor en funcionamiento para siempre. Así que es por eso que con un sensor y esto es 
        # una mejor práctica, siempre especificar un timeout. De lo contrario, el sensor seguirá funcionando 
        # durante siete días por defecto.
        timeout=20
    )