import hashlib
import json
from base import app, api, Resource, Flask, request, publish_storage_plan
from flask_jwt_extended import jwt_required, get_jwt_identity
import random


class RouteResource(Resource):
    @jwt_required()
    def get(self):
        r = random.random()
        if r > 0.9:
            data_md5 = hashlib.md5(json.dumps('error', sort_keys=True).encode('utf-8')).hexdigest()
        else:
            data_md5 = hashlib.md5(json.dumps(request.json, sort_keys=True).encode('utf-8')).hexdigest()
        
        return {"checksum": data_md5}, 200
    
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if current_user == 'admin':
            message = json.dumps(request.json, sort_keys=True).encode('utf-8')
            checksum = hashlib.md5(message).hexdigest()
            
            publish_storage_plan(message, checksum)
            return {"msg": "successful Processing"}, 200
        else:
            return {"msg": "Unauthorized"}, 403


api.add_resource(RouteResource, '/api-queries/routes')



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')
