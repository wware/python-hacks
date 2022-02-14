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
