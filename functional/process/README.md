# Some thoughts on development process

I started thinking about all this Nearly Functional stuff because of what I do
in my job. I work on a legacy Python 2.7 system spanning 20-plus EC2 instances.
The code is full of non-optimal things, most of them my fault, they seemed like
good ideas at the time. Anyway this is all part of my on-going effort to clean
up the code and ... uh, get to the point...

Beware importing one thing and 200 other things come along for the ride. One of
my source files, `utils.py`, is not a very well-behaved import. It pulls in too
much, small changes may result in circular imports, it does too much beyond
defining objects, etc.

## Clean imports
* Python source files intended for import (like `utils.py`) may DEFINE things
  (classes, functions, global variables) but they should not DO OTHER THINGS.
  This isn't iron-clad -- it might make sense to assign variables based on
  whether you're in AWS or on docker-compose or whatever.
* If you DO OTHER THINGS then you want it to be CRYSTAL CLEAR what is going on.
  Those sections should be well documented. Ideally there should be a
  convention that they are near the top of the file, or they have some special
  comment string to make them easy to find.
* Avoid circular imports: treat imports as a DAG. Don't pile everything into
  one gigantic file (like `utils.py`), split things into separate concerns.
* Be cognizant of operations that might be slow, or might access resources like
  databases or servers that may be slow or unresponsive. Contemplate a comment
  format for THINGS THAT RUN SLOW or MIGHT BE UNRELIABLE or involve EXTERNAL
  DEPENDENCIES.

## Docker Compose dev process
* Create an alternate `docker-compose.yml` file that brings up the smallest
  viable number of containers.
* Find where the source code lives on those containers, and mount it to the
  code lives on your laptop, so you can edit with your regular dev tools and
  run it in the container immediately. No slow image rebuilds. This also goes
  in the alternate `docker-compose.yml` file.
* Look for any slowdown and see if you can work around it. For instance
  something like "well you have to bring up the entire system and warm up the
  database and do N other things before anything can start".

## Coding Style
* Break code out into strict-FP functions in STANDALONE SOURCE FILES that do
  not need the entire Bbot ecosystem.
* TEST SMALL FEATURES IN ISOLATION. Use fast simple tests or code samples that
  run quickly from the command line, where you can print to stdout or invoke
  PDB.
* The docker image will provide the right libraries.
* DO NOT PULL IN UTILS.PY because it will make you crazy. Unless you feel like
  un-crazy-ing `utils.py`, which is really a good idea.

## Guardrails
* Use asserts, not log statements. Log statements become cluttered and you
  can't find stuff.
* Think carefully about what asserts make sense, don't be afraid to write
  library functions to help. When doing so, favor FP style as much as possible.
* The text of the assert statement should tell you everything you need to know.
  Think "literate" ala Knuth. The strings in the source code can function as
  documentation or comments.
* Asserts should be globally switchable. Probably environment variable.
* A good early application is to deal with TestCases being zero for a given
  target id and exe id. That seems to be a frequent problem.
* One nice form of guardrail is pydantic classes. Use more of thos

## System observer
* Think of this as a system observer who can watch for trouble and intervene if
  needed. Trouble can be defined however I need to define it.
* So this guy accepts aggregated logs, but he's not passive. He watches them
  and can be instructed to take action.
* One hard thing with detecting problems is coordinating stuff from one area of
  the code to another e.g. scan and compare steps. Like following what happens
  to a particular exeid over the whole job. Or coordination between master and
  worker.
* Near term, just use the official mongodb docker image. Later get Nisit
  consensus to make it official??
* Alternatively, put a text file in the master or add a SQL table in `db_master`.
  Remember this is just a test stack thing for now.

