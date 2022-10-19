"""
silly examples for pydoc, related stuff

If you create docstrings for everything and do a decent job
with them, you can use pydoc to see the docs:

    python -m pydoc foo

Pydoc does not handle markdown without some kind of extension.
Maybe I'll do something with markdown and/or RDF/Turtle.
"""

import os


class SafJob(object):
    """
    This class represents a run of SAF to test some binary (represented by an exeid).
    There are lots of getters for job parameters (e.g. os, compiler, saf version, etc) and
    some stuff for run control (start, finish, is_running, terminate).

    :param `**kwargs`: The keyword arguments are used for ...
    :vartype arg: str
    """

    def __init__(self, **kwargs):
        self._preprocessor_branch = kwargs['preprocessor_branch']
        self._results_xml = None
        self.results_xml_path = None
        self.saf_path = None

    @property
    def results_xml(self):
        """
        If available, get a ResultsXml object for this job.

        @return: a ResultsXml object produced by this job, or None
        @raise AssertionError: if "_results_xml" is None
        """
        assert self._results_xml is not None
        for attr in ('decomp_cpu_seconds', 'scan_cpu_seconds', 'peak_vm_gigabytes'):
            assert hasattr(self._results_xml, attr), attr
            assert getattr(self._results_xml, attr) is not None, attr
        return self._results_xml

    def start(self):
        """
        Starts this job.  Once the job is completed, `finish()` should be called
        on the job to ensure proper bookkeeping.  If you run jobs via a
        `SafJobQueue`, you will not need to call `start()` or `finish()` yourself.
        """
        saf_path = self.saf_path
        optimized_path = os.path.join(os.path.dirname(saf_path), 'optimized')
        if os.path.exists(optimized_path):
            saf_path = os.path.join(optimized_path, 'saf')
        if not os.path.isfile(saf_path):
            raise Exception(f"Did not find SAF executable at {saf_path}")


class Vehicle(object):
    '''
    The Vehicle object contains lots of vehicles
    :param arg: The arg is used for ...
    :type arg: str
    :param `*args`: The variable arguments are used for ...
    :param `**kwargs`: The keyword arguments are used for ...
    :ivar arg: This is where we store arg
    :vartype arg: str
    '''

    def __init__(self, arg, *args, **kwargs):
        self.arg = arg

    def cars(self, distance, destination):
        '''We can't travel a certain distance in vehicles without fuels, so here's the fuels

        :param distance: The amount of distance traveled
        :type amount: int
        :param bool destinationReached: Should the fuels be refilled to cover required distance?
        :raises: :class:`RuntimeError`: Out of fuel

        :returns: A Car mileage
        :rtype: Cars
        '''
        pass


def add(x, y):
    """
    Try Epydoc style??

    @param x: This is the first param.
    @param y: This is a second param.
    @return: The sum of x and y.
    @raise: KeyError: Raises an exception.
    """
    return x + y


if __name__ == '__main__':
    print(add(3, 4))
