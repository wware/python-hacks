D ('    ', 'this should be a separate comment from') Let's put in a comment that we can refer to using a regular
expression, and make it a multi-line comment so that we can
pull complex thoughts out in that way. In Markdown these should
be rendered as block quotes. Write a Jinja custom filter for this.
# This is my markdown document
## Diverging from Knuth

Knuth's writings on Literate Programming describe a source document of a
novel format that is processed separately to produce source code in one
instance and a printable document for publication in the other. This is
burdensome since his novel format is not handled well by any tools. There
are far too many advantages to using source code as the format from which
to work. One is tooling, the other is removing the need to maintain a
novel format that nobody else uses, and finally, we remove an entire
toolchain by producing source code directly.

In the current aproach, we instead add machinery so that source code can
include elements that can be used to create the printable document. This
source file is an exploration of what that might look like, and how to
make it as flexible and useful as possible without being confusing.

To generate the printable document from this file, type

    ./hack.py --target my_doc > README.md

We will follow the common pattern of keeping the additional docs in the
source code to prevent divergence.

Let's be able to refer to a function inside the doc text:

## parse_cmd_line_args


    Here is my arg parser.
    :return: parsed args, DUH
    
## *Second* paragraph

Think about how this stuff could dovetail with the MTSL project.
Can we embed RDF into this somehow? And ideally in a way that it
could be automatically extracted and handed to a reasoner?

> Let's put in a comment that we can refer to using a regular
> expression, and make it a multi-line comment so that we can
> pull complex thoughts out in that way. In Markdown these should
> be rendered as block quotes. Write a Jinja custom filter for this.

and let's note a separate comment, differentiated by a change of
indentation

> this should be a separate comment from
> the one immediately above it
