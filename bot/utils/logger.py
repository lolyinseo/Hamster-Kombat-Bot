import sys
from loguru import logger as base_logger


def setup_logger():
    base_logger.remove()
    base_logger.add(
        sink=sys.stdout,
        format="<white>{time:YYYY-MM-DD HH:mm:ss}</white>"
               " | <level>{level: <8}</level>"
               " | <cyan><b>{line}</b></cyan>"
               " - <white><b>{message}</b></white>"
    )
    return base_logger.opt(colors=True)


logger = setup_logger()
