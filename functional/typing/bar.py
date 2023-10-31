import doctest
from pydantic import BaseModel


class Student(BaseModel, frozen=True):
    """
    >>> s = Student(
    ...     first_name='Andrew',
    ...     last_name='Smith'
    ... )
    >>> print(s)
    first_name='Andrew' last_name='Smith'
    >>> repr(s)
    "Student(first_name='Andrew', last_name='Smith')"
    >>> s.dict()
    {'first_name': 'Andrew', 'last_name': 'Smith'}
    >>> Student(
    ...     first_name=1234,
    ...     last_name='Smith'
    ... )
    Student(first_name='1234', last_name='Smith')
    >>> Student(
    ...     first_name=['An', 'dr', 'ew'],
    ...     last_name='Smith'
    ... )
    Traceback (most recent call last):
      ...
    pydantic.error_wrappers.ValidationError: 1 validation error for Student
    first_name
      str type expected (type=type_error.str)
    >>> s.first_name
    'Andrew'
    >>> s.last_name
    'Smith'
    >>> s.first_name = 'Jack'
    Traceback (most recent call last):
      ...
    TypeError: "Student" is immutable and does not support item assignment
    """
    first_name: str
    last_name: str


if __name__ == '__main__':
    doctest.testmod(optionflags=doctest.ELLIPSIS)
