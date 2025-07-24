import logging

# Configure logger
logging.basicConfig(
    level=logging.INFO,  # INFO, DEBUG, ERROR, etc.
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
