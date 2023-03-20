import hashlib
import json
from base import EXPERIMENT_ID
from base import COUNT_VEHICLES
from base import write_to_output, update_status_transport
from base import app, api, Resource, Flask, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import random


class TransportResource(Resource):
    @jwt_required()
    def post(self):
        payload, current_user = request.json, get_jwt_identity()

        if current_user == 'admin':
             checksum_original = request.headers['CheckSum']

             message = json.dumps(payload, sort_keys=True).encode('utf-8')
             checksum_validation = hashlib.md5(message).hexdigest()
             if(checksum_original == checksum_validation):
                 write_to_output(f"TRANSPORT;{EXPERIMENT_ID};200;{payload['inactive_vehicles']};{checksum_original};{checksum_validation}")
             else:
                 write_to_output(f"TRANSPORT;{EXPERIMENT_ID};400;{payload['inactive_vehicles']};{checksum_original};{checksum_validation}")
                 return {"msg": "Bad Request"}, 400 

             return {"msg": "successful Processing"}, 200
        else:
             write_to_output(f"TRANSPORT;{EXPERIMENT_ID};403;;;;")
             return {"msg": "Unauthorized"}, 403


api.add_resource(TransportResource, '/api-commands/availability')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')
