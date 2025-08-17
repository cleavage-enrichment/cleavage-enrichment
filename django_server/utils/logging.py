import logging
from io import StringIO

class InMemoryLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_output = StringIO()

    def emit(self, record):
        msg = self.format(record)
        self.log_output.write(msg + '\n')

    def get_logs(self):
        return self.log_output.getvalue()