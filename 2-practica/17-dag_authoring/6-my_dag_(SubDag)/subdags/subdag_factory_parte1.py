from airflow.models import DAG
from airflow.decorators import task

@task.python
def process_a(partner_name, partner_path):
    print(partner_name)
    print(partner_path)

@task.python
def process_b(partner_name, partner_path):
    print(partner_name)
    print(partner_path)

@task.python
def process_c(partner_name, partner_path):
    print(partner_name)
    print(partner_path)

def subdag_factory(parent_dag_id, subdag_dag_id, default_args, partner_settings):

    with DAG(f'{parent_dag_id}.{subdag_dag_id}', default_args=default_args) as dag:

        process_a(partner_settings['partner_name'], partner_settings['partner_path'])
        process_b(partner_settings['partner_name'], partner_settings['partner_path'])
        process_c(partner_settings['partner_name'], partner_settings['partner_path'])
    
    return dag