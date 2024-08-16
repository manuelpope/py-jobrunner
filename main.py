# import logging
# from flask import Flask, jsonify, request
# from multiprocessing import Process, Queue, freeze_support
# import time
# import uuid
#
# from flasgger import Swagger
#
# from InitDB import init_db
# from JobDataBase import JobDatabase
#
# # Configurar logging con fecha, hora, nombre del proceso y del thread
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(processName)s %(threadName)s] %(levelname)s %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )
# logger = logging.getLogger(__name__)
#
# app = Flask(__name__)
# swagger = Swagger(app)
#
#
# class ExampleJob:
#     def run(self):
#         logger.info("Ejecutando ExampleJob")
#         time.sleep(10)  # Simulando un trabajo que toma 10 segundos
#         logger.info("ExampleJob completado")
#
#
# def run_job(job_id, job, status_queue):
#     start_time = time.time()
#     try:
#         logger.info(f"Iniciando trabajo con ID: {job_id}")
#         job.run()
#         status_queue.put((job_id, 'completed', time.time()))
#         logger.info(f"Trabajo con ID: {job_id} completado en {time.time() - start_time:.2f} segundos")
#     except Exception as e:
#         status_queue.put((job_id, 'failed', None))
#         logger.error(f"Error en el trabajo con ID: {job_id} - {str(e)}")
#
#
# def monitor_processes(status_queue, job_db):
#     while True:
#         while not status_queue.empty():
#             job_id, status, end_time = status_queue.get()
#             job_db.update_job(job_id, status, end_time)
#             logger.info(f"Estado final del trabajo con ID: {job_id} actualizado a '{status}'")
#         time.sleep(5)  # Revisar cada 5 segundos
#
#
# @app.route('/submit_job', methods=['POST'])
# def submit_job():
#     """
#     Submit a new job
#     ---
#     parameters:
#       - name: body
#         in: body
#         required: true
#         schema:
#           id: job
#           required:
#             - job_type
#           properties:
#             job_type:
#               type: string
#               description: The type of job to run
#     responses:
#       202:
#         description: Job submitted successfully
#       400:
#         description: Invalid job type
#     """
#     global job_db, status_queue
#     job_type = request.json.get('job_type')
#     logger.info(f"Recibida solicitud para un nuevo trabajo: {job_type}")
#
#     if job_type == 'example':
#         job = ExampleJob()
#     else:
#         logger.warning(f"Tipo de trabajo no reconocido: {job_type}")
#         return jsonify({'error': 'Tipo de trabajo no reconocido'}), 400
#
#     job_id = str(uuid.uuid4())  # Usar UUID en lugar de timestamp
#     start_time = time.time()
#     job_db.add_job(job_id, 'running', start_time)
#
#     logger.info(f"Trabajo con ID: {job_id} en estado 'running'")
#
#     # Iniciar el trabajo en un proceso separado
#     p = Process(target=run_job, args=(job_id, job, status_queue))
#     p.start()
#
#     logger.info(f"Proceso iniciado para el trabajo con ID: {job_id}, PID: {p.pid}")
#     return jsonify({'job_id': job_id}), 202
#
#
# @app.route('/job_status/<job_id>', methods=['GET'])
# def job_status(job_id):
#     """
#     Get the status of a job
#     ---
#     parameters:
#       - name: job_id
#         in: path
#         type: string
#         required: true
#     responses:
#       200:
#         description: Job status retrieved successfully
#       404:
#         description: Job not found
#     """
#     global job_db
#     job = job_db.get_job(job_id)
#     if job:
#         logger.info(f"Estado del trabajo con ID: {job_id} consultado. Estado: {job['status']}")
#         return jsonify(job)
#     logger.warning(f"Trabajo con ID: {job_id} no encontrado")
#     return jsonify({'error': 'Trabajo no encontrado'}), 404
#
#
# def main():
#     global job_db, status_queue
#     init_db()  # Inicializar la base de datos
#     job_db = JobDatabase()  # Inicializar la base de datos en SQLite
#     status_queue = Queue()  # Crear una cola para las actualizaciones de estado
#
#     monitor_proc = Process(target=monitor_processes, args=(status_queue, job_db))
#     monitor_proc.start()
#     logger.info("Iniciando la aplicación Job Runner API")
#     app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
#
#
# if __name__ == '__main__':
#     freeze_support()
#     main()
