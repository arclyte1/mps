from os import environ
from kombu import Queue

broker_url = environ['BROKER_URL']
backend_url = environ['BACKEND_URL']
# worker_heartbeat = 120
# task_concurrency = 4
# worker_prefetch_multiplier = 1
task_queues = [
    Queue('default'),
    Queue('osu_api'),
    Queue('osu_api_tokens', max_length=2)
]
