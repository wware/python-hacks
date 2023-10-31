import pytest
from frozendict import frozendict
from frozenlist import FrozenList
from pydantic import BaseModel


# Let's first confirm that these data types are really "frozen"

def test_frozendict_really_frozen():
    d = frozendict({"abc": 123, "def": 456})
    with pytest.raises(TypeError):
        d["abc"] = 11
    with pytest.raises(TypeError):
        d["def"] = 654321
    assert d["abc"] == 123
    assert d["def"] == 456
    assert d == {"abc": 123, "def": 456}


def test_frozenlist_really_frozen():
    L = FrozenList(range(5))
    L[2] = 11
    # you can change the list until you freeze it
    L.freeze()
    with pytest.raises(RuntimeError):
        L[3] = 42
    assert L == [0, 1, 11, 3, 4]



class Person(BaseModel, frozen=True):
    name: str
    age: int


def test_frozen_instance_really_frozen():
    p = Person(name="Bob", age=35)
    with pytest.raises(TypeError):
        p.name = "Jimmy"
    with pytest.raises(TypeError):
        p.age = 42
    assert p == Person(name="Bob", age=35)
