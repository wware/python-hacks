# Python Software Testing for Great Justice!

We all want to write bug-free code that nobody ever complains about.
There are various ways to get closer to this goal. One of the most
effective is software tests.

* http://docs.python-guide.org/en/latest/writing/tests/

## How to think about testing

* Correctness
  - Tests prove that your code works as claimed.
  - Tests show how the code is to be used, what arguments to supply and
    what behavior or return values to expect back.
  - Tests ideally exercise every line of the code and every possible
    execution pathway thru the code.
    This is called [coverage](https://en.wikipedia.org/wiki/Code_coverage).
  - Trapeze artists always use safety nets. As a software engineer, tests are
    your safety net.
  - After your development work is done, your tests give notification if
    some other work somehow breaks your code. This is called
    [regression testing](https://en.wikipedia.org/wiki/Regression_testing).
  - Aim to write code that is easy to test - non-testable code is often bad code.
* Process stuff
  - Tests should run fast, so that you can conveniently re-run them constantly
    as you develop your code. You will never want to run slow tests, and the time
    spent on them will have been wasted.
  - Tests and code should be developed together. For each little piece of
    functionality, write a test that fails because the functional code isn’t
    written yet, then write code to satisfy the test. This is called
    [test-driven development](https://en.wikipedia.org/wiki/Test-driven_development). 
* Being a team player
  - The tests you write should be a help to whoever does QA on your code.

[Unit tests](https://en.wikipedia.org/wiki/Unit_testing) are for independently
testing something small in isolation (a class, a function, a module). Unit tests
should run very quickly, and you should  feel free to write LOTS of them.

Mocks are simplified models of the things you *_aren't_* testing right now:
other pieces of code, or databases, or network connections, often thing that
may be slow or unreliable.

[Functional](https://en.wikipedia.org/wiki/Functional_testing) and
[integration tests](https://en.wikipedia.org/wiki/Integration_testing) are
about testing  larger pieces of functionality spanning multiple classes or modules.

## The economics of software testing

You probably already know the  rationale for extensive developer testing, but to review,
bugs are cheaper to fix when they are caught earlier, and often the earliest quickest
way to catch them is while you are developing the code. Some bugs can be caught while
you're still just thinking about how to develop the code, but testing encourages good
habits in that phase as well.

You may be worried that writing tests will chew up valuable time in your schedule.
People who do a lot of testing find that overall, tests save time, because there
are far fewer unpleasant time-consuming surprises later on.

## Mocks

Mocks are an important enough topic to merit individual discussion. The idea
is that your code wants to interact with some entity that you don't want to
actually touch every time you're testing. It could be a production database
that should be left alone. It could be an unreliable network connection, and you
don't want your tests to suffer from that unreliability. It could be something
super slow, and you don't want slow tests. Anyway, it has some kind of interface,
and you want a "fake" version of it to talk to your test, instead of trying to
interact with the real one.

Mocks can be implemented with fixtures or with monkeypatch, or with the standard
mock module. If you're testing a class or module that ordinarily interacts with
others, those others can be mocked out, so that you're only testing your own code.
In cases where reliability  can be an issue, write tests to exercise the
possible failures: timeouts, dropped connections, missing DB table rows, etc.

Mocks are related to a testing pattern called
[dependency injection](https://en.wikipedia.org/wiki/Dependency_injection).

# Py.test

The py.test framework is very cool and has more or less won the competition for
best possible Python test framework.

There are [thorough docs](http://pytest.org/latest/contents.html).
One of the most powerful things about py.test is [fixtures](http://pytest.org/latest/fixture.html).
Mocking is done with [monkeypatch](http://pytest.org/latest/monkeypatch.html)
(but you can still use the `mock` module if you want). Installation is easy:


## Test discovery

Py.test will look for tests in modules, files, or functions whose names start with
`test_`, and in classes whose names start with `Test`, where the tests are methods
whose names start with `test_`. Packages that include tests should always have a
`__init__.py` file at each directory level.

## Command line options

When a test fails, py.test can pop you into a debugger with the `--pdb` command line option.
For extra special cleverness points, put asserts in your functional code, then run
`pytest --pdb` to pop  into the debugger immediately after a fault is detected to query
the variables.

You can include doctests with the normal tests using the `--doctest-modules` option.

You can select tests within a file or module using `-k`, for instance

    py.test foo/bar/test_baz.py -k test_specific_1

which would run only `test_specific_1` in the `test_baz.py` file, ignoring `test_specific_2`
or any other tests in the same file. It is frequently useful to select a single test and run
it repeatedly while working on the code that it tests.

You can check the coverage of your tests using
[pytest-cov](https://pytest-cov.readthedocs.org/en/latest/),
First pip-install `pytest-cov` and then using the `--cov` command line option. There are some
[useful variations](https://pytest-cov.readthedocs.org/en/latest/readme.html#usage)
of this option that you can read about.
