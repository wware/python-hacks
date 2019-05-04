# https://medium.freecodecamp.org/hacking-together-a-simple-graphical-python-debugger-efe7e6b1f9a8

import sys

def sample(a, b):
    x = a + b
    y = x * 2
    print('Sample: ' + str(y))

def tracefunc(frame, event, arg):
    if frame.f_code.co_name == "sample":
        print((frame.f_lineno, frame.f_code, event))
    return tracefunc

sys.settrace(tracefunc)

sample(3, 4)
