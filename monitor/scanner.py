import hashlib
import json
import requests
from schedule import every, repeat, run_pending
import time
from base import app, Resource, Flask, request
from flask_jwt_extended import create_access_token

@repeat(every(30).minutes)
def scan():
    cuerpo = {
        "message":"Hola Gestor Rutas"
    }
    data_esperada = hashlib.md5(json.dumps(cuerpo, sort_keys=True).encode('utf-8')).hexdigest()
    token = create_access_token()
    peticion = requests.get("url_gestor_rutas",
                            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(token)},
                            json=cuerpo)
    #Deberia primero validar el status code y hacer un loggcito
    data_recibida = peticion.json
    if(data_esperada == data_recibida):
        #Todo salio bien
        pass
    else:
        #Todo se derrumbo dentro del Gestor Rutas
        pass
    
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')
    while True:
        run_pending()
        time.sleep(1)
