from os import environ
from kombu import Queue, Exchange
from osu_api import API_RATE_LIMIT_PER_MINUTE as osu_api_rate_limit


broker_url = environ['BROKER_URL']
backend_url = environ['BACKEND_URL']
beat_schedule = {
    'load_new_mps_every_60_seconds': {
        'task': 'load_new_mps',
        'schedule': 60.0
    },
    'add_osu_api_tokens': {
        'task': 'token',
        'schedule': 60 / osu_api_rate_limit
    }
}

task_default_priority = 5
task_queues = [
    Queue('default', Exchange('default'), routing_key='default', queue_arguments={'x-max-priority': 10}),
    Queue('osu_api', Exchange('osu_api'), routing_key='osu_api', queue_arguments={'x-max-priority': 10}),
    Queue('osu_api_tokens', max_length=2)
]
