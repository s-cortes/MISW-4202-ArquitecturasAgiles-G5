import hashlib
import json
from base import app, api, Resource, Flask, request
from flask_jwt_extended import jwt_required
import random


class RouteMonitoringResource(Resource):
    @jwt_required()
    def get(self):
        r = random.random()
        if r > 0.9:
            data_md5 = hashlib.md5(json.dumps('error', sort_keys=True).encode('utf-8')).hexdigest()
        else:
            data_md5 = hashlib.md5(json.dumps(request.json, sort_keys=True).encode('utf-8')).hexdigest()
        
        return {"checksum": data_md5}, 200


api.add_resource(RouteMonitoringResource, '/api-queries/routes')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')
