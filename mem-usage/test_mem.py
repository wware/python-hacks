#!/usr/bin/env python

import logging
import gc
from mem import memory_usage, all_info

logging.basicConfig(
    format='%(asctime)-15s  %(levelname)s  %(filename)s:%(lineno)d  %(message)s',
    level=logging.DEBUG,
)


def make_big_list():
    x = [1.0]
    for i in range(6):
        y = []
        for _ in xrange(10):
            y.extend(x)
        x = y
    return x

# http://stackoverflow.com/questions/23369937

"""
Long running Python jobs that consume a lot of memory while
running may not return that memory to the operating system
until the process actually terminates, even if everything
is garbage collected properly.

The solution I need for my problem is that FOR EACH PIECE,
I'll need to spawn a new process AND TERMINATE THAT PROCESS
when its work is done. I think that's the only way out of this
morass.
"""


def main():
    for _ in xrange(5):
        logging.debug(memory_usage())
        logging.debug(all_info(gc.get_objects()))
        x = make_big_list()
        logging.debug(memory_usage())
        logging.debug(all_info(gc.get_objects()))
        del x
        logging.debug(memory_usage())
        logging.debug(all_info(gc.get_objects()))

if __name__ == "__main__":
    main()
