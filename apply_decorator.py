import ast
import inspect
import os
import sys


def hack_function(node):
    if isinstance(node, ast.FunctionDef) and node.name != 'decorator':
        print(f"Hacking {node.name}")
        node.decorator_list.insert(0, ast.Name(id="decorator", ctx=ast.Load()))
        for node2 in ast.walk(node):
            if node2 is not node:
               hack_function(node2)


def main():
    fn = sys.argv[1]
    assert os.path.isfile(fn) and fn.endswith(".py"), fn
    source_file = open(fn, "r")
    source_code = source_file.read()
    source_file.close()
    tree = ast.parse(source_code)
    for node in tree.body:
        hack_function(node)
    with open(fn, "w") as source_file:
        source_file.write(ast.unparse(tree))


if __name__ == "__main__":
    main()
