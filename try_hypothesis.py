def encode(input_string):
    # print input_string
    count = 1
    prev = ''
    lst = []
    lastchar = ''
    for character in input_string:
        lastchar = character
        if character != prev:
            if prev:
                entry = (prev, count)
                lst.append(entry)
            count = 1
            prev = character
        else:
            count += 1
    entry = (lastchar, count)
    lst.append(entry)
    return lst


def decode(lst):
    q = ''
    for character, count in lst:
        q += character * count
    return q

from hypothesis import given
from hypothesis.strategies import text

@given(text())
def test_decode_inverts_encode(s):
    assert decode(encode(s)) == s

if __name__ == '__main__':
    test_decode_inverts_encode()