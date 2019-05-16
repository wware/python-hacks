# Tower of Hanoi solved by Hypothesis

This uses a simple _reductio-ad-absurdum_ argument. Specify the
problem and assert that no solution exists, and let Hypothesis
try to prove you wrong.

The pain in the butt is that you need a fairly exhaustive search
to make this work, and Hypothesis does a lot of lovely things
but nearly exhaustive searches are not among its tricks.

You want to design the strategies to minimize the number of
branches Hypothesis needs to try. That's a good idea for
puzzle solving in general.