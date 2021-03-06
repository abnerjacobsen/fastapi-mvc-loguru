# das_sankhya
[![CI](https://your.repo.url.here/actions/workflows/main.yml/badge.svg?branch=master)](https://your.repo.url.here/actions/workflows/main.yml)
[![K8s integration](https://your.repo.url.here/actions/workflows/integration.yml/badge.svg)](https://your.repo.url.here/actions/workflows/integration.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub](https://img.shields.io/badge/fastapi-v.0.70.0-blue)
![GitHub](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9-blue)
![GitHub](https://img.shields.io/badge/license-MIT-blue)

## This project was generated with [fastapi-mvc](https://github.com/rszamszur/fastapi-mvc)

---

## Prerequisites

If You want to go easy way and use provided virtualized environment You'll need to have installed:
* rsync 
* Vagrant [How to install vagrant](https://www.vagrantup.com/downloads)
* (Optional) Enabled virtualization in BIOS

Otherwise, for local complete project environment with k8s infrastructure bootstrapping You'll need:

For application:
* Python 3.7 or later installed [How to install python](https://docs.python-guide.org/starting/installation/)
* Poetry [How to install poetry](https://python-poetry.org/docs/#installation)

For infrastructure:
* make, gcc, golang
* minikube version 1.22.0 [How_to_install_minikube](https://minikube.sigs.k8s.io/docs/start/)
* helm version 3.0.0 or higher [How_to_install_helm](https://helm.sh/docs/intro/install/)
* kubectl version 1.16 up to 1.20.8 [How_to_install_kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
* Container runtime interface. NOTE! dev-env script uses docker for minikube, for other CRI you'll need to modify this line in dev-env.sh `MINIKUBE_IN_STYLE=0 minikube start --driver=docker 2>/dev/null`

## Quickstart
First run `vagrant up` in project root directory and enter virtualized environment using `vagrant ssh`
Then run following commands to bootstrap local development cluster exposing `fastapi-mvc` application.
```sh
$ cd /syncd
$ make dev-env
```
*Note: this process may take a while on first run.*

Once development cluster is up and running you should see summary listing application address:
```
Kubernetes cluster ready

fastapi-mvc available under: http://das_sankhya.192.168.49.2.nip.io/

You can delete dev-env by issuing: minikube delete
```
*Note: above address may be different for your installation.*

*Note: provided virtualized env doesn't have port forwarding configured which means, that bootstrapped application stack in k8s won't be accessible on Host OS.*

Deployed application stack in Kubernetes:
```shell
vagrant@ubuntu-focal:/syncd$ make dev-env
...
...
...
Kubernetes cluster ready
FastAPI available under: http://das_sankhya.192.168.49.2.nip.io/
You can delete dev-env by issuing: make clean
vagrant@ubuntu-focal:/syncd$ kubectl get all -n das_sankhya
NAME                                                     READY   STATUS    RESTARTS   AGE
pod/das_sankhya-7f4dd8dc7f-p2kr7                1/1     Running   0          55s
pod/rfr-redisfailover-persistent-keep-0                  1/1     Running   0          3m39s
pod/rfr-redisfailover-persistent-keep-1                  1/1     Running   0          3m39s
pod/rfr-redisfailover-persistent-keep-2                  1/1     Running   0          3m39s
pod/rfs-redisfailover-persistent-keep-5d46b5bcf8-2r7th   1/1     Running   0          3m39s
pod/rfs-redisfailover-persistent-keep-5d46b5bcf8-6kqv5   1/1     Running   0          3m39s
pod/rfs-redisfailover-persistent-keep-5d46b5bcf8-sgtvv   1/1     Running   0          3m39s

NAME                                        TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)     AGE
service/das_sankhya                ClusterIP   10.110.42.252   <none>        8000/TCP    56s
service/rfs-redisfailover-persistent-keep   ClusterIP   10.110.4.24     <none>        26379/TCP   3m39s

NAME                                                READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/das_sankhya                1/1     1            1           55s
deployment.apps/rfs-redisfailover-persistent-keep   3/3     3            3           3m39s

NAME                                                           DESIRED   CURRENT   READY   AGE
replicaset.apps/das_sankhya-7f4dd8dc7f                1         1         1       55s
replicaset.apps/rfs-redisfailover-persistent-keep-5d46b5bcf8   3         3         3       3m39s

NAME                                                 READY   AGE
statefulset.apps/rfr-redisfailover-persistent-keep   3/3     3m39s

NAME                                                                  AGE
redisfailover.databases.spotahome.com/redisfailover-persistent-keep   3m39s
vagrant@ubuntu-focal:/syncd$ curl http://das_sankhya.192.168.49.2.nip.io/api/ready
{"status":"ok"}
```

## Installation

With make:
```shell
make install
```

You can customize poetry installation with [environment variables](https://python-poetry.org/docs/configuration/#using-environment-variables) 
```shell
export POETRY_HOME=/custom/poetry/path
export POETRY_CACHE_DIR=/custom/poetry/path/cache
export POETRY_VIRTUALENVS_IN_PROJECT=true
make install
```

Or using poetry directly:
```shell
poetry install
```

To bootstrap local minikube Kubernetes cluster exposing `das_sankhya` application:
```shell
make dev-env
```

## CLI

This package exposes simple CLI for easier interaction:

```shell
$ das_sankhya --help
Usage: das_sankhya [OPTIONS] COMMAND [ARGS]...

  das_sankhya CLI root.

Options:
  -v, --verbose  Enable verbose logging.
  --help         Show this message and exit.

Commands:
  serve  das_sankhya CLI serve command.
$ das_sankhya serve --help
Usage: das_sankhya serve [OPTIONS]

  das_sankhya CLI serve command.

Options:
  --host TEXT                  Host to bind.  [default: localhost]
  -p, --port INTEGER           Port to bind.  [default: 8000]
  -w, --workers INTEGER RANGE  The number of worker processes for handling
                               requests.  [default: 2;1<=x<=8]
  --help                       Show this message and exit.
```

*NOTE: Maximum number of workers may be different in your case, it's limited to `multiprocessing.cpu_count()`*

To serve application simply run:

```shell
$ das_sankhya serve
```

To confirm it's working:

```shell
$ curl localhost:8000/api/ready
{"status":"ok"}
```

## Dockerfile

This repository provides Dockerfile for virtualized environment.

*NOTE: Replace podman with docker if it's yours containerization engine.*
```shell
$ make image
$ podman run -dit --name das_sankhya -p 8000:8000 das_sankhya:$(cat TAG)
f41e5fa7ffd512aea8f1aad1c12157bf1e66f961aeb707f51993e9ac343f7a4b
$ podman ps
CONTAINER ID  IMAGE                                 COMMAND               CREATED        STATUS            PORTS                   NAMES
f41e5fa7ffd5  localhost/das_sankhya:0.1.0  /usr/bin/fastapi ...  2 seconds ago  Up 3 seconds ago  0.0.0.0:8000->8000/tcp  das_sankhya
$ curl localhost:8000/api/ready
{"status":"ok"}
```

## Application configuration

This application provides flexibility of configuration. 
All significant settings are defined by the environment variables, each with the default value. 
Moreover, package CLI allows overriding core ones: host, port, workers. 
You can modify all other available configuration settings in the gunicorn.conf.py file.

Priority of overriding configuration:
1. cli
2. environment variables
3. gunicorn.conf.py

All application configuration is available in `das_sankhya.config` submodule.

### Environment variables

#### Application configuration

| Key                  | Default                                                         | Description                                                    |
|----------------------|-----------------------------------------------------------------|----------------------------------------------------------------|
| FASTAPI_HOST         | `"127.0.0.1"`                                                   | FastAPI host to bind.                                          |
| FASTAPI_PORT         | `"8000"`                                                        | FastAPI port to bind.                                          |
| FASTAPI_WORKERS      | `"2"`                                                           | Number of gunicorn workers (uvicorn.workers.UvicornWorker)     |
| FASTAPI_DEBUG        | `"True"`                                                        | FastAPI logging level. You should disable this for production. |
| FASTAPI_PROJECT_NAME | `"das_sankhya"`                               | FastAPI project name.                                          |
| FASTAPI_VERSION      | `"0.4.0"`                                                       | Application version.                                           |
| FASTAPI_DOCS_URL     | `"/"`                                                           | Path where swagger ui will be served at.                       |
| FASTAPI_USE_REDIS    | `"False"`                                                       | Whether or not to use Redis.                                   |
| FASTAPI_GUNICORN_LOG_LEVEL | `"info"`                                                        | The granularity of gunicorn log output |
| FASTAPI_GUNICORN_LOG_FORMAT | `'%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'` | Gunicorn log format |

#### Redis configuration

| Key                        | Default       | Description                               |
|----------------------------|---------------|-------------------------------------------|
| FASTAPI_REDIS_HOTS         | `"127.0.0.1"` | Redis host.                               |
| FASTAPI_REDIS_PORT         | `"6379"`      | Redis port.                               |
| FASTAPI_REDIS_USERNAME     | `""`          | Redis username.                           |
| FASTAPI_REDIS_PASSWORD     | `""`          | Redis password.                           |
| FASTAPI_REDIS_USE_SENTINEL | `"False"`     | If provided Redis config is for Sentinel. |

### gunicorn.conf.py

1. Source: `das_sankhya.config/gunicorn.conf.py`
2. [Gunicorn configuration file documentation](https://docs.gunicorn.org/en/latest/settings.html)

### Routes definition

Endpoints are defined in `das_sankhya.config.router`. Just simply import your controller and include it to FastAPI router:

```python
from fastapi import APIRouter
from das_sankhya.app.controllers.api.v1 import ready

router = APIRouter(
    prefix="/api"
)

router.include_router(ready.router, tags=["ready"])
```

## Development

You can implement your own web routes logic straight away in `das_sankhya.app.controllers.api.v1` submodule. For more information please see [FastAPI documentation](https://fastapi.tiangolo.com/tutorial/).

### Utilities

For your discretion, I've provided some basic utilities:
* RedisClient `das_sankhya.app.utils.redis`
* AiohttpClient `das_sankhya.app.utils.aiohttp_client`

They're initialized in `asgi.py` on FastAPI startup event handler:

```python
async def on_startup():
    """Fastapi startup event handler.

    Creates RedisClient and AiohttpClient session.

    """
    log.debug("Execute FastAPI startup event handler.")
    # Initialize utilities for whole FastAPI application without passing object
    # instances within the logic. Feel free to disable it if you don't need it.
    if settings.USE_REDIS:
        await RedisClient.open_redis_client()

    AiohttpClient.get_aiohttp_client()


async def on_shutdown():
    """Fastapi shutdown event handler.

    Destroys RedisClient and AiohttpClient session.

    """
    log.debug("Execute FastAPI shutdown event handler.")
    # Gracefully close utilities.
    if settings.USE_REDIS:
        await RedisClient.close_redis_client()

    await AiohttpClient.close_aiohttp_client()
```

and are available for whole application scope without passing object instances. In order to utilize it just execute classmethods directly.

Example:
```python
from das_sankhya.app.utils import RedisClient

response = RedisClient.get("Key")
```
```python
from das_sankhya.app.utils import AiohttpClient

response = AiohttpClient.get("http://foo.bar")
```

### Exceptions

#### HTTPException and handler

Source: `das_sankhya.app.exceptions.http.py`

This exception combined with `http_exception_handler` method allows you to use it the same manner as you'd use `FastAPI.HTTPException` with one difference. 
You have freedom to define returned response body, whereas in `FastAPI.HTTPException` content is returned under "detail" JSON key.
In this application custom handler is added in `asgi.py` while initializing FastAPI application. 
This is needed in order to handle it globally.

### Web Routes
All routes documentation is available on:
* `/` with Swagger
* `/redoc` or ReDoc.

## License

This project is licensed under the terms of the MIT license.


With the help of some information obtained on the internet I was able to customize the fastapi-mvc-example to do the following:

* Use loguru instead of the standard Python logging module to manage system logs. Apparently loguru works better with threads and multiprocessing.

* Capture all logs, even Gunicorn startup logs with the custom log format I intend to use in my application.
* Put the following information in the log lines: PID of the process (gunicorn worker) that generated the log, x-correlation-id and x-request-id (a necessity of my application and which are generated/obtained by a fastapi middleware )
* Gunicorn's master and workers appear with a friendly name when I run a ps axu

By default I generate the logs in stdout, but I also tested saving the logs in a file and it worked perfectly, even after rotating the file. Each worker continued writing to the same file after loguru's file rotation.

My version of wsgi.py is hardcoded to configure Gunicorn as per this post: https://medium.com/building-the-system/gunicorn-3-means-of-concurrency-efbb547674b7 - I don't know if it's the most efficient way , but in my tests it worked fine.

Although not complete, I added a new command to start a uvicorn server only, this is because I like to use its reload feature when I'm developing my code and I couldn't find a way to do this with Gunicorn - apparently it's impossible. The command is:

das_sankhya devserve

I used this information to prepare this demo:

* https://medium.com/building-the-system/gunicorn-3-means-of-concurrency-efbb547674b7
# https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/
* https://github.com/pahntanapat/Unified-FastAPI-Gunicorn-Log
* https://github.com/Delgan/loguru/issues/365
* https://loguru.readthedocs.io/en/stable/api/logger.html#sink

And the main changes I made are in these files:

* https://github.com/abnerjacobsen/fastapi-mvc-loguru/blob/main/das_sankhya/wsgi.py
* https://github.com/abnerjacobsen/fastapi-mvc-loguru/blob/main/das_sankhya/core/logs2.py
* https://github.com/abnerjacobsen/fastapi-mvc-loguru/blob/main/das_sankhya/core/gunicorn_logs.py