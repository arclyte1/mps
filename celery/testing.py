from kombu import Connection, Exchange, Producer, Queue 
import uuid
import os 
import socket
import json
from tasks import get_users, get_beatmaps, load_mp, load_new_mps


def send_msg_to_celery(args, queue, task, priority=5):
    task_id = str(uuid.uuid4())
    properties = {
        'correlation_id': task_id,
        'content_type': 'application/json', 
        'content_encoding': 'utf-8',
        'priority': priority
    }
    header2 = {
        'task': task,
        'id': task_id,
        'origin': '@'.join([str(os.getpid()), socket.gethostname()])
    }
    rabbit_url = 'amqp://localhost:5672/'
    conn = Connection(rabbit_url) 
    channel = conn.channel()
    exchange = Exchange('', type="direct")
    producer = Producer (exchange=exchange, channel=channel, routing_key=queue)
    queue = Queue(name=queue, exchange=exchange, routing_key=queue, queue_arguments={'x-max-priority': 10}) 
    queue.maybe_bind(conn)
    queue.declare()

    om = list()
    om.append(args)
    om.append({})
    om.append({})
    producer.publish(json.dumps(om), headers=header2, **properties)


if __name__ == '__main__':
    for i in range(10):
        load_mp.apply_async((109143626 + i,), priority=7)
    # for i in range(20):
    #     load_mp.apply_async((i,), priority=7)
    #     # send_msg_to_celery([i], 'osu_api', 'load_mp', priority=5)
        
    # for i in range(5):
    #     get_users.apply_async(kwargs={'user_ids': i}, priority=5)
    #     # send_msg_to_celery([i], 'osu_api', 'get_users', priority=7)
        
    # for i in range(5):
    #     get_beatmaps.apply_async(kwargs={'beatmap_ids': i}, priority=5)
    #     # send_msg_to_celery([i], 'osu_api', 'get_beatmaps', priority=7)
        
    # for i in range(5):
    #     load_new_mps.apply_async(priority=6)
    #     # send_msg_to_celery([], 'osu_api', 'load_new_mps', priority=6)