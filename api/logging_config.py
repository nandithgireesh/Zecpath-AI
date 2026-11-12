import logging
import os


def setup_logging():

    log_folder = "data/logs"

    os.makedirs(
        log_folder,
        exist_ok=True,
    )

    log_file = os.path.join(
        log_folder,
        "ats.log",
    )

    logging.basicConfig(
        level=logging.INFO,
        format=("%(asctime)s | " "%(levelname)s | " "%(name)s | " "%(message)s"),
        handlers=[
            logging.FileHandler(
                log_file,
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
    )
