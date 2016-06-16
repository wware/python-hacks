import pprint
from rdb import dig

def gen_primes(n):
    yield 2
    known = [2]
    for i in range(3, n, 2):
        composite = False
        for j in known:
            if (i % j) == 0:
                composite = True
                break
            if j * j > i:
                break
        if not composite:
            known.append(i)
            yield i

x = {
    'primes': [z for z in gen_primes(100)],
    'string': 'Four score and seven years ago...',
    'generator': gen_primes(100)
}

pprint.pprint(dig(x, 3))
