# Literate Programming hacks

Let's try some literate programming. From Don Knuth's original idea, thru
Norman Ramsey's noweb reformulation, by way of Jonathan Aquino's Python
version, which I tweaked to accept Markdown input.

```shell
mdweb.py -R 'outer function' mdweb.md | python
```

prints

```text
Hello world
25
Have a good day
```

## A simple python example

### *inner function*

I know this is a chunk that should be included in processing because
the section title is in italics (a "*" character in Markdown source).

This function will later be called by the `_outer` function below.

```python
def _inner(x):
    print(x)
```

When we import a code chunk with indentation, that indentation is
applied to the imported chunk. Adding a little more to the `_inner`
function to demonstrate this:

```python
    #*inner inner function*#
    pr_square(5)
    print("Have a good day")
```

### *inner inner function*

```python
def pr_square(x):
    print(x**2)
```

### this is not a chunk

We can throw in examples that aren't chunks and they don't get
processed in any way.

```python
def pr_cube(x):
    print(x**3)
```

### *outer function*

```python
#*inner function*#

def _outer(x):
    _inner(x)

_outer("Hello world")
```

## Hacking prolog

People have put a lot of work into Prolog. There must be something to it. I
know Ross King used it in his "robot scientist" project. It seems to be an
ideal computational environment for exercises in first-order logic.

* [Prolog (wikipedia)](https://en.wikipedia.org/wiki/Prolog)
* [Prolog quickstart](https://www.swi-prolog.org/pldoc/man?section=quickstart)

To exercise some of the stuff below, you can run the "root" chunk below
by typing

```bash
mdweb.py -R root mdweb.md | bash
```

### *root*

```bash
mdweb.py -R 'try some prolog' mdweb.md > foo.pl
# enumerate solutions non-interactively
swipl -f foo.pl -g "forall((Goal=sibling(X,Y),call(Goal)),(write(Goal),nl))." -t halt.
```

### *try some prolog*

```prolog
mother_child(trude, sally).

father_child(tom, sally).
father_child(tom, erica).
father_child(mike, tom).

sibling(X, Y) :- parent_child(Z, X), parent_child(Z, Y), X \= Y.
parent_child(X, Y) :- father_child(X, Y).
parent_child(X, Y) :- mother_child(X, Y).
```

### *Quicksort in Prolog*

```prolog
partition([], _, [], []).
partition([X|Xs], Pivot, Smalls, Bigs) :-
    (   X @< Pivot ->
        Smalls = [X|Rest],
        partition(Xs, Pivot, Rest, Bigs)
    ;   Bigs = [X|Rest],
        partition(Xs, Pivot, Smalls, Rest)
    ).

quicksort([])     --> [].
quicksort([X|Xs]) -->
    { partition(Xs, X, Smaller, Bigger) },
    quicksort(Smaller), [X], quicksort(Bigger).
```
