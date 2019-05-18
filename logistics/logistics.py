#!/usr/bin/env python

import pprint
import logging
import sys
import yaml

logging.basicConfig(format='%(asctime)-15s  %(levelname)s  %(filename)s:%(lineno)d  %(message)s',
                    level=logging.DEBUG, stream=sys.stdout)


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
    def owner(self):
        return getattr(self, '_owner', None)

    def __repr__(self):
        return "{0}'s car".format(self._name)


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


def layer(trajectories, target, before, moveClass):
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


######################################################################
# Stuff specific to my near-term logistical challenges

PLACENAMES = ["CWV", "NEBH", "MGH", "Will's house", "Lori's house", "Sue's house"]

lori = Person("Lori")
will = Person("Will")
sue = Person("Sue")

lcar = Car(lori)
wcar = Car(will)
scar = Car(sue)

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

def moveBuilder(lookup):
    class ThisMove(Move):
        def is_valid(self):
            first, second, people = self._first, self._second, [i for i in self._items if isinstance(i, Person)]
            # Lori cannot drive into Boston by herself
            if second in ('NEBH', 'MGH') and people == [lookup['Lori']]:
                return False
            # If Sue drives into Boston, Lori is with her
            if second in ('NEBH', 'MGH') and lookup['Sue'] in people and lookup['Lori'] not in people:
                return False
            # Don't drive Will or Lori to Sue's house
            if second == "Sue's house" and (lookup['Will'] in people or lookup['Lori'] in people):
                return False
            return True
    return ThisMove


def main(problem_specification):
    info = yaml.load(problem_specification, Loader=yaml.SafeLoader)
    # logging.debug("\n" + pprint.pformat(info))

    placenames = info['places']
    people = []
    cars = []
    lookup = {}

    for name in info['people']:
        p = Person(name)
        people.append(p)
        c = Car(name)
        c._owner = p
        cars.append(c)
        lookup[repr(p)] = p
        lookup[repr(c)] = c

    thisMove = moveBuilder(lookup)

    def config(step):
        step = step.copy()
        step.pop('description')
        assert set(step.keys()) <= set(placenames), step.keys()
        places = {name: [] for name in placenames}
        places.update({k: map(lambda z: lookup[z], v) for k, v in step.items()})
        return places


    initial = info['steps'][0]
    print '### ' + initial['description']
    pprint.pprint({k: v for k, v in initial.items() if k != 'description'})

    previous = None
    for step1, step2 in zip(info['steps'][:-1], info['steps'][1:]):
        cfg1 = config(step1)
        cfg2 = config(step2)
        assert previous is None or previous == cfg1
        before = clone(cfg1)
        trajectories = [[]]
        winners = []
        while not winners:
            winners, trajectories = layer(trajectories, cfg2, before, thisMove)
        winners.sort(cmp_func)
        print
        print '### ' + step2['description']
        pprint.pprint(winners[0])
        previous = cfg2


if __name__ == '__main__':
    main("""
people: [Lori, Will, Sue]
# cars: [Lori, Will, Sue]
# if cars is not specified, assume each person has a car

places: [Lori's house, Will's house, Sue's house, CWV, MGH, NEBH]

# TBD - this replaces moveBuilder
disallowed_moves:
    # Lori doesn't drive into Boston alone.
    - people: [Lori]
      destination_in: [NEBH, MGH]
    # Neither does Sue.
    - people: [Sue]
      destination_in: [NEBH, MGH]
    # Lori and Sue never go to Sue's house.
    - people_include: [Will]
      destination: Sue's house
    - people_include: [Lori]
      destination: Sue's house

steps:
    - CWV:
        - Lori
        - Lori's car
      Will's house: [Will, Will's car]
      Sue's house: [Sue, Sue's car]
      description: Initial state
    - CWV: [Lori's car]
      MGH: [Will, Will's car, Lori]
      Sue's house: [Sue, Sue's car]
      description: Monday 4pm, get Lori to MGH
    - Will's house: [Will, Lori, Will's car, Lori's car]
      Sue's house: [Sue, Sue's car]
      description: Monday evening, go to Will's house
    - Will's house: [Will's car, Lori's car]
      NEBH: [Will, Lori, Sue, Sue's car]
      description: Tuesday morning, Sue drives us to NEBH
    - Will's house: [Will's car]
      NEBH: [Will]
      Sue's house: [Sue, Sue's car]
      Lori's house: [Lori, Lori's car]
      description: Tuesday night, Will stays at NEBH, everybody else goes home
    - Will's house: [Will's car, Will, Lori, Lori's car]
      Sue's house: [Sue, Sue's car]
      description: Thursday night, Lori stays over to help Will recover
    - Will's house: [Will's car, Will]
      Lori's house: [Lori, Lori's car]
      Sue's house: [Sue, Sue's car]
      description: Sunday night, Lori goes home""")
