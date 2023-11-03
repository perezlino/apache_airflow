import pandas as pd
from datetime import datetime

# Observa que el nombre del parámetro no es importante
# Podría llamarse "kwargs" también. Yo lo llamé "contexto" 
# para mostrar que esta variable existe ya que usamos el parámetro
# provide_context=True del PythonOperator
def process_logs_func(**contexto):
    log_dir = contexto['templates_dict']['log_dir']
    filename = contexto['params']['filename']

    print("Log dir: {}".format(log_dir))
    print("Filename: {}".format(filename))
    logs = pd.read_csv(log_dir + "/" + filename, sep=";")
    logs.drop("index", axis=1, inplace=True)
    logs['timestamp'] = logs['timestamp'].apply(lambda x: datetime.fromtimestamp(x))
    logs.rename(
            columns={
                'timestamp': 'processing_time',
                'ds_airflow': 'etl_execution_time'
                },
            inplace=True
            )
    logs.to_csv(log_dir + "/processed_log.csv", sep=";", index=False)