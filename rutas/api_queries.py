import hashlib
import json
from base import app, api, Resource, Flask, request
from base import EXPERIMENT_ID, IDENTITY, IDENTITY_TOKEN, IDENTITY_ROL
from base import publish_storage_plan, working_correctly, write_to_output
from flask_jwt_extended import jwt_required, get_jwt_identity
import random


class RouteResource(Resource):
    @jwt_required()
    def get(self):
        r = random.random()
        if r > 0.9:
            data_md5 = hashlib.md5(json.dumps("error", sort_keys=True).encode("utf-8")).hexdigest()
        else:
            data_md5 = hashlib.md5(json.dumps(request.json, sort_keys=True).encode("utf-8")).hexdigest()
        
        return {"checksum": data_md5}, 200
    
    @jwt_required()
    def post(self):
        payload, current_user = request.json, get_jwt_identity()

        if current_user == "admin":
            is_healthy = working_correctly()
            state = "HEALTHY" if is_healthy else "FLAKY"
            payload["rol"] = IDENTITY_TOKEN

            message = json.dumps(payload, sort_keys=True)
            checksum = hashlib.md5(message.encode("utf-8")).hexdigest()

            if not is_healthy:
                payload["rol"] = IDENTITY
                message = json.dumps(payload, sort_keys=True)

            write_to_output(f"ROUTE;{EXPERIMENT_ID};200;{state};{message};{checksum}")
            publish_storage_plan(f"{message};{checksum}")

            return {"msg": "successful Processing"}, 200
        else:
            write_to_output(f"ROUTE;{EXPERIMENT_ID};403;;;")
            return {"msg": "Unauthorized"}, 403


api.add_resource(RouteResource, "/api-queries/routes")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", ssl_context="adhoc")
