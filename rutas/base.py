import os
import pika
from flask import Flask, request
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager

EXCHANGE_NAME = os.environ.get("STORAGE_PLAN_EXCHANGE_NAME")
ROUTING_KEY_NAME = os.environ.get("STORAGE_PLAN_ROUTING_REQUEST_KEY")

connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()
channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct")

def publish_storage_plan(message, checksum):
    channel.basic_publish(
        exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY_NAME, body=message
    )

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "secret-jwt"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

jwt = JWTManager(app)
api = Api(app)
