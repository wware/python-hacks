# Revelations from PyCon 2019

A guy named Luciano <Something> talked about sets in Python and how they
represented a well-designed API worthy of study. Some things I did not know
about sets:

   a < b     means set a is a proper subset of set b
   a <= b    means a is an improper subset: either a subset, or equal to, B

## Book recommendations

- Fluent Python, by Luciano himself
- The Go Programming Language, Donovan and Kernighan

## ABCs as interfaces

collections.abc is a way to specify an interface for a class (in the Java
sense of "interface")

- https://pymotw.com/2/abc/
- https://docs.python.org/2/library/abc.html
- https://docs.python.org/3/library/collections.abc.html (Python 3)

The PyMOTW page gives a good description of how ABCs work. It is really not
very tricky.

Another thing is asyncio and "await". Oh wait, asyncio is a Python 3 thing.

## API Evolution

Then there was a talk about how to evolve an API over time without placing
an unreasonable maintenance burden on people using your library. This is also
available online:
https://emptysqua.re/blog/api-evolution-the-right-way/

## Solvers

You can use collections.deque to implement both breadth-first and depth-first
searches.
https://jeremykun.com/2013/01/22/depth-and-breadth-first-search/
(not the guy who gave the talk on solvers)

SAT solvers operate by looking at all possible combinations of a set of
boolean variables to see which combinations satisfy some boolean expression.
This would not be too interesting except that tricky ways have been found to
write SAT solvers that do not require exhaustive search so you can have vast
numbers of boolean variables. I am not familiar with the body of theory involved.

An example of such a SAT solver is "pycosat".
https://github.com/ContinuumIO/pycosat
That is actually just a Python wrapper for a SAT solver written in C.
http://fmv.jku.at/picosat/

Reinforcement learning is a powerful thing. It turns out you can write a program
that learns to beat people at Rock-Paper-Scissors because people are not
perfectly random, they have "styles" of play that can be learned.

## Using Bdb to write customized debuggers for Python

sys.settrace

https://docs.python.org/2.7/library/bdb.html
https://docs.python.org/2.7/library/sys.html#sys.settrace


