# Functional Programming

The idea here is to make your code look like a collection of
mathematical functions.

* Functions lack state or history. Given the same inputs, they always produce
  the same output. The cosine of 90 degrees is always zero.
* Functions have no side effects. When you take the cosine of 90 degrees, it
  has no effect on the outputs of the sine or tangent functions.
* Functions are unaffected by external events. The cosine does not depend on
  the weather, or the room temperature, or the exchange rate of any currency.

Another closely related thing is immutable data. When you assign a variable,
its value should not change as long as the variable remains in scope. Any access
to the variable, for instance the 3rd element of a list or tuple, or any
attribute of a class instance, or any value in a dictionary or set, should
remain invariant as long as the variable is still valid.

These principles of math-like function on the one hand, and immutable data on
the other, vastly reduce the possibility of bugs in your code. They also make
the code much easier to test because you don't need tests to handle the cases
where you would have seen things change.

For the values of variables to be immutable, we must not change those values
once the variables are initially assigned. The arguments to the function should
never be changed inside the function. Variables defined in the body of the
function should not be changed after their first assignment.

    def f(x, y, z):
        u = 1
        v = 2
        w = 3   # okay so far
        z = g(u, v, w)     # -- BAD -- because we are changing z, an argument
        print(u + v)       # this is okay, it won't change anything
        v += 1     # -- BAD -- do not change v here
        return u * v * w

There are other ways variables can be created or initially defined, such as by
a for loop or an enumerate.

    def f(some_list_of_things):
        for i, x in enumerate(some_list_of_things):
            do stuff with i
            do stuff with x
            but do not change either of them
        return whatever

This is okay.

## Testable internal stuff

    def f(x, y, z):
        def g(u, v, w):
            do stuff
            return something
        do more stuff
        use g for something
        return whatever

The function f is accessible but the function g, defined inside f, is not
accessible. You can't test something you can't access. So move the definition
of g outside f, enabling g to be tested.

You can test a method of a class, and even of a class defined inside a class,
like this.

    class Foo(object):
        class Bar(object):
            def mymethod(self, x, y):
                return whatever

This is a handy way to make functions relatively private but still available for
testing. Simply write a test that refers to `Foo.Bar.mymethod`. The method isn't
prominently taking up public namespace but it's rechable when you need it.
