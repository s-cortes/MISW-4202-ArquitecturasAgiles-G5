from datetime import datetime, timedelta
from flask import Flask
from flask_jwt_extended import create_access_token
from flask_jwt_extended import JWTManager
from flask_restful import Api
import timesched
import requests
import hashlib
import json
import logging

logging.basicConfig(filename='record.log', level=logging.INFO)


app = Flask(__name__)  
app_context = app.app_context()
app_context.push()

app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
jwt = JWTManager(app)
api = Api(app)

s = timesched.Scheduler()
def callback(typ, arg):
    ds = str(datetime.now())[:19]

    token = requests.get(f"https://jwt-queries:5000/api-queries/jwt", verify=False)
    token = token.json()
    app.logger.debug(token['access_token'])

    url = 'https://routes-queries:5000/api-queries/routes'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+ token['access_token']
    }
    body = {
        'id': 201531124,
        'name': 'monitor'
    }
    response = requests.get(url, verify=False, headers=headers, json=body)
    md5_response = response.json()
    checksum = md5_response['checksum']

    data_md5 = hashlib.md5(json.dumps(body, sort_keys=True).encode('utf-8')).hexdigest()
    logging.info(f'App rutas respondio  {datetime.now()}')
  
    if checksum != data_md5:
        logging.info(f'App rutas fallo {datetime.now()}')
    else:
        logging.info(f'App rutas respondio correctamente {datetime.now()}')

    print(f'{ds} {typ} {arg}, active={s.count()}, response={response.text}, md5={data_md5}, md5={checksum}')


callback('started', 'now')

minute = timedelta(minutes=0.5)
s.repeat(minute, 0, callback, 'repeat', minute)
s.run()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')