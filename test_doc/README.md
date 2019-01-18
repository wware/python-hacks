# Testable documentation

[Fully rendered](http://htmlpreview.github.io/?https://github.com/wware/python-hacks/blob/master/test_doc/w.html)

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

## Thinking about going further with this

I'm looking at [Mistune](https://github.com/lepture/mistune) and while it's
appealing, it's not the right direction. My chief problem is that I want to
pull lines out of source files and I need to decide how to do that gracefully.

Currently I try to figure out where a method or function or class ends. That
mostly works. But then I can't pull out just some section of something. And
the way I do it works mostly, but not perfectly.

I could mark up my source with comments like `#+foobar` to start a section and
`#-foobar` to end it, but that's really kinda messy. It would have the benefit
of keeping documentation prominent in the mind of the developer as they
change the code, since they need to have those tags make sense. But it's still
a bit ugly.

I'm half convinced that those ugly tags are really the right way to go. I
don't see a much prettier solution to this. Either the code is marked up or
it isn't, and if it is, you need markup that doesn't break functionality
and isn't too cumbersome, and `#+foobar` may be about as well as you can do.

Let's use `@` for whole things (classes, methods, functions) which are
already working, and use `=` for tagged regions. The mnemonic will be that
`+`, `-`, and `=` are all arithmetic symbols. So let's try some of that.

Here is a bit of the regulra expression hacking to make this work.

=weave.py:hack-regex-1

And a little bit more of that hacking here.

=weave.py:hack-regex-2
