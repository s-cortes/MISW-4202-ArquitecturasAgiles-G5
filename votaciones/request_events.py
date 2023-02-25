import os
import pika
from random import randint
from threading import Timer

EXCHANGE_NAME = os.environ.get("VOTING_EXCHANGE_NAME")
ROUTING_KEY_NAME = os.environ.get("VOTING_ROUTING_REQUEST_KEY")
NUM_REQUESTS = int(os.environ.get("NUM_REQUESTS"))

connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()

channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct")

def publish_product_request(*args, **kwargs):
    corerlation = kwargs.get("count", 0)
    product, quantity = randint(0,4), randint(0, 100)

    message = f"{corerlation}:{product}:{quantity}"
    channel.basic_publish(exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY_NAME, body=message)
    print(f"VOTING_REQ:{message}")

    if corerlation < NUM_REQUESTS:
        Timer(1, publish_product_request, kwargs={"count":corerlation+1}).start()
    else:
        print("VOTING ENDED")
        connection.close()

publish_product_request()