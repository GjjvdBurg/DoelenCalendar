import logging
import logging.handlers
import sys

def init_logger(flushlevel):
    """
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream = logging.StreamHandler(stream=sys.stderr)
    stream.setFormatter(formatter)

    if flushlevel == 'INFO':
        flushlvl = logging.INFO
    elif flushlevel == 'DEBUG':
        flushlvl = logging.DEBUG
    elif flushlevel == 'WARNING':
        flushlvl = logging.WARNING
    elif flushlevel == 'ERROR':
        flushlvl = logging.ERROR
    elif flushlevel == 'CRITICAL':
        flushlvl = logging.CRITICAL

    mem = logging.handlers.MemoryHandler(1024*10, flushlvl, target=stream)
    logger.addHandler(mem)
