# Debug stuff in out-of-band whatsis

    out-of-band:
        # use this file to debug the preflight step
        # The saf-preflight script will import the file as a Python
        # module and then run the xyzzy function, passing in its
        # globals directory as an argument
        preflight: /tmp/foo12345.py@xyzzy

-----------------

This is a change to the "debuggable" function in utils.py.

This makes it possible to replace global objects (functions, class definitions)
in the saf-preflight step (or elsewhere), or to replace methods in a class. One
useful from of replacement is to use a Python decorator so that you're not
having to replicate all the functionality in a large function or method. So that
might look like

    def xyzzy(G):
        cls = G.get("MyClass", None)
        assert cls is not None and isinstance(cls, (type, types.ClassType)), cls
        old_method = cls.mymethod

        def my_new_method(self, x, y):
            print x, y
            z = old_method(self, x, y)
            print z
            return z
        
        cls.mymethod = my_new_method

So this is a case of decorating a class method. The code in the debuggable
function will look something like
