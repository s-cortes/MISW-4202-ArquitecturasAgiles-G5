import os
import pika
from flask import Flask, request
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager
from random import randint

EXCHANGE_NAME = os.environ.get("STORAGE_PLAN_EXCHANGE_NAME")
ROUTING_KEY_NAME = os.environ.get("STORAGE_PLAN_ROUTING_REQUEST_KEY")

WORKER_TYPE = os.environ.get("WORKER_TYPE", "HEALTHY")
HEALTHY_WORKER = WORKER_TYPE == "HEALTHY"
SUCCESS_PROBABILITY = int(os.environ.get("SUCCESS_PROBABILITY", "75"))

EXPERIMENT_ID = os.environ.get("EXPERIMENT_ID")
output_file_path = f"outputs/{EXPERIMENT_ID}.csv"

connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()
channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct")

def publish_storage_plan(message):
    channel.basic_publish(
        exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY_NAME, body=message
    )


def working_correctly():
    return HEALTHY_WORKER or randint(0, 100) >= SUCCESS_PROBABILITY


def write_to_output(message):
    print(message)
    with open(output_file_path, "a") as output_file:
        output_file.write(f"{message}\n")

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "secret-jwt"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

write_to_output("COMPONENT;CORRELATION_ID;RESPONSE;STATE_TYPE;BODY;CHECKSUM")

jwt = JWTManager(app)
api = Api(app)
