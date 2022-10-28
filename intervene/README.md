# Debug stuff in out-of-band whatsis

This is a set of debug add-ons that you control by setting an environment
variable and uploading a python source file to each host. Typical use cases
will be tracing running Python code, and watching changes to the values of
particular variables, and you can do these things without changing the source
code running on the worker.

Application might typically look like this.

    out-of-band:
        env:
            # The worker code will import the file `/work/foo123456.py` as a Python
            # module and then run the `main` function in that file
            INJECT: foo12345
            # or we could opt to run the `xyzzy` function in that file
            INJECT: foo12345@xyzzy

In the code in this directory, the application code is in `example.py`, the
`foo12345.py` file is being represented by `elsewhere.py`, and the utils code
I will need is in `intervene.py`.

To use this stuff in a normal workflow, you would run the `predeploy` playbook
to make sure all the workers are awake, then use an ansible command to copy
the `foo12345.py` file into the `~/app` directory which is mapped to `/work` in
the docker container, and then use the YAML snippet above to set up the environment
variable.
