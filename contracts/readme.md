# Messing about with DbC in Python

There is a huge amount of very shallow tutorial material on the web and
on Youtube, explaining over and over the same few basic ideas. But there
is also the impression I get that there really is some importance to DbC
and there must be something more interesting and useful.

I think the thing to do is to choose a big project and use a LOT of
DbC, and see if it solves a lot of problems. Let's do this with a
project I'm going to do anyway, so I don't have to contrive some
purely hypothetical project that I don't really care about.

I theorize that even a non-programmer can understand the basics of DbC
in ten minutes or less. Tell them that *this is a function*

    def some_function(variable1, variable2, variable3):
        do some stuff
        return something

and explain things that should make sense:

* Arguments and return values can have different types (ints, strings,
  objects, other functions, etc)
* All software is just big complex collections of functions (elide
  nuances like state, classes, side effects)
* Programmers' assumptions are almost never recorded accurately or
  communicated effectively
* Traditional QA (boxes running tests) is expensive and is not
  guaranteed to catch all bugs

Now introduce DbC:

* Each function has assumptions specified as preconditions and
  postconditions and invariants
* All these assumptions are tested on every function call all the
  time (unless switched off for performance)
* Any failed assumption shuts down the whole operation and provides
  information to minimize the search space for the bug

Where functions are huge, try to refactor them into smaller pieces.
Even just identifying types without additional constraints will be a win.

DbC is a sort of unit test that runs whenever the code is executed.
Unlike mocks, they do not hinder refactoring.

At the same time it addresses Knuth's intent with literature programming
of preventing divergence of code and docs by keeping both in the same
source file, and executing them together frequently.

You should use DbC wherever you can, minimally to identify the types of
arguments. You can add more constraints later. Write predicates for the
states of things like "this file object hasn't yet been closed".
