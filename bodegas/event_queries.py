import os
import pika
import hashlib
import json
from random import randint

EXCHANGE_NAME = os.environ.get("STORAGE_PLAN_EXCHANGE_NAME")
REQUEST_KEY_NAME = os.environ.get("STORAGE_PLAN_ROUTING_REQUEST_KEY")

REQUEST_QUEUE_BASE = os.environ.get("STORAGE_PLAN_ROUTING_REQUEST_Q")
REPLICA_ID = os.environ.get("HOSTNAME")  # container identifier
QUEUE_NAME = f"{REQUEST_QUEUE_BASE}-{REPLICA_ID}"

EXPERIMENT_ID = os.environ.get("EXPERIMENT_ID")


print(f"Starting Subscription to {EXCHANGE_NAME}/{REQUEST_KEY_NAME}/{QUEUE_NAME}")

output_file_path = f"outputs/{EXPERIMENT_ID}_{REPLICA_ID}.csv"
connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()

channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct")
result = channel.queue_declare(queue=QUEUE_NAME, exclusive=True)
queue_name = result.method.queue

channel.queue_bind(
    exchange=EXCHANGE_NAME, queue=queue_name, routing_key=REQUEST_KEY_NAME
)

def write_to_output(message):
    print(message)
    with open(output_file_path, "a") as output_file:
        output_file.write(f"{message}\n")


def set_storage_plan(ch, method, properties, body):
    message, checksum = body.decode("utf-8").split(";")
    payload = json.loads(message)
    validation = hashlib.md5(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()
    resp = 200

    if payload.get("rol", None) != 'ruta':
        resp = 403
    elif checksum == validation:
        resp = 400
        

    write_to_output(
        f"BODEGA;{REPLICA_ID};{EXPERIMENT_ID};{resp};{checksum}:{validation};{message}"
    )


write_to_output("COMPONENT;REPLICA_ID;CORRELATION_ID;RESPONSE;CHECKSUM;VALIDATION;MESSAGE")

channel.basic_consume(
    queue=queue_name, on_message_callback=set_storage_plan, auto_ack=True
)
channel.start_consuming()
