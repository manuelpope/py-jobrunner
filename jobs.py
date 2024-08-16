class ExampleJob:
    def run(self):
        import logging
        import time
        logger = logging.getLogger(__name__)
        logger.info("Ejecutando ExampleJob")
        time.sleep(10)  # Simulando un trabajo que toma 10 segundos
        logger.info("ExampleJob completado")