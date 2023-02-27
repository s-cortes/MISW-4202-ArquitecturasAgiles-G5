import os
import pika
from random import randint
from threading import Timer

EXCHANGE_NAME = os.environ.get("VOTING_EXCHANGE_NAME")
ROUTING_KEY_NAME = os.environ.get("VOTING_ROUTING_REQUEST_KEY")
NUM_REQUESTS = int(os.environ.get("NUM_REQUESTS"))
REQUEST_INTERVAL = float(os.environ.get("REQUEST_INTERVAL", 1))
VOTING_EXPERIMENT_ID = os.environ.get("VOTING_EXPERIMENT_ID")

print(f"Starting Connection to {EXCHANGE_NAME}/{ROUTING_KEY_NAME}")

connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()

channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct")

output_file = open(f"outputs/{VOTING_EXPERIMENT_ID}_request.csv", "w")
output_file.write("COMPONENT;CORRELATION_ID;PRODUCT_ID;QUANTITY\n")

def publish_product_request(*args, **kwargs):
    corerlation = kwargs.get("count", 0)
    product, quantity = randint(0, 4), randint(0, 100)

    message = f"correlation{corerlation};{product};{quantity}"
    channel.basic_publish(
        exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY_NAME, body=message
    )
    print(f"VOTING_REQ:{message}")
    output_file.write(f"VOTING_REQ;{message}\n")

    if corerlation < NUM_REQUESTS:
        Timer(
            REQUEST_INTERVAL, publish_product_request, kwargs={"count": corerlation + 1}
        ).start()
    else:
        print(f"VOTING ENDED;{VOTING_EXPERIMENT_ID};{NUM_REQUESTS}")
        output_file.close()
        connection.close()

print(f"VOTING STARTED;{VOTING_EXPERIMENT_ID};{NUM_REQUESTS}")
publish_product_request()
