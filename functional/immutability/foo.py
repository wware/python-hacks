import json
import datetime
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


class BaseJsonModel(BaseModel):
    @classmethod
    def fromjson(cls, s):
        d = json.loads(s)
        return cls(**d)

    def json(self):
        def make_json_dumpable(obj):
            if obj is None or isinstance(obj, (int, float)):
                return obj
            elif isinstance(obj, complex):
                return {'re': obj.real, 'im': obj.imag}
            elif isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
                return obj.isoformat()
            elif isinstance(obj, datetime.timedelta):
                return str(obj)
            elif isinstance(obj, (set, list, tuple)):
                return [make_json_dumpable(x) for x in obj]
            elif isinstance(obj, dict):
                return dict(make_json_dumpable(list(obj.items())))
            else:
                return str(obj)
        return json.dumps(make_json_dumpable(self.dict()))


class Person2(BaseJsonModel, frozen=True):
    name: str
    age: int
    birthday: datetime.date


def test_json_frozen_instance_really_frozen():
    bday = datetime.date(1982, 3, 25)
    p = Person2(name="Bob", age=35, birthday=bday)
    with pytest.raises(TypeError):
        p.name = "Jimmy"
    with pytest.raises(TypeError):
        p.age = 42
    assert p == Person2(name="Bob", age=35, birthday=bday)
    assert '"name": "Bob"' in p.json(), p.json()
    assert '"age": 35' in p.json(), p.json()
    assert '"birthday": "1982-03-25"' in p.json(), p.json()
    p2 = Person2.fromjson(p.json())
    assert p2 == p, p2
    assert p2.name == "Bob", p2
    assert p2.age == 35, p2
    assert p2.birthday == bday, p2
    # TODO also test datetime.datetime, datetime.time, datetime.timedelta
