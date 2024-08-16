# routes.py
import logging
import time
import uuid
from multiprocessing import Process

from flask import jsonify
from flask_apispec import use_kwargs, marshal_with
from marshmallow import Schema, fields

logger = logging.getLogger(__name__)

class JobSchema(Schema):
    job_type = fields.Str(required=True, description="The type of job to run")

class JobResponseSchema(Schema):
    job_id = fields.Str(description="The ID of the submitted job")

class JobStatusSchema(Schema):
    status = fields.Str(description="The status of the job")
    start_time = fields.Float(description="The start time of the job")
    end_time = fields.Float(description="The end time of the job", allow_none=True)

def register_routes(app, job_db, status_queue):
    @app.route('/submit_job', methods=['POST'])
    @use_kwargs(JobSchema)
    @marshal_with(JobResponseSchema)
    def submit_job(job_type):
        """Submit a new job"""
        logger.info(f"Recibida solicitud para un nuevo trabajo: {job_type}")

        job = get_job_instance(job_type)
        if not job:
            logger.warning(f"Tipo de trabajo no reconocido: {job_type}")
            return jsonify({'error': 'Tipo de trabajo no reconocido'}), 400

        job_id = str(uuid.uuid4())
        start_time = time.time()
        job_db.add_job(job_id, 'running', start_time)

        logger.info(f"Trabajo con ID: {job_id} en estado 'running'")

        p = Process(target=run_job, args=(job_id, job, status_queue))
        p.start()

        logger.info(f"Proceso iniciado para el trabajo con ID: {job_id}, PID: {p.pid}")
        return {'job_id': job_id}, 202

    @app.route('/job_status/<job_id>', methods=['GET'])
    @marshal_with(JobStatusSchema)
    def job_status(job_id):
        """Get the status of a job"""
        job = job_db.get_job(job_id)
        if job:
            logger.info(f"Estado del trabajo con ID: {job_id} consultado. Estado: {job['status']}")
            return job
        logger.warning(f"Trabajo con ID: {job_id} no encontrado")
        return jsonify({'error': 'Trabajo no encontrado'}), 404

    return [submit_job, job_status]  # Retorna las funciones de las rutas

def get_job_instance(job_type):
    from jobs import ExampleJob
    job_classes = {
        'example': ExampleJob
    }
    return job_classes.get(job_type)()

def run_job(job_id, job, status_queue):
    start_time = time.time()
    try:
        logger.info(f"Iniciando trabajo con ID: {job_id}")
        job.run()
        end_time = time.time()
        status_queue.put((job_id, 'completed', end_time))
        logger.info(f"Trabajo con ID: {job_id} completado en {end_time - start_time:.2f} segundos")
    except Exception as e:
        status_queue.put((job_id, 'failed', None))
        logger.error(f"Error en el trabajo con ID: {job_id} - {str(e)}")