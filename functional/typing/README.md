# Type checking is good

You want to use types for the values in your code, and you want those types
to illustrate or clarify the intent of what your code is doing, and you want
your programming language to flag any type mismatches. Languages like OCaml
and Haskell are great at this sort of thing.

Generally you won't need to specify types for every single variable or class
or whatever. In a lot of cases the language will be able to infer many of
these from usage. If you have a smart-ish IDE like PyCharm, it will perform
that inference and flag mismatches visually.

## Language support: pydantic

Pydantic is similar to dataclasses, but it enforces types by
validating the fields of classes when the constructor is run. If
a type can be coerced (for instance making a string from an int),
it will do that in preference to raising a ValidationError.

Like dataclasses, these classes can be declared to be frozen so
that attempts to set an attribute raise a TypeError.

## Language support: pyright

Pyright is a Microsoft-created linter for type checking in Python.
I haven't used it much and don't know a lot about it. What little
I've read sounds pretty good.

