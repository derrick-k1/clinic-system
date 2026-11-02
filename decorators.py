import logging
from functools import wraps
from time import perf_counter

logging.basicConfig(
    filename="clinic.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_operation(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        logging.info("Started: %s", function.__name__)

        try:
            result = function(*args, **kwargs)
            logging.info("Completed: %s", function.__name__)
            return result

        except Exception:
            logging.exception("Failed: %s", function.__name__)
            raise

    return wrapper

def measure_time(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        start = perf_counter()

        try:
            return function(*args, **kwargs)

        finally:
            elapsed = perf_counter() - start

            logging.info(
                "%s took %.6f seconds",
                function.__name__,
                elapsed
            )

    return wrapper
