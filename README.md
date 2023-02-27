# MISW-4202-ArquitecturasAgiles-G5

Este repositorio contiene el código relacionado a las actividades del curso MISW4202, Arquitecturas Ágiles de Software, del semestre 202310.

## Integrantes

* Melissa Castro [m.castros@uniandes.edu.co](mailto:m.castros@uniandes.edu.co)
* Ivan Mateo Bohorquez Perez [i.bohorquezp@uniandes.edu.co](i.bohorquezp@uniandes.edu.co)
* Miguel Angel Orjuela [ma.orjuela73@uniandes.edu.co](ma.orjuela73@uniandes.edu.co)
* Santiago Cortés Fernández [s.cortes@uniandes.edu.co](s.cortes@uniandes.edu.co)

## Instalación

Los servicios de este ejemplo utilizan *flask*, *redis*, *rabbitMQ*, *docker* y *docker-compose*. Para su instalación debe clonar este repositorio, e instalar *docker* y *docker-compose*.

```shell
git clone github.com:s-cortes/MISW-4202-ArquitecturasAgiles-G5.git
```

## Ejecución

Para correr la aplicación se debe ejecutar alguno de los siguientes comandos:


```shell
docker compose up
docker compose up -d
```

## Estructura del Repositorio


## Descripción de los servicios táctica votación

Esta rama (async-sec) muestra la comunicación entre servicios de manera asíncrona e implementa el patrón CQRS. Para la comunicación asíncrona, se hace uso de ***RabbitMQ*** como plataforma de mensajería. Para la seguridad se utiliza un certificado SSL para asegurar la comunicación entre los servicios. A continuación, se explica con mayor detalle cada uno de los servicios.


### Bodegas

Al implemetar el patrón CQRS las operaciones que expone este servicio se implementan en dos partes: consultas (`api_queries.py`) y eventos/queries asíncronos (`event_queries.py`). En particular, se tienen las siguientes operaciones:

- **Consultar Productos** (`api_queries.py`): Esta operación se implementa en la función `ProductListResource` a través del método get.
- **Consultar Disponibilidad Producto** (`api_queries.py`): Esta operación se implementa en la función `ProductResource` a través del método get.

- **Consultar Disponibilidad Producto** (`event_queries.py`): Esta operación utiliza la plataforma de mensajería para recibir request. Para su funcionamiento/orquestación, se deben definir las siguientes variables de entorno:

```shell
# File ./events.env

# Exchance para la conexión entre Voting y Bodega
VOTING_EXCHANGE_NAME="product_exchange"

# Nombre del Queue para la publicación de requests
VOTING_ROUTING_REQUEST_Q="product_request_queue"
# Routing Key para el direccionamiento de mensajes
VOTING_ROUTING_REQUEST_KEY="vote_product_request"

# Nombre del Queue para la publicación de responses
VOTING_ROUTING_RESPONSE_Q="product_response_queue"
# Routing Key para el direccionamiento de mensajes
VOTING_ROUTING_RESPONSE_KEY="vote_product_response"

# identificador del experimento
VOTING_EXPERIMENT_ID="example"
```

#### Ejecución

Para desplegar este servicio, se utiliza *docker-compose* para levantar los contenedores relacionados. Por otra parte, para la ejecución de ***experimentos de disponibilidad*** es necesario realizar los cambios:
* Editar el archivo `docker-compose.yaml` para definir el número de répicas de contenedores "healthy" (funcionando correctamente, `services > products-healthy-events > deploy > replicas`) y contenedores "flaky" (inyección de fallas, `services > products-flaky-events > deploy > replicas`), 
* Editar el archivo `docker-compose.yaml` para definir la probabilidad de inyectar un error para el componente *products-flaky-events* (`services > products-flaky-events > environment > FAILURE_PROBABILITY`)
* Editar la variable de entorno ***VOTING_EXPERIMENT_ID*** (`/events.env`) para la captura de resultados.


```shell
docker compose up -d products-flaky-events
docker compose up -d products-healthy-events
```

#### Outputs
Luego de ejecutar un experimento, cada instancia desplegada genera un archivo `.csv` con las operaciones realizadas. En la carpeta `./bodegas/outputs` se encuentra un ejemplo de ejecución del experimento.


### Votaciones

Este servicio implementa la táctica de disponibilidad ***Voting*** entre los servicio de [Bodegas](#Bodegas). En particular, esta táctica fue implementada utilizando comunicación asíncrona entre los componentes, utilizando ***RabbitMQ*** como plataforma de mensajería. Para su funcionamiento/orquestación, se deben definir las siguientes variables de entorno:

```shell
# File ./events.env

# Exchance para la conexión entre Voting y Bodega
VOTING_EXCHANGE_NAME="product_exchange"

# Nombre del Queue para la publicación de requests
VOTING_ROUTING_REQUEST_Q="product_request_queue"
# Routing Key para el direccionamiento de mensajes
VOTING_ROUTING_REQUEST_KEY="vote_product_request"

# Nombre del Queue para la publicación de responses
VOTING_ROUTING_RESPONSE_Q="product_response_queue"
# Routing Key para el direccionamiento de mensajes
VOTING_ROUTING_RESPONSE_KEY="vote_product_response"

# identificador del experimento
VOTING_EXPERIMENT_ID="example"
```

Este servicio expone las siguientes operaciones:

* **Publicación Request**: Implementa la lógica para realizar requests (queries) al servicio de [Bodegas](#Bodegas) (ver `requests_events.py`)
* **Gestor Responses**: Implementa la lógica para la recepción de responses del servicio de [Bodegas](#Bodegas), al igual que la lógica para realizar la votación y consenso entre respuestas (ver `resaponse_events.py`)

#### Ejecución

Para desplegar este servicio, se utiliza *docker-compose* para levantar los contenedores relacionados. Por otra parte, para la ejecución de ***experimentos de disponibilidad*** es necesario editar el archivo `./votaciones/requests.env` para definir el número y periodicidad de los requests a realizar. Del mismo modo, se debe definir la variable de entorno ***VOTING_EXPERIMENT_ID*** (`/events.env`) para la captura de resultados.

```shell
docker compose up -d voting-responses
docker compose up -d voting-requests
```

```shell
# File ./votaciones/requests.env

# Numero de requests a publicar
NUM_REQUESTS=5
# Intervalo de espera entre publicaciones
REQUEST_INTERVAL=0.5
```

#### Outputs
Luego de ejecutar un experimento, cada instancia desplegada genera un archivo `.csv` con las operaciones realizadas. En la carpeta `./votaciones/outputs` se encuentra un ejemplo de ejecución del experimento.



### Jwt

Este servicio se encarga de gestionar los tokens que deben ser utilizados por los demás servicios y expone una sola operación:

- Crear token: Esta operación se implementa en la función AuthResource a través del método get, la cual retorna un token el cual se debe incluir en el llamado de cualquiera de los otros servicios descritos anteriormente.

Este componente fue creado al utilizar como referencia el repositorio [ci-cortesg/fotoalpes-microservices-examples](https://github.com/ci-cortesg/fotoalpes-microservices-examples) (licencia compatible MIT).

#### Ejecución

Para desplegar este servicio, se utiliza *docker-compose* para levantar los contenedores relacionados.
```shell
docker compose up -d jwt-queries
```



### API Gateway

Se utiliza la configuración proxy del servidor *Ngnix* para la implementación del API Gateway. Esta configuración permite que todas las solicitudes se hagan al servidor Ngnix y este redireccione al servicio correspondiente (ver `MISW-4202-ArquitecturasAgiles-G5/nginx/nginx-proxy.conf`).

Este componente fue creado al utilizar como referencia el repositorio [ci-cortesg/fotoalpes-microservices-examples](https://github.com/ci-cortesg/fotoalpes-microservices-examples) (licencia compatible MIT).

#### Ejecución

Para desplegar este servicio, se utiliza *docker-compose* para levantar los contenedores relacionados.
```shell
docker compose up -d nginx
```

### Plataforma de Mensajería Asíncrona

Se utiliza la imagen "alpine" de *RabbitMQ* para la implementación de la plataforma de mensajería . Esta configuración se puede encontrar en los componentes de [Bodegas](#Bodegas) y [Votaciones](#Votaciones). Adicionalmente, se expone el puerto `15672` para poder utilizar de manera local la página de gestión de *RabbitMQ* (http://localhost:15672/)[http://localhost:15672/]

#### Ejecución

Para desplegar este servicio, se utiliza *docker-compose* para levantar los contenedores relacionados.
```shell
docker compose up -d rabbitmq
```
## Descripción de los servicios táctica monitor condicional

### Rutas
- **Consultar Disponibilidad Rutas** (`api_queries.py`): Esta operación se implementa en la función `RouteMonitoringResource` a través del método get.

### Monitor Rutas
- Mediante el uso de la libreria timesched.Scheduler se implmenta la función llamda callback la cual envia requests de manera recurrente hacia el componente rutas.

#### Ejecución

Para desplegar este servicio, se utiliza *docker-compose* para levantar los contenedores relacionados.
```shell
docker compose up monitor-rutas
```
