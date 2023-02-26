from datetime import datetime, timedelta
import hashlib
import json
from base import app, api, Resource, Flask, request
from flask_jwt_extended import jwt_required
import random
import os

EXPERIMENTO_ID = os.environ.get("EXPERIMENTO_ID")
output_file_path = f"output/{EXPERIMENTO_ID}.csv"

def write_to_output(message):
    print(message)
    with open(output_file_path, "a") as output_file:
        output_file.write(f"{message}\n")

class RouteMonitoringResource(Resource):
    @jwt_required()
    def get(self):
        r = random.random()
        
        if r > 0.9:
            data_md5 = hashlib.md5(json.dumps('error', sort_keys=True).encode('utf-8')).hexdigest()
            write_to_output(f'{datetime.now()};{data_md5};{"fail"}')
            
        else:
            data_md5 = hashlib.md5(json.dumps(request.json, sort_keys=True).encode('utf-8')).hexdigest()
            write_to_output(f'{datetime.now()};{data_md5};{ "ok"}')
        
        return {"checksum": data_md5}, 200


api.add_resource(RouteMonitoringResource, '/api-queries/routes')
write_to_output("time;response;result")



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')
    
