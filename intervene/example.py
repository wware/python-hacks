# Normal:      python example.py
# With debug:  INJECT=elsewhere python example.py

import os
import sys
import importlib


def subroutine(n):
    for i in range(n):
        print(f"Main loop: {i=} {n=}")


def main():
    subroutine(3)
    subroutine(4)


if __name__ == '__main__':
    # import intervene

    where = os.environ.get('INJECT', None)
    if where is not None:
        sys.path.insert(0, '.')
        importlib.import_module(where).main()
    # intervene.fuss('elsewhere')

    main()
