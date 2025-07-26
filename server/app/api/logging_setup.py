import logging
import logging.handlers

# Centralized logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler = logging.handlers.RotatingFileHandler(
    'plant_info.log', maxBytes=1_000_000, backupCount=3
)
file_handler.setFormatter(
    logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
)

root_logger = logging.getLogger()
root_logger.addHandler(file_handler)

# Optionally adjust third-party loggers if too verbose
# logging.getLogger('httpx').setLevel(logging.WARNING)

# Helper

def redact_sensitive(text: str) -> str:
    from config import Config
    return text.replace(Config.PLANTNET_KEY, "<api-key>")
