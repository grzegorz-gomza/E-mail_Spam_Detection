from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import ShortCircuitOperator
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

# ------------------------
# Default arguments for your DAG
# ------------------------
default_args = {
    'owner': 'greg',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# ------------------------
# Callable for ShortCircuitOperator
# ------------------------
def condition_check(ti):
    """Check XCom from drift detection task and return True/False."""
    condition_result = ti.xcom_pull(task_ids='condition_check_drift', key='return_value')
    if isinstance(condition_result, str):
        return condition_result.lower() == 'true'
    return bool(condition_result)

# ------------------------
# DAG definition
# ------------------------
with DAG(
    'spam_classifier_monthly_model_retraining',
    default_args=default_args,
    description='Checks for data drift monthly and conditionally retrains a model.',
    schedule_interval='0 0 7 * *',  # At 00:00 on day-of-month 7.
    catchup=False,
) as dag:

    drift_check_task = DockerOperator(
        task_id='condition_check_drift',
        image='drift_detection_env:1.0',
        command="python /opt/airflow/scripts/project_spam_classifier/drift_detection.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        do_xcom_push=True,
        mount_tmp_dir=False,
        mounts=[
            Mount(
                source='/absolute/path/to/deploy_model/docker_airflow/scripts',  # <-- update as needed
                target='/opt/airflow/scripts', 
                type='bind'
            )
        ]
    )

    retraining_decision = ShortCircuitOperator(
        task_id='retraining_decision',
        python_callable=condition_check,
        provide_context=True,
    )

    model_retrain_task = DockerOperator(
        task_id='model_retrain_task',
        image='drift_detection_env:1.0',
        api_version='auto',
        auto_remove=True,
        command="python /opt/airflow/scripts/project_spam_classifier/model_retrain.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        mount_tmp_dir=False,
        mounts=[
            Mount(
                source='/absolute/path/to/deploy_model/storage',  # <-- update as needed
                target='/opt/airflow/storage', 
                type='bind'
            ),
            Mount(
                source='/absolute/path/to/deploy_model/docker_airflow/scripts',  # <-- update as needed
                target='/opt/airflow/scripts', 
                type='bind'
            )
        ]
    )

    drift_check_task >> retraining_decision >> model_retrain_task
