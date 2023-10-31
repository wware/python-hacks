# Tail recursion

Let's start out by describing mathematical induction.

* If `n` is an integer, then `n + 1` is also an integer.
* Zero is an integer.

From this it follows that numbers like `1234321` are also integers
because you could arrive at them just by repetitively applying the two
rules above.

The first rule lets you simplify a problem a little bit. We can say that
`1234321` is an integer if we can show that `1234320` is an integer. We
can use that first rule to work backwards all the way to "...if we can
show that `0` is an integer", and then we invoke the second rule. So now
all of those numbers are integers.

One rule tells you how to go, another tells you when you can stop. Now
let's apply this to Python functions.

Recursion is when a function calls itself. Here is a simple example.

```python
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)
```

The `n == 0` case tells us when we can stop. The other case tells us how
to move forward.

But there's a problem. Let's suppose `n` is huge. We'll get an out-of-memory
problem. Each step requires a stack frame. Stack frames consume memory.
Tail recursion is how you handle huge `n` without using a huge number of
stack frames.

We need to refactor it a bit. It will look more like this. We need to get
rid of the `n *` outside the recursive call.

```python
def factorial(n, prod=1):
    if n == 0:
        return prod
    else:
        return factorial(n - 1, n * prod)
```

The way to keep re-using the same stack frame is to make the recursion
step look just like the function call, and just change the arguments.

If Python natively supported tail recursion, we'd be done. It would
recognize what we're trying to do, and handle the change of arguments.
Alas, Python doesn't, but adding it to the language is pretty easy.

How has this not made it into a Python standard library by now? A few
people have proposed pretty simple ways to acccomplish this in Python.

* [Blog post](https://chrispenner.ca/posts/python-tail-recursion)
* [ActiveState](https://code.activestate.com/recipes/474088-tail-call-optimization-decorator/)

The big surprise for me was HOW FAST these things are as tail recursions!
