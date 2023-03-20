import os
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "secret-jwt"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
jwt = JWTManager(app)
api = Api(app)

ID_ADMIN = os.environ.get("ID_ADMIN")
ID_BODEGA = os.environ.get("ID_BODEGA")
ID_RUTA = os.environ.get("ID_RUTA")
ID_TRANSPORTE = os.environ.get("ID_TRANSPORTE")

ROLES = {
    ID_ADMIN: "admin",
    ID_BODEGA: "bodega",
    ID_RUTA: "ruta",
    ID_TRANSPORTE: "transporte"
}

class AuthResource(Resource):
    def post(self):
        payload, rol = request.json, "test"
        user, password = None, None
        if payload:
            user = payload.get("user", None)
            password = payload.get("password", None)
        if user and password and user==password and user in ROLES:
            rol = ROLES.get(user, "test")
            access_token = create_access_token(identity=rol)
            return jsonify(access_token=access_token, rol=rol)
        else:
            return {"msg": "Invalid user and/or password"}, 401

api.add_resource(AuthResource, "/api-queries/jwt")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", ssl_context="adhoc")