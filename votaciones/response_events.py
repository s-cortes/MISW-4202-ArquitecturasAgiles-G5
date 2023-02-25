import os
import pika


EXCHANGE_NAME = os.environ.get("VOTING_EXCHANGE_NAME")
RESPONSE_QUEUE_NAME = os.environ.get("VOTING_ROUTING_RESPONSE_Q")
RESPONSE_KEY_NAME = os.environ.get("VOTING_ROUTING_RESPONSE_KEY")

connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()

channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct")


result = channel.queue_declare(queue=RESPONSE_QUEUE_NAME, exclusive=False)
queue_name = result.method.queue

channel.queue_bind(
    exchange=EXCHANGE_NAME, queue=queue_name, routing_key=RESPONSE_KEY_NAME
)


def query_product_quantity(ch, method, properties, body):
    message = body.decode("utf-8")
    print(f"{method.routing_key} Received: {message}")


channel.basic_consume(
    queue=queue_name, on_message_callback=query_product_quantity, auto_ack=True
)
channel.start_consuming()
