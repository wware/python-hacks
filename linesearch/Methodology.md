# Design methodology for this

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

We have NOT YET WRITTEN ANY CODE. This is all text documents so far, or
drawings on paper or whiteboard. It probably wants to all go into a Markdown
file or a Google doc.

Once all that is done and you have your google doc or markdown, learn how to
write the tests and start TDDing the thing into existence.

# Challenges to applying this methodology

On Thursday I failed to stick to the design methodology. Like
[this owl](https://www.youtube.com/watch?v=pvFzOgK-V9E),
I succumbed to bad habits and went for a quick win. When I started seeing
HOW to get the thing built, I quickly abandoned my "Let's get TDD religion"
stance and ran ahead and just coded it. It worked but it was not the
behavioral change I am hoping to make.

Partly it's that I was worried about how complicated testing might be in
Go, [but this](https://gobyexample.com/testing) looks very palatable.

Taking another look at testing, I see that right now I have two functions,
one for formatting the output line and the other is just the main function,
and neither are suitable for testing. The formatter function makes direct
calls to fmt.Print and its friends, and there is no way to capture and
verify that output in a test as far as I am currently aware.

THe other thing was that I had a fixed schedule yesterday during which I
was trying to learn Go and learn this new methodology at the same time,
and it was just too much. Now I have a working prototype in hand and I
think that positions me well for a second pass.

I'm realizing that there is a skill set for that kind of methodology and
I haven't cultivated that skill set.
