# nearly-functional-python

This repository contains some ideas to make Python as nearly FP as possible, with some example code.

## History and motivation

The academic stuff

* [Lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus)
  invented by Alonzo Church in 1936
* [Turing machines](https://en.wikipedia.org/wiki/Turing_machine)
  invented by Alan Turing around the same time
* The [Church-Turing thesis](https://en.wikipedia.org/wiki/Church%E2%80%93Turing_thesis)
  states that these are equivalent, what we now call
  ["Turing complete"](https://en.wikipedia.org/wiki/Turing_completeness)
* Haskell Curry observes a
  similarity between computer programs and mathematical proofs, and
  formalizes it as the
  [Curry-Howard correspondence](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence),
  advancing the field of
  [formal verification](https://en.wikipedia.org/wiki/Formal_verification)
* [Coq](https://coq.inria.fr/) is a software proof assistant. It has a nice little
  [tutorial](https://michaeldnahas.com/doc/nahas_tutorial).

The programming stuff

* [Lisp](https://en.wikipedia.org/wiki/Lisp_(programming_language))
  developed at MIT in 1958
* [Standard ML](https://en.wikipedia.org/wiki/Standard_ML) developed in 1983
* [OCaml](https://en.wikipedia.org/wiki/OCaml)
* [Haskell](https://en.wikipedia.org/wiki/Haskell) - probably the deepest
  academically
* [F#](https://en.wikipedia.org/wiki/F_Sharp_(programming_language)) - roughly
  OCaml for the .NET world
* [Rust](https://en.wikipedia.org/wiki/Rust_(programming_language))

### Motivation

Why am I interested in FP for Python? Because I work on a very big, very ugly
legacy system written in Python 2.7. I've moved part of the system to Python 3,
which is great. But the more I read about FP and its benefits, and see them
confirmed in my own experience, the better I feel about FP.

As engineers, we all want to write clean correct code that doesn't smell bad.
We all want to build reliable systems that don't crash frequently. FP is a
powerful set of tools to assist in that goal.

### FP advocacy

[Michael Clarkson](https://www.engineering.cornell.edu/faculty-directory/michael-clarkson)
is a brilliant OCaml guy at Cornell
([textbook](https://cs3110.github.io/textbook/cover.html),
[videos](https://www.youtube.com/@MichaelRyanClarkson/videos))
who has done a lot of advocacy for FP. He is deeply rooted in its theory,
history and underpinnings, but has a very sensible rounded view of it.
He is versed in the theory without getting lost in it. He understands why it's
important to write bullet-proof code in a world that needs a lot more
bullet-proof code. He's smart and articulate and a good writer and those
videos represent a ton of work. In addition to the Cornell OCaml course
he has also worked on theorem provers, formally provable software correctness,
[Coq](https://coq.inria.fr/), all that good stuff that historically set
the direction for FP.

## Principles of functional programming

### Functions as first-class objects

This is a feature already baked into Python. Once defined, a function may be assigned to
a variable or passed to another function as an argument.

This has a number of implications. There are
[libraries](https://docs.python.org/3/library/functional.html)
for making use of them.

### Immutable data

The idea here is that once first assigned, a "variable" should be treated as a constant.
It should never be reassigned for the entire time it remains in scope.

In Python, this property is frequently referred to as "frozen", and various resources
provide this. For instance, instead of dicts, lists, and sets, you can use
[frozendict](https://pypi.org/project/frozendict/),
[frozenlist](https://pypi.org/project/frozenlist/), and
[frozenset](https://docs.python.org/3/library/stdtypes.html?highlight=frozenset#frozenset).

Both
[pydantic models](https://docs.pydantic.dev/latest/concepts/models/) and
[dataclasses](https://docs.python.org/3/library/dataclasses.html) can be frozen.

<!-- Maybe write a
[pylint checker](https://pylint.pycqa.org/en/latest/development_guide/how_tos/custom_checkers.html#write-a-checker)
that detects variable reassignment?? -->

### Typing

[Here is some advice](https://github.com/microsoft/pyright/blob/main/docs/getting-started.md) on how to update
legacy code with typing hints.

Use lots of [type hints](https://docs.python.org/3/library/typing.html) with
["mypy –strict"](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html),
flake8, and [pyright](https://github.com/microsoft/pyright) for linting and to approximate static typing. Another great linter is [ruff](https://github.com/astral-sh/ruff).

[Algebraic data types](https://stackoverflow.com/questions/16258553)

#### Pattern matching

This has been
[available in Python](https://peps.python.org/pep-0636/)
since version 3.10
([1](https://www.infoworld.com/article/3609208/how-to-use-structural-pattern-matching-in-python.html),
 [2](https://benhoyt.com/writings/python-pattern-matching/)).
Pattern matching may look like just a switch statement, and goodness knows that's long overdue
in Python. But it's more. In Python it's called *structural* pattern matching because it can
match a data structure or class instance as well as a primitive value, and then internals of
the structure become available in that case. Here's an example.

```python
@dataclass
class Point:
    x: int
    y: int

points = ...something...

match points:
    case []:
        print("No points")
    case [Point(0, 0)]:
        print("The origin")
    case [Point(x, y)]:
        print(f"Single point {x}, {y}")    # using x and y
    case [Point(0, y1), Point(0, y2)]:
        print(f"Two on the Y axis at {y1}, {y2}")
    case _:
        print("Something else")
```

### Iterators and lazy evaluation

When I first started hearing about iterators, it was as a trick to conserve memory: a way to
iterate thru a sequence of values without keeping all the values in memory, for instance in
a list. This is done by maintaining enough state to generate the sequence.

Iterators can be faster than stepping thru a list or other data structure. They can also
enable computations that aren't practical because the list would consume too much memory.

* A [Pycon talk](https://pycon2019.trey.io/iterator-protocol.html) about iterators and lazy evaluation.
* [Why it's useful](https://stackoverflow.com/questions/265392/why-is-lazy-evaluation-useful)

[Example from the `itertools` docs](https://docs.python.org/3/library/itertools.html):

```python
from itertools import *

def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(
        islice(iterable, n, None),
        default
    )

c = count(1)
nth(c, 999)   ==> 1000
```

Haskell also has iterators. Infinite lists are possible because of lazy evaluation: Haskell
only evaluates things when it needs to. So you can ask for the 1000th element of a list and
Haskell will oblige. The syntax is more concise than Python.

```haskell
[1..] !! 999            -- 1000
```

#### Filtering an infinite iterator

We can filter an iterator before applying a very laborious operation, and thereby avoid
doing that computation on elements that we don't care about.

```python
from itertools import *

c = count(1)    # this is an infinite iterator

def divisible_by_100(n):
    return (n % 100) == 0

def very_laborious_computation(n):
    return n + 1

it1 = filter(divisible_by_100, c)
it2 = map(very_laborious_computation, it1)
# it2 is still infinite...

for x in islice(it2, 4):
    print(x)
# 101
# 201
# 301
# 401
```

### [Generators](https://en.wikipedia.org/wiki/Generator_(computer_programming))

Python uses the word "generator" to mean "intentionally constructed iterator".
Nothing very tricky here, not a lot of new content beyond the earlier section
on iterators.

The simplest way to create a generator is using a comprehension.

```python
g = (i for i in range(1000))
next(g)   # 0
next(g)   # 1
```

The next simplest thing is to write a function using `yield`.

```python
def make_gen():
    for i in range(1000):
        yield i

g = make_gen()
next(g)   # 0
next(g)   # 1
```

Finally, you can write a generator class.

```python
class Fib:
    def __init__(self):
        self.a, self.b = 0, 1

    def __iter__(self):
        return self

    def __next__(self):
        return_value = self.a
        self.a, self.b = self.b, self.a+self.b
        return return_value

f = Fib()
for i in range(3):
    print(next(f))     # 0, 0, 1
```

### [Closures](https://en.wikipedia.org/wiki/Closure_(computer_programming))

The idea here is to "bury" some state so that it can inform a function but not
be easily modified from the outside. Here are two ways to create a counter.

```python
# as a generator
def make_counter_1():
    count = 0
    while True:
        count += 1
        yield count

c = make_counter_1()
next(c)   # 1
next(c)   # 2
```

This is just like the generators in the previous section. Arguably there is
"buried state" here, in the form of the `counter` variable.

```python
# as a function created with a closure
def make_counter_2():
    count = 0
    def counter():
        nonlocal count
        count += 1
        return count
    return counter

c = make_counter_2()
c()   # 1
c()   # 2
```

In the second case, the "buried state" is again the `counter` variable. But
we could have defined multiple functions that access `counter` in different
ways and interact with one another. For instance, we could have defined a
variable for an account balance, and created functions for `deposit` and
`withdraw`. We'd need to think about thread safety. It allows communication
between these different functions.

### Memoization

If you agree not to use side effects, and let a function's return value depend
only upon its arguments, then you can save up past results in a dictionary so
that if you see them again, you alread have an answer. You burn some memory
to save potentially a ton of time that would be spent re-computing the result.

This is such a useful thing that, before Python 3, I had rolled my own Python 2
implementation. But in Python 3, it's in the standard libraries.

Remember you may want to put a bound on the size of the cache.

#### cache

This decorator uses an unbounded cache. Use with caution.

```python
from functools import cache

@cache
def factorial(n):
    return n * factorial(n-1) if n else 1

>>> factorial(10)      # no previously cached result, makes 11 recursive calls
3628800
>>> factorial(5)       # just looks up cached value result
120
>>> factorial(12)      # makes two new recursive calls, the other 10 are cached
479001600
```

#### Least-recently-used cache

Here we have a `maxsize` argument (the number of elements) to put an upper bound on the
size of the cache.

```python
from functools import cache

@lru_cache(maxsize=32)
def factorial(n):
    return n * factorial(n-1) if n else 1
```

### Monads???

People do write monads in Python ([1][monad1], [2][monad2]).
I'm just not sure how useful they are.
I probably need to learn more about them.

Somebody somewhere wrote:

> Monads are a way of structuring code that can be used to implement many of the other functional programming idioms. They are a powerful tool that can be used to make code more concise, elegant, and correct.

My impression is that the purpose of a monad is to enable an otherwise "pure" value
(something simple like an integer or a string) to carry some additional "metadata" a bit
like `NaN` or `None` in an otherwise un-nullable value, or some diagnostics, or even to
do something non-functional like write to a log file under some circumstance. And then
you have machinery that allows you to somehow pass this monad into functions written for
the pure value, without breaking everything.

#### "Maybe" monad

The monad itself is defined in [the article on Medium][monad1]. The usages give the idea
of whether it's useful. What the monad allows us to do is to chain function calls, while
letting a bogus result pass thru without breaking the pipeline.

```python
def add_one(x):
    return x + 1

def double(x):
    return x * 2

result = Maybe(3).bind(add_one).bind(double)
print(result)  # Just 8

result = Maybe(None).bind(add_one).bind(double)
print(result)  # Nothing

result = Maybe(None).bind(add_one).bind(double).orElse(10)
print(result)  # Just 10

result = Maybe(None) | Maybe(1)
print(result) # Just 1
```

[monad1]: https://medium.com/@hk151817/mastering-pythons-hidden-power-monad-design-patterns-for-smarter-code-123e509553d1
[monad2]: https://medium.com/swlh/more-monads-in-python-178492f482f6

## FP topics that don't make sense for python

### [Currying](http://learnyouahaskell.com/higher-order-functions)

The idea here is that each function actually only takes one argument, and
any function that appears to take more than one is actually constructed
from a chain of single-argument functions. This sticks closer to the ideas
from formal lambda calculus, and does have some interesting and useful
consequences. Python doesn't work this way, but it includes
[partial application](https://docs.python.org/3/library/functools.html#functools\.partial),
one of those consequences.

### [Tail recursion](https://wiki.haskell.org/Tail_recursion)

This is a hack for accomplishing something like a for-loop when you don't
have variables that can be reassigned. It's a form of recursion that doesn't
consume additional stack space. Again, academically interesting, and
[it can be done in Python](https://pypi.org/project/tail-recursive/),
but it's not idiomatic or terribly useful. You're allowed mutable variables
in Python, just use them sparingly.

An example of tail recursion would look like this. Notice that `helper`
makes a call to itself in its last line, with only a change in the value
of the arguments. At run-time, Python can re-use the same stack frame, just
plugging those new values into the argument slots. Voila, instant for-loop.

```python
def factorial(n):
    def helper(product, n):
        if n < 2:
            return product
        else:
            return helper(product * n, n - 1)
    return helper(1, n)
```

### Recusion in general

My personal opinion is that recursion is usually not a great idea. If you
need a for-loop, just go ahead and use a mutable counter variable.

If you have some exotic situation where recursion makes the code a lot more
readable, use recursion, but remember that it can chew up stack space in a
big hurry.
