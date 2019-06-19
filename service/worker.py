import pickle
import pika
import time

import config
from task import Task


def main():
    connection_parameters = Task.get_connection_parameters()
    with pika.BlockingConnection(connection_parameters) as connection:
        channel = connection.channel()
        channel.queue_declare(queue='incoming_tasks', durable=True)
        channel.basic_consume('incoming_tasks', process_task)
        channel.start_consuming()


def process_task(channel, method, properties, body):
    payload = pickle.loads(body)
    task = Task(**payload)
    task.process_task()
    channel.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    main()
