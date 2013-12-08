import logging
import logging.handlers
import sys

def init_logger(flushlevel, logfile=None):
    """
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if not logfile is None:
        logstream = logging.StreamHandler(stream=sys.stdout)
        logstream.setFormatter(formatter)
    else:
        logstream = logging.FileHandler(logfile)
        logstream.setFormatter(formatter)

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

    mem = logging.handlers.MemoryHandler(1024*10, flushlvl, target=logstream)
    logger.addHandler(mem)
