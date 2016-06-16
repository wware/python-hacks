import httplib
import logging
import os
import sys
import threading
import urllib
import remote_pdb

import comms


def inform(host_ip, port):
    try:
        params = urllib.urlencode(
            {'ipaddr': comms._local_ip, 'port': port}
        )
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        conn = httplib.HTTPConnection(host_ip + ':5000')
        conn.request("POST", "/rdb", params, headers)
        conn.getresponse()
        conn.close()
    except Exception as e:
        logging.exception(e)



class RemotePdb(remote_pdb.RemotePdb):
    def __init__(self, port=4444):
        host_ip = comms.get_host_ip()
        inform(host_ip, port)
        remote_pdb.RemotePdb.__init__(self, '0.0.0.0', port, False)

    # Be able to run shell commands
    def do_sh(self, *args):
        cmd = ' '.join(args)
        print >>self.stdout, os.popen(cmd).read().rstrip()
