import airflow.utils.dates
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

default_args = {
    "start_date": airflow.utils.dates.days_ago(1), 
    "owner": "Airflow"
}

'''Este DAG no tiene nada especial, tiene tres tareas, donde la primera tarea se basa en el 
PythonOperator para imprimir el mensaje enviado desde el DAG controlador. Aquí, en la función 
"remote_value", accedemos al "contexto de dag_run" y obtenemos el valor de "message". Hacemos 
lo mismo con los templates en la tarea t2 donde esta vez utilizamos el objeto predefinido 
"dag_run" y comprobamos si existe. Si es así, se devuelve el valor de "message". Por último, 
la tarea t3 ejecuta el comando sleep durante 30 segundos para mostrar que el DAG controlador 
terminará antes de que termine el DAGRun target. '''


def remote_value(**context):
    print("Value {} for key=message received from the controller DAG".format(context["dag_run"].conf["message"]))

with DAG(dag_id="triggerdagop_target_dag", default_args=default_args, 
            schedule_interval=None) as dag:

    t1 = PythonOperator(
            task_id="t1",
            provide_context=True,
            python_callable=remote_value, 
        )

    t2 = BashOperator(
        task_id="t2",
        bash_command='echo Message: {{ dag_run.conf["message"] if dag_run else "" }}')

    t3 = BashOperator(
        task_id="t3",
        bash_command="sleep 30"
    )