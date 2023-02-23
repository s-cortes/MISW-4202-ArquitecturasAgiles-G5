import hashlib
import json
from base import app, api, Resource, Flask, request
from flask_jwt_extended import jwt_required


class RouteMonitoringResource(Resource):
    @jwt_required()
    def get(self):
        data_md5 = hashlib.md5(json.dumps(request.json, sort_keys=True).encode('utf-8')).hexdigest()
        return {"checksum": data_md5}, 200


api.add_resource(RouteMonitoringResource, '/api-queries/routes')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')
