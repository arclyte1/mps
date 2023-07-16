from kombu import Connection, Exchange, Producer, Queue 
import uuid
import os 
import socket
import json

def send_msg_to_celery(args, queue, task):
    task_id = str(uuid.uuid4())
    properties = {
        'correlation_id': task_id,
        'content_type': 'application/json', 
        'content_encoding': 'utf-8',
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
    queue = Queue(name=queue, exchange=exchange, routing_key=queue) 
    queue.maybe_bind(conn)
    queue.declare()

    om = list()
    om.append(args)
    om.append({})
    om.append({})
    producer.publish(json.dumps(om), headers=header2, **properties)


if __name__ == '__main__':
    send_msg_to_celery([10], 'default', 'load_mp')