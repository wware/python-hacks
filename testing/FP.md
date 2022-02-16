# Functional Programming

The idea here is to make your code look like a collection of
mathematical functions.

* Functions lack state or history. Given the same inputs, they always produce
  the same output. The cosine of 90 degrees is always zero.
* Functions have no side effects. When you take the cosine of 90 degrees, it
  has no effect on the outputs of the sine or tangent functions.
* Functions are unaffected by external events. The cosine does not depend on
  the weather, or the room temperature, or the exchange rate of any currency.

One way to support this functional programming style is to stay as close as
possible to the principle of immutable data. Once a variable is created and
given its initial value, it should ideally never be changed as long as the
variable remains in scope. Then you can more easily reason about what the
code is doing.

Many languages provide support for keeping data immutable. It is not generally
enforced but it's made easy, and where a variable is reassigned there is often
some syntactic convention to make that evident. You'll see this in Clojure and
I believe Rust.

For non-primitive data types, Python provides tuples, frozen sets, and frozen
dicts, which prevent reassignment of internals. It's also possible to use a
namedtuple to provide immutable attributes for a sort of frozen class.

    from collections import namedtuple
    
    class Vector(namedtuple("V", "x y z")):
        def len(self):
            return self.inner(self) ** .5
    
        def inner(self, w):
            assert isinstance(w, Vector)
            return self.x*w.x + self.y*w.y + self.z*w.z
    
        def scale(self, k):
            return Vector(k*self.x, k*self.y, k*self.z)

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
        w = 3              # okay so far
        z = g(u, v, w)     # -- BAD -- because we are changing z, an argument
        print(u + v)       # this is okay, it won't change anything
        v += 1             # -- BAD -- do not change v here
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

It's preferable to use a map()-like function rather than a loop. Internal to
the map() function there are certainly variables and assignments, but at least
you're not doing them yourself, you are relying on some library that has
presumably got its own test framework maintained elsewhere.

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
