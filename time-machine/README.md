# Time machine debugging

* Log everything, but keep the logs as terse as possible. Think of it like
  MPEG: you periodically have a full-detail place where you record everything,
  and you can always go back to one of those, and then to move forward from
  there, you log just deltas. Logs are basically sequences of python dicts.
  The sequence is maintained in a way where going forward or backward one step
  is easy.
* Log format -- maybe Python pickles separated by linefeeds??
* Handling of variables and data is shallow unless you mark something as “I
  need to follow this deeply”. I don’t know yet the exact mechanics for that.
* Presentation is via HTTP. You can slap a time-machine-debug endpoint in
  anything, pull in one or two files, and make it available. And you can turn
  it on simply with feature switches or option checkboxes or whatever. Maybe
  you do a curl command to specify an area where it will be applied.

## What gets logged?

* Filename (full path)
* Line number
* Local variables
