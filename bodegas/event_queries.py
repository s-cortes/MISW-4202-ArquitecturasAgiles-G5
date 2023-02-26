import os
import pika
from random import randint

from models import Products

EXCHANGE_NAME = os.environ.get("VOTING_EXCHANGE_NAME")
REQUEST_KEY_NAME = os.environ.get("VOTING_ROUTING_REQUEST_KEY")
RESPONSE_KEY_NAME = os.environ.get("VOTING_ROUTING_RESPONSE_KEY")

REQUEST_QUEUE_BASE = os.environ.get("VOTING_ROUTING_REQUEST_Q")
REPLICA_ID = os.environ.get("HOSTNAME")  # container identifier
QUEUE_NAME = f"{REQUEST_QUEUE_BASE}-{REPLICA_ID}"

WORKER_TYPE = os.environ.get("WORKER_TYPE", "HEALTHY")
HEALTHY_WORKER = WORKER_TYPE == "HEALTHY"
FAILURE_PROBABILITY = int(os.environ.get("FAILURE_PROBABILITY", "75"))
VOTING_EXPERIMENT_ID = os.environ.get("VOTING_EXPERIMENT_ID")

product_list = Products().products

print(f"Starting Subscription to {EXCHANGE_NAME}/{REQUEST_KEY_NAME}/{QUEUE_NAME}")

output_file_path = f"outputs/{VOTING_EXPERIMENT_ID}_{REPLICA_ID}_{WORKER_TYPE}.csv"
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


def working_correctly():
    return HEALTHY_WORKER or randint(0, 100) > FAILURE_PROBABILITY


def query_product_quantity(ch, method, properties, body):
    correlation, pindex, quantity = body.decode("utf-8").split(";")

    in_stock = product_list[int(pindex)]["quantity"] >= int(quantity)
    service_state = working_correctly() 
    in_stock = in_stock if service_state else not in_stock
    result = "Y" if in_stock else "N"

    message = f"{REPLICA_ID};{correlation};{pindex};{quantity};{result}"
    write_to_output(f"BODEGA;{message};{'OK' if service_state else 'WRONG'}")
    
    ch.basic_publish(
        exchange=EXCHANGE_NAME, routing_key=RESPONSE_KEY_NAME, body=message
    )

write_to_output("COMPONENT;REPLICA_ID;CORRELATION_ID;PRODUCT_ID;QUANTITY;RESULT;OUTPUT_TYPE")

channel.basic_consume(
    queue=queue_name, on_message_callback=query_product_quantity, auto_ack=True
)

channel.start_consuming()
