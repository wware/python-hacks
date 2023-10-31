"""
Things to do here:

    pylint dbhack.py
    mypy dbhack.py
    python3 dbhack.py
"""

import os
# pylint: disable=missing-function-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=missing-class-docstring, redefined-outer-name
import logging
import sys
from typing import Generator
import pytest
from sqlalchemy import create_engine, text, insert, select
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.engine import Engine, cursor
from sqlalchemy.sql import sqltypes
# pylint: disable=no-name-in-module
from pydantic import BaseModel, create_model
# pylint: enable=no-name-in-module

is_debugging = os.environ.get("DEBUG", "").lower() in ['1', 'true', 'yes']
logger = logging.getLogger()
h = logging.StreamHandler(sys.stdout)
h.setFormatter(logging.Formatter("%(filename)s:%(lineno)d -- %(message)s"))
logger.handlers = [h]
logger.setLevel(logging.DEBUG if is_debugging else logging.INFO)


def execute_db(engine: Engine, *args, **kw):
    assert isinstance(engine, Engine), engine
    stacklevel = kw.pop('stacklevel', 2)
    logger.debug(args, stacklevel=stacklevel)
    sql, args = text(args[0]), args[1:]
    with engine.connect() as connection:
        # mypy doesn't know about connections
        # the "begin" context manager handles commit and rollback
        with connection.begin():                     # type: ignore
            return connection.execute(sql, *args)    # type: ignore



class BaseQuery:
    """
    The SQL query string goes here in the docstring.
    Note this is NOT a pydantic model.
    Queries like this are iterators. They can query across multiple
    tables using JOINs.
    """
    def __init__(self, eng: Engine, **args):
        self.eng = eng    # later this will need to be SQLAlchemy connection
        self.args = args

    def __iter__(self) -> Generator[BaseModel, None, None]:
        result_class = getattr(self, 'Result')
        keys = result_class.__fields__.keys()
        for row in execute_db(self.eng, self.__doc__, self.args, stacklevel=3):
            yield result_class(**dict(zip(keys, row)))


#######################################


metadata_obj = MetaData()


def validatingTable(T):
    def get_type_for(col):
        if isinstance(col.type, sqltypes.Integer):
            return 123
        elif isinstance(col.type, sqltypes.String):
            return 'abc'
        else:
            raise Exception(col.type)
    # Still much to do to figure this out
    # https://docs.pydantic.dev/usage/models/
    types = dict(((c.name, get_type_for(c)) for c in T.columns))
    print(types)
    strategy = create_model('Strategy', **types)
    return T

person = validatingTable(Table(
    "Person",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(16), nullable=False),
    Column("age", Integer)
))


book = validatingTable(Table(
    "Book",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("title", String(16), nullable=False),
    Column("owner_id", Integer, ForeignKey("Person.id"), nullable=False),
))




def insert_into(engine: Engine, table: Table, **params):
    stmt = insert(table).values(**params)
    with engine.begin() as conn:
        # begin handles commit and rollback
        result = conn.execute(stmt)
        conn.commit()


def get_id(engine: Engine, table: Table, **params):
    cols = getattr(table, 'c')
    stmt = select(getattr(cols, 'id'))
    for k, v in params.items():
        stmt = stmt.where(getattr(cols, k) == v)
    with engine.connect() as conn:
        things = conn.execute(stmt).fetchall()
        assert len(things) == 1, (stmt.compile(), things)
        return things[0][0]


class YoungFolksWithBooks(BaseQuery):
    """
    SELECT DISTINCT    -- any person owning any books
        Person.name
    FROM Person
    JOIN Book
        ON Book.owner_id = Person.id
    WHERE age < :cutoff
    """
    class Result(BaseModel, frozen=True):
        name: str


####################################


@pytest.fixture
def testdb() -> Engine:
    e = create_engine("sqlite:///:memory:")
    return e


@pytest.fixture
def scenario(testdb):
    assert isinstance(testdb, Engine), testdb
    metadata_obj.create_all(testdb)
    insert_into(testdb, person, name="Alice", age=23)
    insert_into(testdb, person, name="Bob", age=25)
    insert_into(testdb, person, name="Charlie", age=12)

    id1 = get_id(testdb, person, name="Alice")
    insert_into(testdb, book, owner_id=id1, title="Book 1")
    insert_into(testdb, book, owner_id=id1, title="Book 2")
    id2 = get_id(testdb, person, name="Bob")
    insert_into(testdb, book, owner_id=id2, title="Book 3")
    return testdb


def test_1_check_engine(scenario):
    eng = scenario
    assert isinstance(eng, Engine), eng


def test_2_everybody(scenario):
    eng = scenario
    stmt = select(person.c.name, person.c.age)
    with eng.connect() as conn:
        z = conn.execute(stmt)
    # fetchone or fetchall from a table returns a list of tuples
    assert z.fetchall() == [
        ('Alice', 23), ('Bob', 25), ('Charlie', 12)
    ]


def test_2_check_types(scenario):
    eng = scenario
    with pytest.raises(Exception):
        # age should be an integer
        insert_into(eng, person, name="Debbie", age="young")


def test_3_select_with_where_clause(scenario):
    eng = scenario
    stmt = select(person.c.name, person.c.age).where(person.c.age > 24)
    with eng.connect() as conn:
        z = conn.execute(stmt)
    assert z.fetchall() == [
        ('Bob', 25)
    ]


def test_4_queries_are_iterable(scenario):
    def is_iterable(thing):
        return iter(thing) is not None

    eng = scenario
    these = YoungFolksWithBooks(eng=eng, cutoff=24)
    assert is_iterable(these), these
    assert isinstance(list(these), list), these


def test_5_select_with_books(scenario):
    eng = scenario
    these = YoungFolksWithBooks(eng=eng, cutoff=24)
    assert [result.name for result in these] == ['Alice']
    assert list(YoungFolksWithBooks(eng=eng, cutoff=30)) == [
        YoungFolksWithBooks.Result(name='Alice'),
        YoungFolksWithBooks.Result(name='Bob')
    ]


if __name__ == "__main__":
    pytest.main([__file__])
