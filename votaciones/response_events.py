import os
import pika
import redis


EXCHANGE_NAME = os.environ.get("VOTING_EXCHANGE_NAME")
RESPONSE_QUEUE_NAME = os.environ.get("VOTING_ROUTING_RESPONSE_Q")
RESPONSE_KEY_NAME = os.environ.get("VOTING_ROUTING_RESPONSE_KEY")
NUM_REPLICAS = int(os.environ.get("NUM_REPLICAS", "3"))
VOTING_EXPERIMENT_ID = os.environ.get("VOTING_EXPERIMENT_ID")

print(f"Starting Subscription to {EXCHANGE_NAME}/{RESPONSE_KEY_NAME}/{RESPONSE_QUEUE_NAME}")

output_file_path = f"outputs/{VOTING_EXPERIMENT_ID}.csv"

r = redis.Redis(host='redis', port=6379, db=0)

connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()

channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct")

result = channel.queue_declare(queue=RESPONSE_QUEUE_NAME, exclusive=False)
queue_name = result.method.queue

channel.queue_bind(
    exchange=EXCHANGE_NAME, queue=queue_name, routing_key=RESPONSE_KEY_NAME
)

def write_to_output(message):
    print(message)
    with open(output_file_path, "a") as output_file:
        output_file.write(f"{message}\n")

write_to_output("COMPONENT;CORRELATION_ID;PRODUCT_ID;QUANTITY;RESULTS;FINAL_VOTE\n")

def query_product_response_consensus(ch, method, properties, body):
    bodega, correlation, pindex, quantity, result = body.decode("utf-8").split(";")
    print(f"VOTING_RES;{correlation};{bodega};{pindex};{quantity};{result}")

    info_bodegas = {} 
    if r.exists(correlation):
        info_bodegas = r.hgetall(correlation)
    info_bodegas[bodega] = result
    
    if len(info_bodegas) == NUM_REPLICAS:
        num_positives = 0
        results = ""
        for result in info_bodegas.values():
            results += result
            if result == "Y":
                num_positives += 1
        final_vote = "Y" if num_positives > NUM_REPLICAS / 2 else "N"

        write_to_output(f"VOTING_RES;{correlation};{pindex};{quantity};{results};{final_vote}\n")


channel.basic_consume(
    queue=queue_name, on_message_callback=query_product_response_consensus, auto_ack=True
)
channel.start_consuming()
