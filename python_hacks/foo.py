# https://medium.freecodecamp.org/hacking-together-a-simple-graphical-python-debugger-efe7e6b1f9a8

def example(a, b):
    x = a + b
    y = x * 2
    print 'Result is {0}'.format(y)

#########

# import dis
# dis.dis(example)

#########

interesting_fcode = None

def tracefunc(frame, event, _):
    global interesting_fcode
    fc = frame.f_code
    if interesting_fcode is None and fc.co_name == "example":
        interesting_fcode = fc
        print frame, [x for x in dir(frame) if not x.startswith("_")]
    if fc is interesting_fcode:
        print((frame.f_lineno, frame.f_lasti, event))
    return tracefunc

# import sys
# sys.settrace(tracefunc)

example(3, 4)
