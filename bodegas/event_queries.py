import os
import pika


EXCHANGE_NAME = os.environ.get("VOTING_EXCHANGE_NAME")
REQUEST_KEY_NAME = os.environ.get("VOTING_ROUTING_REQUEST_KEY")
RESPONSE_KEY_NAME = os.environ.get("VOTING_ROUTING_RESPONSE_KEY")

REQUEST_QUEUE_BASE = os.environ.get("VOTING_ROUTING_REQUEST_Q")
REPLICA_ID = os.environ.get("HOSTNAME") # container identifier
QUEUE_NAME = f"{REQUEST_QUEUE_BASE}-{REPLICA_ID}"

print(f"Starting Subscription to {EXCHANGE_NAME}/{REQUEST_KEY_NAME}/{QUEUE_NAME}")

connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()

channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct")


result = channel.queue_declare(queue=QUEUE_NAME, exclusive=True)
queue_name = result.method.queue

channel.queue_bind(
    exchange=EXCHANGE_NAME, queue=queue_name, routing_key=REQUEST_KEY_NAME
)


def query_product_quentity(ch, method, properties, body):
    product, quantity = body.decode("utf-8").split(":")
    print(f"{method.routing_key} check P{product} Q{quantity}")
    ch.basic_publish(
        exchange=EXCHANGE_NAME, routing_key=RESPONSE_KEY_NAME, body=f"Response {product}:{quantity}"
    )


channel.basic_consume(
    queue=queue_name, on_message_callback=query_product_quentity, auto_ack=True
)

channel.start_consuming()
