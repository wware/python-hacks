#!/usr/bin/env python

import pprint
import random


class Thing(object):
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return "{0}".format(self._name)

    @classmethod
    def at(cls, places, placename):
        return [x for x in places[placename] if isinstance(x, cls)]


class Person(Thing):
    pass


class Car(Thing):
    def __init__(self, owner):
        assert isinstance(owner, Person)
        Thing.__init__(self, owner)

    def owner(self):
        return self._name

    def __repr__(self):
        return "{0}'s car".format(self.owner()._name)


class Move(object):
    def __init__(self, first, second, items):
        self._first = first
        self._second = second
        self._items = items

    def __repr__(self):
        return "{0} goes from {1} to {2}".format(self._items, self._first, self._second)

    def go(self, places):
        for item in self._items:
            assert item in places[self._first], (self, item, self._first)
            places[self._first].remove(item)
            places[self._second].append(item)

    @classmethod
    def enumerate(cls, places):
        def all_subsets(g):
            results = []
            n = len(g)
            for i in range(1, 2 ** n):
                this_subset = []
                for j in range(n):
                    if (1 << j) & i:
                        this_subset.append(g[j])
                results.append(this_subset)
            return results

        for placename in places.keys():
            these_cars = Car.at(places, placename)
            if len(these_cars) == 0:
                continue
            people = Person.at(places, placename)
            if len(people) == 0:
                continue
            destinations = [p for p in places.keys() if p != placename]
            groupings = all_subsets(people)
            for car in these_cars:
                for grouping in groupings:
                    for dest in destinations:
                        move = cls(placename, dest, grouping + [car])
                        if move.is_valid():
                            yield move

    def demerit(self):
        # a move gets a demerit if somebody is driving somebody else's car
        cars = [i for i in self._items if isinstance(i, Car)]
        assert len(cars) == 1
        car = cars[0]
        people = [i for i in self._items if isinstance(i, Person)]
        if car.owner() in people:
            return 0
        else:
            return 1

    def is_valid(self):
        return True    # base class, moves are always valid

def eq(x, y):
    def f(z):
        return {k: set(v) for k, v in z.items()}

    return f(x) == f(y)

def clone(places):
    return {k: v[:] for k, v in places.items()}

def change_state(places, desired, moveClass=Move):
    before = clone(places)

    def layer(trajectories, target):
        winners = []
        new_trajectories = []
        for t in trajectories:
            config = clone(before)
            for move in t:
                move.go(config)
            for next_move in moveClass.enumerate(config):
                config2 = clone(config)
                new_trajectory = t + [next_move]
                next_move.go(config2)
                if eq(config2, target):
                    winners.append(new_trajectory)
                new_trajectories.append(new_trajectory)
        return winners, new_trajectories

    trajectories = [[]]
    winners = []
    while not winners:
        winners, trajectories = layer(trajectories, desired)

    def cmp_func(path1, path2):
        if len(path1) < len(path2):
            return -1
        if len(path1) > len(path2):
            return 1
        demerits1 = sum([move.demerit() for move in path1])
        demerits2 = sum([move.demerit() for move in path2])
        if demerits1 < demerits2:
            return -1
        if demerits1 > demerits2:
            return 1
        return 0

    winners.sort(cmp_func)
    return winners[0]


######################################################################
# Stuff specific to my near-term logistical challenges

PLACENAMES = ["CWV", "NEBH", "MGH", "Will's house", "Lori's house", "Sue's house"]

lori = Person("Lori")
will = Person("Will")
sue = Person("Sue")

lcar = Car(lori)
wcar = Car(will)
scar = Car(sue)


class ThisMove(Move):
    def is_valid(self):
        first, second, people = self._first, self._second, [i for i in self._items if isinstance(i, Person)]
        # Lori cannot drive into Boston by herself
        if second in ('NEBH', 'MGH') and people == [lori]:
            return False
        # If Sue drives into Boston, Lori is with her
        if second in ('NEBH', 'MGH') and sue in people and lori not in people:
            return False
        # Don't drive Will or Lori to Sue's house
        if second == "Sue's house" and (will in people or lori in people):
            return False
        return True


def stuff_at(d):
    rd = {k: [] for k in PLACENAMES}
    rd.update(d)
    # If Sue and Sue's car are not explicitly specified, put them at Sue's house
    for s in (sue, scar):
        if not [place for name, place in rd.items() if s in place and name != "Sue's house"]:
            rd["Sue's house"].append(s)
    return rd

######################################################################
#    Finally, solve the actual problem
######################################################################

initial = stuff_at({
    "CWV": [lori, lcar],
    "Will's house": [will, wcar],
})

mon_4pm = stuff_at({
    'CWV': [lcar],
    'MGH': [will, wcar, lori],
})

print "Monday 4pm: Get Lori to MGH"
pprint.pprint(change_state(initial, mon_4pm, moveClass=ThisMove))

both_at_wills_house = stuff_at({
    "Will's house": [will, wcar, lori, lcar],
})

print
print "Monday night, Will and Lori go back to Will's house"
pprint.pprint(change_state(mon_4pm, both_at_wills_house, moveClass=ThisMove))

before_surgery = stuff_at({
    'NEBH': [will, sue, scar, lori],
    "Will's house": [wcar, lcar]
})

print
print "Tuesday morning, Will and Lori get a ride from Sue to NEBH"
pprint.pprint(change_state(both_at_wills_house, before_surgery, moveClass=ThisMove))

will_alone_at_nebh = stuff_at({
    'NEBH': [will],
    "Will's house": [wcar],
    "Lori's house": [lcar, lori],   # Lori has work on Monday
})

print
print "Tuesday night, Will stays at NEBH, everybody else goes home"
pprint.pprint(change_state(before_surgery, will_alone_at_nebh, moveClass=ThisMove))

thursday_night = stuff_at({
    "Will's house": [wcar, lcar, will, lori],
})

print
print "Thursday night, Lori stays over to help Will recover"
pprint.pprint(change_state(will_alone_at_nebh, thursday_night, moveClass=ThisMove))

final = stuff_at({
    "Lori's house": [lori, lcar],
    "Will's house": [will, wcar],
})

print
print "Sunday night, Lori goes home"
pprint.pprint(change_state(thursday_night, final, moveClass=ThisMove))
