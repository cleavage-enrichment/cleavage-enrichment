from functools import wraps
import json
import logging
from io import StringIO
import traceback

from django.http import JsonResponse

class InMemoryLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_output = StringIO()

    def emit(self, record):
        msg = self.format(record)
        self.log_output.write(msg + '\n')

    def get_logs(self):
        return self.log_output.getvalue()


def with_logging(view_func):
    """
    Decorator that attaches an in-memory log handler to capture logs 
    during the execution of a view and injects it into the response.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        logger = logging.getLogger()
        log_handler = InMemoryLogHandler()
        log_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)
        logger.propagate = False

        try:
            response = view_func(request, logger, *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            logger.error(f"{e}")
            response = JsonResponse({"error": str(e)})
        finally:
            logs = list(set(log_handler.get_logs().splitlines()))
            logger.removeHandler(log_handler)
            log_handler.close()

        # Ensure logs are added to JSON response
        if isinstance(response, JsonResponse):
            payload = json.loads(response.content)
            payload["logs"] = logs
            response = JsonResponse(payload)

        return response
    return wrapper