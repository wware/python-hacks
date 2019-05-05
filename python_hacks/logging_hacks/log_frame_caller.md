# Log frame caller

Sometimes you want a Python function that includes a `logging.info()` or `logging.debug()` call, but you'd
really prefer the logged filename and line number to be from the caller of your function, not your function
itself. This is the solution to that problem, at least for Python 2.7. Also see
https://stackoverflow.com/questions/12980512/custom-logger-class-and-correct-line-number-function-name-in-log/47215183
