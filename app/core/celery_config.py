import os
from functools import lru_cache
from kombu import Queue
from pydantic import BaseSettings

def route_task(name, args, kwargs, options, task=None, **kw):
    if ":" in name:
        queue, _ = name.split(":")
        return {"queue": queue}
    return {"queue": "celery"}


class BaseConfig(BaseSettings):
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "rpc://")

    CELERY_TASK_QUEUES: list = (
        # default queue
        Queue("celery"),
        # custom queue
        Queue("olt"),
        Queue("recurrent")
    )

    CELERY_TASK_ROUTES = (route_task,)

    """ CELERY_BEAT_SCHEDULE = {
        'update-port-tx-power': {
            'task': 'task.add',
            'schedule': 30.0,
            'args': (16, 16)
        }
    } """

class DevelopmentConfig(BaseConfig):
    pass

@lru_cache()
def get_settings():
    config_cls_dict = {
        "development": DevelopmentConfig,
    }
    config_name = os.environ.get("CELERY_CONFIG", "development")
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()