from flask import Flask, request
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager


app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "secret-jwt"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

jwt = JWTManager(app)
api = Api(app)
