import logging
import os
import sys

_local_ip = None
_host_getter = None
_host_ip = None
_loggers = {}


def setup_comms(local_if, get_host):
    global _host_getter, _local_ip
    _loggers.clear()
    if sys.platform == 'cygwin':
        # how to use the local_if here??
        cmd = 'ipconfig | grep IPv4 | sed "s/.*: //"'
    else:
        cmd = (
            'ifconfig ' + local_if + ' | grep "inet addr:.*Bcast" | ' +
            'sed "s/.*addr://" | sed "s/ .*//"'
        )
    _local_ip = os.popen(cmd).readline().strip()
    logging.info((local_if, _local_ip, get_host))
    _host_getter = get_host


def get_host_ip():
    global _host_ip
    if _host_ip is None:
        if _host_getter is None:
            return
        _host_ip = _host_getter()
    return _host_ip
