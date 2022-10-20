# Line search utility

This is something I need for a project. It's like a smarter version of
Unix head and tail. Here is the rough idea.

    linesearch -head -regex 'def\\s+start' -offset 1 -file input.txt

The opposite of "-head" is "-tail". There is a trigger event (which line
contains the regex) and an offset (treat it like it happened one line
later, or one line earlier, or whatever). If it's "head" then you print
all the lines from top of file to the trigger line (up to offset), if
it's "tail" then you print from the trigger line to the end of file.
Output goes to stdout.

You can invert the sense of the regex with "-not", so that you trigger
on the absence of the regex rather than its presence.

Line numbers are controlled by "-nums" and output format by "-format".
The format pieces are like this

* "%N" is line number, "%6N" to make it six characters wide, "%-6N" for left justified
* "%L" is contents of line not including trailing CR-or-LF
* Default format is "%L\\n"

Maybe I'll add more options later, can't think of any more right now

This project will be done in Go.

# TDD Vibes

It's pretty common for me to get stuck in the weeds with a lot of yak shaving.
Obviously I want to avoid that going forward. Here is my plan.

* Apply TDD at a "product" level.
* Break down the product into functions, data structures, etc. Draw a block diagram.
* Apply TDD to each function, data structure, class, method, etc.

What do I mean by "apply TDD"?

* Brief description of intended function and how it fits into the design.
* What types or data structures are used as inputs.
* What type or data structure is returned.
* Tests to confirm correct behavoid. Look for corner cases and weird stuff.
  Make the tests comprehensive.

Note we have NOT YET WRITTEN ANY CODE. This is all text documents so far, or
drawings on paper or whiteboard. It probably wants to all go into a Markdown
file or a Google doc.

Once all that is done and you have your google doc or markdown, learn how to
write the tests and start TDDing the thing into existence.

# So let's do the product-level vibe

Executable takes an input file and some command line arguments as described
above. Prints out lines from the input file as controlled by the command
line arguments.

The input file is just straight text, we don't concern ourselves with its
contents, we do not try to parse or interpret any in it.

# Round one did not go so well

I failed to stick to the design process. Like
[this owl](https://www.youtube.com/watch?v=pvFzOgK-V9E),
I succumbed to bad habits and went for a quick win. When I started seeing
HOW to get the thing built, I quickly abandoned my "Let's get TDD religion"
stance and ran ahead and just coded it. It worked but it was not the
behavioral change I am hoping to make.

Partly it's that I was worried about how complicated testing might be in
Go, [but this](https://gobyexample.com/testing) looks very palatable.

THe other thing was that I had a fixed schedule yesterday during which I
was trying to learn Go and learn this new methodology at the same time,
and it was just too much. Now I have a working prototype in hand and I
think that positions me well for a second pass.