# Line search utility

This is something I need for a project. It's like a smarter version of
Unix head and tail. Here is the rough idea.

    linesearch --head --regex 'def\\s+start' --offset 1 --file input.txt

A "trigger line" is the line on which the regex is found, moved by the
amount specified by `--offset`, so if the offset is +2 then the trigger
line is two lines after the regex, if -1 it is the line before, and so on.

If "--head" is selected then we print from the first line to the trigger
line inclusive. If "--tail" is selected then we print from the trigger
line to the last line inclusive. If both are selected then the entire
input file will be printed. If neither is selected, then only the trigger
line is printed.

You can invert the sense of the regex with "--not", so that you trigger
on the absence of the regex rather than its presence.

The output format by "--format". The format pieces are like this

* "%N" is line number, "%6N" to make it six characters wide, "%-6N" for left justified
* "%L" is contents of line not including line endings
* Default format is "%L"

Maybe I'll add more options later, can't think of any more right now.

This project will be done in Go.

# Top-level vibe

Executable takes an input file and some command line arguments as described
above. Prints out lines from the input file as controlled by the command
line arguments.

The input file is just straight text, we don't concern ourselves with its
contents, we do not try to parse or interpret any in it.

Suppose we have an input file like this. Call it `input.txt`.

    This is the first line of the input file.
    The second line mentions the word "donkey".
    The third line includes the word "petunia".
    Here is the the fourth line.
    Not much happens on the fifth line.

A simple case would be to print all lines up to and including the line that
contains "petunia", and this can be done using `--input` or taking the input
from stdin.

    linesearch --head --regex petunia --input input.txt
    cat input.txt | linesearch --head --regex petunia

In either case you get three lines of output:

    This is the first line of the input file.
    The second line mentions the word "donkey".
    The third line includes the word "petunia".

If you add `--offset 1` you'll get the fourth line at the end. If you add
`--offset -1` then you'll only get the first two lines.

