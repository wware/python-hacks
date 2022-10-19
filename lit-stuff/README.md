# Literate programming hacks for Python

I have various ideas in this area.

* Figure out how to do straight-up literate programming without
  losing the benefit of a nice IDE like PyCharm. Stick the texty
  stuff in a separate file?
* What about semantic web stuff? Maybe adapt JSON-LD or RDFa to
  work with Markdown?

Let's plan on a separate file, and let's make ....

What's the workflow? What are you trying to accomplish?

    Code -> runnable as is
    Source text -> markdown -> HTML/PDF
        pull in code snippets, something nice with any RDF
    Source text -> RDF/Turtle -> sem web tools of any sort

Use regexps to select areas of code, use sequence of patterns like this

    SOURCEFILE foo.py
    AFTER class SafJob
    INCLUDE def results_xml

    INCLUDE def start

So we grab the first instance of `def\s+start` that comes after the
first instance of `class\s+SafJob`. We look at indentation to decide
where the method ends. We discard blank lines and optionally preserve
line numbers.

We might need some kind of root directory for `SOURCEFILE`.

Semantic stuff looks like

    RDF    Quux a prefix:thing .

If it comes immediately after an `INCLUDE` then it refers to that function
or variable or class or whatever and you can use "_" as the subject.

A big block of RDF can look like

    RDF   First line blah blah
    RDF   Second line blah blah
    RDF   Third line blah blah
    RDF   Fourth line blah blah

