#!/usr/bin/env python

import pprint
import random


# places

places = {
    'CWV': [],
    'NEBH': [],
    'MGH': [],
    "Will's house": [],
    "Lori's house": [],
    "Sue's house": []
}


class Thing(object):
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return "{0}".format(self._name)

    @classmethod
    def at(cls, placename):
        return [x for x in places[placename] if isinstance(x, cls)]


class Person(Thing):
    pass


class Car(Thing):
    def __init__(self, owner):
        assert isinstance(owner, Person)
        Thing.__init__(self, owner)

    def __repr__(self):
        # self._name is actually a Person, not a string
        return "{0}'s car".format(self._name._name)


class Move(object):
    def __init__(self, first, second, items):
        self._first = first
        self._second = second
        self._items = items

    def __repr__(self):
        return "\n{0} goes from {1} to {2}".format(self._items, self._first, self._second)

    def go(self):
        print self
        for item in self._items:
            assert item in places[self._first], (item, self._first)
            places[self._first].remove(item)
            places[self._second].append(item)


lori = Person("Lori")
will = Person("Will")
sue = Person("Sue")

lcar = Car(lori)
wcar = Car(will)
scar = Car(sue)


def random_move():
    def non_empty_subset(g):
        assert len(g) > 0
        while True:
            sg = [x for x in g if random.choice([True, False])]
            if len(sg) > 0:
                return sg

    tries = 0
    while True:
        try:
            firsts = []
            for k in places.keys():
                if len(Car.at(k)) > 0 and len(Person.at(k)) > 0:
                    firsts.append(k)
            first = random.choice(firsts)
            car = random.choice(Car.at(first))
            people = non_empty_subset(Person.at(first))
            second = random.choice([sec for sec in places.keys() if sec != first])
            move = Move(first, second, people + [car])

            # Lori cannot drive into Boston by herself
            assert not (people == [lori] and second in ('NEBH', 'MGH')),\
                "Lori cannot drive into Boston by herself - {0}".format(move)

            return move
        except InvalidMove:
            tries += 1
            if tries == 10000:
                raise Exception("Maybe no good moves??\n" + pprint.pformat(places))


def pause(info):
    print
    print info
    pprint.pprint(places)


# initial state
places["CWV"] = [lori, lcar]
places["NEBH"] = []
places["MGH"] = []
places["Will's house"] = [will, wcar]
places["Lori's house"] = []
places["Sue's house"] = [sue, scar]

pause("Monday afternoon before MGH appointment")
Move("Will's house", "CWV", [will, wcar]).go()
Move("CWV", "MGH", [will, lori, wcar]).go()
assert lori in places["MGH"]
Move("MGH", "CWV", [will, lori, wcar]).go()
Move("CWV", "Will's house", [will, wcar]).go()
Move("CWV", "Will's house", [lori, lcar]).go()
pause("Monday night")

Move("Sue's house", "Will's house", [sue, scar]).go()
pause("Tuesday morning")

Move("Will's house", "NEBH", [will, lori, sue, scar]).go()
assert will in places["NEBH"]
pause("Will surgery")
Move("NEBH", "Will's house", [lori, sue, scar]).go()

Move("Will's house", "Sue's house", [sue, scar]).go()
Move("Will's house", "Lori's house", [lori, lcar]).go()

pause("Thursday morning and Will is ready to go home")
Move("Lori's house", "Will's house", [lori, lcar]).go()
Move("Sue's house", "Will's house", [sue, scar]).go()
Move("Will's house", "NEBH", [lori, sue, scar]).go()
Move("NEBH", "Will's house", [will, lori, sue, scar]).go()
Move("Will's house", "Sue's house", [sue, scar]).go()
pause("Thursday night")

pause("Sunday night and Lori has work the next day")
Move("Will's house", "Lori's house", [lori, lcar]).go()
pause("Starting the work week")
assert lori in places["Lori's house"]