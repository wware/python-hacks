# Contractual functions in Python

People call this "design by contract". The easily google-able info
about it is pretty shallow, unfortunately. But I think there is
something worthwhile there. See `tryit.py` in this directory for
the general idea.

If you want to disable the contract stuff and get back any performance
hit it might have caused, run the code with `python -O` instead of
`python`, which will turn off the `__debug__` flag.

## Why do this?

Programmers' assumptions are almost never recorded accurately or
communicated effectively. With contracts, we get:

* Each function has assumptions specified as pre-conditions and
  post-conditions and invariants.
* All these assumptions are tested on every function call all the
  time, unless switched off for performance.
* Any failed assumption provides information to minimize the
  search space for the bug.

If a post-condition fails after the pre-conditions passed, then the
function is at fault. If a pre-condition fails, then the code that
calls the function is at fault. If an invariant changes, at least you
know where to start looking.

You can mix contractual and non-contractual functions, so you don't
need to upgrade all your code before you can benefit.