#!/bin/bash

# Este script crea un log llamado filename en DEST_PATH usando macros, variables
# y templates de Airflow

# DEST_PATH corresponde a la ruta de destino donde se creará el archivo log
# Observe que DEST_PATH se crea utilizando templates, macros y variables con AIRFLOW
# var.value.source_path es una variable procedente del panel de variables de Airflow UI -> variables
# macros.ds_format() es una macro definida por Airflow
# ts_nodash es una variable definida por Airflow
# Las llaves permiten utilizar Jinja Templating para sustituir los marcadores de posición por valores en tiempo de ejecución.

'''Puedes notar que los valores son templados directamente en el archivo. Así que aquí, tenemos una variable 
llamada "source_path" necesaria para especificar la ruta donde se almacenará el archivo log generado. Debemos
crear la variable en Airflow UI: 
    key: source_path
    val: /usr/local/airflow/dags
'''
DEST_PATH={{ var.value.source_path }}/data/{{ macros.ds_format(ts_nodash, "%Y%m%dT%H%M%S", "%Y-%m-%d-%H-%M") }}

'''Al ejecutar el DAG se tendrá una nueva carpeta llamada "data" con un archivo log generado llamado "log.csv".  
Este archivo ha sido generado por el script “generate_new_logs.sh”. Este archivo tendrá 4 columnas "index", 
"message", "timestamp" y "ds_airflow". 
'''
mkdir -p $DEST_PATH # Crea el directorio en la ruta dada por la variable DEST_PATH
echo "index;message;timestamp;ds_airflow" >> $DEST_PATH/{{ params.filename }}
echo "templated_log_dir not templated from params: {{ params.dir_ }}"
for i in {1..5}
do
    RANDOM_STRING=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
    CURRENT_TS=$(date +%s)
    # We template the variable ds in order to have the current executation date of the DAG
    # filename is given from the parameter params of the BashOperator
    echo "$i;$RANDOM_STRING;$CURRENT_TS;{{ ds }}" >> $DEST_PATH/{{ params.filename }}
done