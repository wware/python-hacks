"""
pylint likes docstrings, even useless ones
"""
from typing import List
from pydantic import BaseModel


class Student(BaseModel, frozen=True):
    """
    pylint likes docstrings, even useless ones
    """
    first_name: str
    last_name: str


class Lecturer(Student):
    """
    frozen-ness is inherited from Student
    """
    subject: str


class UniversityClass(BaseModel, frozen=True):
    """
    pylint likes docstrings, even useless ones
    """
    lecturers: List[Lecturer]
    students: List[Student]

    def everybody(self):
        """
        pylint likes docstrings, even useless ones
        """
        return self.lecturers + self.students

    def __iter__(self):
        """
        pylint likes docstrings, even useless ones
        """
        return UniversityClassIter(uc=self)


class IteratorHelper(BaseModel):
    """
    cannot be frozen, iterators are inherently stateful
    """
    def __iter__(self):
        """
        pylint likes docstrings, even useless ones
        """
        return self

    def __next__(self):
        """
        pylint likes docstrings, even useless ones
        """
        raise NotImplementedError

    def filter(self, func):
        """
        pylint likes docstrings, even useless ones
        """
        owner = self

        class FilteredIterator(IteratorHelper):
            def __next__(self):
                # StopIteration trickles up to caller
                while True:
                    this = next(owner)
                    if func(this):
                        return this
        return FilteredIterator()

    def map(self, func):
        """
        pylint likes docstrings, even useless ones
        """
        owner = self

        class MappedIterator(IteratorHelper):
            def __next__(self):
                # StopIteration trickles up to caller
                return func(next(owner))
        return MappedIterator()


class UniversityClassIter(IteratorHelper):
    """
    cannot be stateful, current_index needs to be mutable
    """
    uc: UniversityClass
    current_index: int = 0

    def __next__(self):
        """
        pylint likes docstrings, even useless ones
        """
        try:
            r_value = self.uc.everybody()[self.current_index]
            self.current_index += 1
            return r_value
        except IndexError as exc:
            raise StopIteration from exc


if __name__ == '__main__':
    s1 = Student(
        first_name='Andrew',
        last_name='Smith'
    )
    s2 = Student(
        first_name='Helen',
        last_name='White'
    )
    s3 = Student(
        first_name='George',
        last_name='Johnson'
    )

    l1 = Lecturer(
        first_name='Jane',
        last_name='Richardson',
        subject='Algorithms'
    )
    l2 = Lecturer(
        first_name='Bob',
        last_name='Johanson',
        subject='Programming'
    )

    uni_cl = UniversityClass(
        lecturers=[l1 ,l2],
        students=[s1, s2, s3]
    )
    uni_cl2 = UniversityClass(
        lecturers=[l1 ,l2],
        students=[s1, s2, s3]
    )

    i1 = iter(uni_cl)
    i2 = iter(uni_cl2)
    # pull two items out of the first iterator
    print(next(i1))
    print(next(i1))
    # only three left
    for member1, member2 in zip(i1, i2):
        print((member1, member2))
    print('----')
    for member in iter(uni_cl).filter(
        # select only the things you want the expensive
        # computation applied to
        lambda s: 'o' in s.first_name
    ).map(
        # perform an expensive computation on the selected things
        lambda s: f"{repr(s)} with expensive computation"
    ):
        print(member)
