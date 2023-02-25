import os
import pika
from random import randint

EXCHANGE_NAME = os.environ.get("VOTING_EXCHANGE_NAME")
ROUTING_KEY_NAME = os.environ.get("VOTING_ROUTING_REQUEST_KEY")

connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()

channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct")

product, quantity = randint(0,4), randint(0, 100)
channel.basic_publish(exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY_NAME, body=f"{product}:{quantity}")

connection.close()
