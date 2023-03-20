from flask import Flask, request
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager
import os

EXPERIMENT_ID = os.environ.get("EXPERIMENT_ID")
COUNT_VEHICLES = os.environ.get("COUNT_VEHICLES")
output_file_path = f"outputs/{EXPERIMENT_ID}.csv"

def write_to_output(message):
    print(message)
    with open(output_file_path, "a") as output_file:
        output_file.write(f"{message}\n")

def update_status_transport(message):
    return (message > (COUNT_VEHICLES / 2))

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "secret-jwt"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

jwt = JWTManager(app)
api = Api(app)

write_to_output("COMPONENT;CORRELATION_ID;RESPONSE;STATE_TYPE;BODY;CHECKSUM_ORI;CHECKSUM_VAL")
