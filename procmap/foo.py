# We're gonna make a list with a map method, which forks processes
# and then sends back results as JSON. Each process starts as a copy
# of everything in the original process. Then I need an IPC hack to
# get the result back to the parent process, let's use mp.Queue.

import time
import pprint
import multiprocessing

N = 100
lst = list(range(N))


def f(q, n):
    value = [9] * ((n % 8) + 3)
    result = {n: value}
    time.sleep(1)
    q.put(result)


def map(func, somelist):
    q = multiprocessing.Queue()

    procs = []
    for x in somelist:
        p = multiprocessing.Process(target=func, args=(q, x))
        procs.append(p)
        p.start()

    for p in procs:
        p.join()

    d = {}
    while not q.empty():
        d.update(q.get())
    pprint.pprint(d)


map(f, lst)
