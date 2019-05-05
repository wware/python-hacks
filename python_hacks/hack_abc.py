import abc


class MyLittleInterface(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def load(self, input):
        """Retrieve data from the input source and return an object."""

    @abc.abstractmethod
    def save(self, output, data):
        """Save the data object to the output."""


class HappyImplementation(MyLittleInterface):
    def load(self, input):
        return input.read()

    def save(self, output, data):
        return output.write(data)


class SadImplementation(MyLittleInterface):
    def load(self, input):
        return input.read()


happy = HappyImplementation()

try:
    sad = SadImplementation()
    assert False, "Instantiating SadImplementation should have failed"
except TypeError:
    # Expected and correct -- this happens because SadImplementation does not provide
    # an implementation for the save method.
    pass