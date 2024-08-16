# main.py
import logging
import time
from multiprocessing import Process, Queue, freeze_support
from flask import Flask
from flask_apispec import FlaskApiSpec
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin


from InitDB import init_db
from JobDataBase import JobDatabase
from routes import register_routes

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(processName)s %(threadName)s] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuración de Swagger/APISpec
app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Job Runner API',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'
})

docs = FlaskApiSpec(app)

def monitor_processes(status_queue, job_db):
    while True:
        while not status_queue.empty():
            job_id, status, end_time = status_queue.get()
            job_db.update_job(job_id, status, end_time)
            logger.info(f"Estado final del trabajo con ID: {job_id} actualizado a '{status}'")
        time.sleep(5)  # Revisar cada 5 segundos

def initialize_app():
    init_db()
    job_db = JobDatabase()
    status_queue = Queue()

    route_functions = register_routes(app, job_db, status_queue)

    # Registrar las rutas con APISpec
    for func in route_functions:
        docs.register(func)

    monitor_proc = Process(target=monitor_processes, args=(status_queue, job_db))
    monitor_proc.start()
    logger.info("Iniciando la aplicación Job Runner API")

    return job_db, status_queue

def main():
    initialize_app()
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)

if __name__ == '__main__':
    freeze_support()
    main()