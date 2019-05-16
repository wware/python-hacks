##############################
# Tower of Hanoi

import logging
from hypothesis import given, settings, assume, unlimited
import hypothesis.strategies as st

log_filename = 'debug.log'
logging.basicConfig(filename=log_filename, level=logging.DEBUG)
logger = logging.getLogger(__name__)


@settings(max_examples=10000)
@given(st.lists(st.integers(min_value=0, max_value=5)))
def test_tower_of_hanoi(lst):
    full = [1, 2, 3]
    things = [full[:], [], []]
    for z in lst:
        x, y = {
            0: (0, 1),
            1: (0, 2),
            2: (1, 0),
            3: (1, 2),
            4: (2, 0),
            5: (2, 1)
        }[z]
        assume(len(things[x]) > 0)
        assume(len(things[y]) == 0 or things[y][0] > things[x][0])
        gotten = things[x].pop(0)
        things[y].insert(0, gotten)
    assert things != [[], [], full]
