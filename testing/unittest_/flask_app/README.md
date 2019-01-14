# Unit-testing Flask apps

The `app.run` thing is a decorator for endpoint functions.
But they are still normal functions and you can import them
into another file and use `unittest` to make sure they do the
right thing.

If there is a database involved, you can mock it out with
`unittest.mock` and make sure the wrapping around the database
is doing the right thing. So that's kinda handy.