import ast

"""
Gather up all the Markdown in a source file's various docstrings.
Put it together into a big Markdown doc. Give it some '#' things.
"""

def foo(x, y):
    """Addition"""
    return x + y


class MyClass:
    """some docstring stuff on the class definition"""
    def mymethod(self, u):
        """more docstring stuff on the method"""
        return u * 3


def examine_ast_expr(e: ast.Expr, parent=None):
    assert isinstance(e, ast.Expr), e
    v = getattr(e, 'value', None)
    if isinstance(v, ast.Constant):
        z = v and getattr(v, 'n', None)
        if isinstance(z, str):
            if parent is not None:
                z += f" (parent: {parent})"
            print(z)


def dig_into(t, parent=None):
    # print(f"+ {t}")
    if isinstance(t, ast.Expr):
        examine_ast_expr(t, parent)
    elif hasattr(t, 'body'):
        for x in t.body:
            dig_into(x, t)

dig_into(ast.parse(open(__file__).read()))
