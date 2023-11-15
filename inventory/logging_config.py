
import logging
import datetime
import os

# Debugging
log_to_console = True # Prints logs to console if True

# Create 'logs' directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Generate a filename with a timestamp
filename = f"logs/logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

# Create a logging handler that writes log messages to a file
file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.INFO)

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a logging format
formatter = logging.Formatter('%(levelname)s: %(message)s')
file_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)

# If log_to_console is True, also log to console
if log_to_console:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
