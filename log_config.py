import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os

# Determine the base destination folder and create the RunLog folder
BASE_DESTINATION_FOLDER = r'C:\ATMLogs'
RUN_LOG_FOLDER = os.path.join(BASE_DESTINATION_FOLDER, 'RunLog')
os.makedirs(RUN_LOG_FOLDER, exist_ok=True)

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a rotating file handler, with a new file created for each run
start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
human_readable_start_time = datetime.now().strftime("%Y-%m-%d_%I-%M-%S%p")
log_file_name = f'atm_log_{human_readable_start_time}.txt'
log_file_path = os.path.join(RUN_LOG_FOLDER, log_file_name)

log_file_handler = RotatingFileHandler(log_file_path, maxBytes=1024 * 1024, backupCount=0)  # backupCount=0 to keep only one log file
log_file_handler.setLevel(logging.DEBUG)

# Create a formatter for the file handler without including time
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%I-%M-%S%p %Y-%m-%d')
log_file_handler.setFormatter(file_formatter)

# Add the file handler to the logger
logger.addHandler(log_file_handler)

# Create a stream handler for console output
console_handler = StreamHandler()
console_handler.setLevel(logging.INFO)  # Adjust the level as needed

# Add the console handler to the logger
logger.addHandler(console_handler)


def decorate_log_record(record):
    timestamp = record.created
    human_readable_timestamp = datetime.utcfromtimestamp(timestamp).strftime('%I:%M:%S%p %Y-%m-%d %I:%M:%S%p')
    decorative_timestamp = f"\n{'*' * 30}\n{'*' * 4} Log generated from a program run at {human_readable_timestamp} {'*' * 4}\n{'*' * 30}\n"
    return decorative_timestamp + '\n\n \n'


class DecorativeTimestampFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.decorative_added = False

    def format(self, record):
        if not self.decorative_added:
            self.decorative_added = True
            return decorate_log_record(record) + super().format(record)
        else:
            return super().format(record)


decorative_formatter = DecorativeTimestampFormatter('%(asctime)s - %(levelname)s - %(message)s',
                                                    datefmt='%I:%M:%S%p %Y-%m-%d %I:%M:%S%p')

# Set the formatter for both handlers
log_file_handler.setFormatter(decorative_formatter)
console_handler.setFormatter(decorative_formatter)
