import logging

logging.basicConfig(
    filename="ai.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

logger.info("Zecpath AI Started")