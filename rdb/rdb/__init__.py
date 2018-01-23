import logging

from .dlog import DistributedHandler, extendLogger
from .comms import _loggers


def getLogger(name=''):
    logger = _loggers.get(name)
    if logger is not None:
        return logger
    # stifle almost all logging from werkzeug
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    logger = logging.getLogger(name)
    logger.addHandler(DistributedHandler())
    extendLogger(logger)
    _loggers[name] = logger
    return logger
