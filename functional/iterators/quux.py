from pydantic import BaseModel
from typing import List


class Student(BaseModel, frozen=True):
    first_name: str
    last_name: str


class Lecturer(BaseModel, frozen=True):
    first_name: str
    last_name: str
    subject: str


class UniversityClass(BaseModel, frozen=True):
    """
    >>> s1 = Student(first_name='Andrew', last_name='Brown')
    >>> s2 = Student(first_name='Helen', last_name='White')
    >>> s3 = Student(first_name='George', last_name='Johnson')
    >>> l1 = Lecturer(first_name='Maria', last_name='Richardson', subject='Algorithms')
    >>> l2 = Lecturer(first_name='Bob', last_name='Johanson', subject='Programming')
    >>> uni_cl = UniversityClass(
    ...     lecturers=[l1 ,l2],
    ...     students=[s1, s2, s3]
    ... )
    >>> for member in uni_cl:
    ...     print(member)
    first_name='Maria' last_name='Richardson' subject='Algorithms'
    first_name='Bob' last_name='Johanson' subject='Programming'
    first_name='Andrew' last_name='Brown'
    first_name='Helen' last_name='White'
    first_name='George' last_name='Johnson'
    >>> for member in _filter(uni_cl, lambda x: 'n' in x.last_name):
    ...    print(member)
    first_name='Maria' last_name='Richardson' subject='Algorithms'
    first_name='Bob' last_name='Johanson' subject='Programming'
    first_name='Andrew' last_name='Brown'
    first_name='George' last_name='Johnson'
    """
    lecturers: List[Lecturer]
    students: List[Student]
    
    def __iter__(self):
        return self.IterHelper(self)

    class IterHelper(object):
        def __init__(self, p):
            self.p = p
            self.current_index = 0

        def __next__(self):
            try:
                this = (self.p.lecturers + self.p.students)[self.current_index]
                self.current_index += 1
                return this
            except IndexError:
                raise StopIteration


def _filter(self, f):
     for i in self:
         if f(i):
            yield i


def _map(self, f):
    for i in self:
         yield f(i)


def _take(n: int, it):
    for i in it:
        if n <= 0:
            return
        n -= 1
        yield i


def numbers():
    """
    >>> u = _filter(numbers(),
    ...             lambda n:  n % 3 == 0)
    >>> u = _map(u, lambda n: n * 0.5)
    >>> print(list(_take(6, u)))
    [0.0, 1.5, 3.0, 4.5, 6.0, 7.5]
    """
    n = 0
    while True:
        yield n
        n += 1
