import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a rotating file handler, with a new file created at midnight and kept for 7 days
log_file_handler = RotatingFileHandler('atm_log.txt', maxBytes=1024 * 1024, backupCount=7)
log_file_handler.setLevel(logging.DEBUG)

# Create a formatter for the file handler
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S\n')
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
    decorative_timestamp = f"\n{'*' * 30}\n{'*' * 4} Log generated from a program run at {timestamp} {'*' * 4}\n{'*' * 30}\n"
    return decorative_timestamp


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
                                                    datefmt='%Y-%m-%d %H:%M:%S')

# Set the formatter for both handlers
log_file_handler.setFormatter(decorative_formatter)
console_handler.setFormatter(decorative_formatter)

