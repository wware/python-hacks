import logging

from .rpdb import RemotePdb
from .dlog import DistributedHandler, extendLogger
from .digger import dig
from .comms import setup_comms, _loggers


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
