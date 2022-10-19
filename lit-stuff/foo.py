"""
# Docstring for the file foo.py

Let's try to do some Markdown in docstrings and see if we can
get Pydoc to do something intelligent with it.
"""

def add(x, y):
    """
    This is an example of Google style.

    Args:
        x: This is the first param.
        y: This is a second param.

    Returns:
        The sum of x and y.

    Raises:
        KeyError: Raises an exception.
    """
    return x + y


if __name__ == '__main__':
    print(add(3, 4))
