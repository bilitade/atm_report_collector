# gui_log_handler.py

import logging
from queue import Queue

class GUIConsoleLogHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        log_message = self.format(record)
        self.log_queue.put(log_message)