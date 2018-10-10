# Testable documentation

I saw somebody give a presentation on documentation that could be included
in automatic tests. That is to say, the usage examples provided in the docs
could be automatically checked to make sure they still work with the current
code. The idea intrigued me and I started thinking about how to do that in
Python.

After a few false starts, I saw that it made sense to enable Markdown docs
(like this one) to create links into source code. These links are expanded
by the `weave.py` script, which gets invoked like this.

    ./weave.py < README.md > foobar.html

Then when you view foobar.html in a browser, the links are expanded to the
source code entity, which can be any named Python object, such as a function,
class, or method. For instance, here are some unit tests.

@tests.py:TestMyStuff

The link is a line starting with an asterisk, like "@tests.py:TestMyStuff".
They are testing the class and the function shown below.

@functional.py:Foo

@functional.py:add

Unit tests need to be run frequently, as they should be during development,
to ensure that they always correctly represent what the code is doing. Then
they can be included in documents with these simple links.

It's still possible for the textual content of the markdown file to lag
behind changes in the code. That's unavoidable, unless the markdown somehow
pulls comments out of the docstrings for the Python objects. Maybe that's
the next step here.
