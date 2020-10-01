from dagster_celery_k8s.executor import celery_k8s_job_executor

from dagster import ModeDefinition, default_executors, pipeline


@pipeline(mode_defs=[ModeDefinition(executor_defs=default_executors + [celery_k8s_job_executor])])
def celery_enabled_pipeline():
    pass
