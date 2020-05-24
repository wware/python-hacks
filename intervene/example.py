import json
import logging
import os
import sys
import yaml

import elsewhere


def debuggable(options, where, globals):
    """
    out-of-band:
        # example usage
        debug: preflight
        target: /path/to/some/pythonfile.py
    """
    from importlib import import_module
    oob = None
    try:
        assert isinstance(where, (str, unicode))
        oob = json.loads(options.out_of_band)
        L = oob.get('debug', None)
        assert L is not None
        if isinstance(L, list):
            assert where in L
        else:
            assert where == L, (where, L)
        target = oob.get('target', None)
        sys.path.insert(0, os.path.realpath(os.path.dirname(target)))
        module = import_module(
            os.path.basename(target).replace(".py", "")
        )
        sys.path.pop(0)
        getattr(module, 'main')(globals)
    except Exception as e:
        logging.exception(e)
        if isinstance(oob, dict) and oob.get('debug', None) is not None:
            logging.error("DEBUGGABLE??? {0}".format((where, options.out_of_band)))


print "BEFORE"
print elsewhere.MyClass().mymethod(3, 4)


class ArgparseMock(object):
    pass

options = ArgparseMock()
options.out_of_band = '{"debug": "preflight", "target": "./intervene.py"}'
debuggable(options, "preflight", globals())

print "\nAFTER"
print elsewhere.MyClass().mymethod(3, 4)
