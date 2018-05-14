import os

from linalg import Vector
from splines import Tile


def try_tile():
    t = Tile(
        Vector(0, 0, 1), Vector(0, 0, 1), Vector(1, 0, 0), Vector(0, 1, 0),
        Vector(0, -1, 1), Vector(-1, 0, 1),
        Vector(0, 0, 1), Vector(1, -1, -1),
        Vector(2, 0, -1), Vector(0, 2, -1),
        Vector(-1, 1, 0), Vector(0, 0, 1)
    )
    fnfmt = "tile{0}.dat"
    ribs = 12
    fns = t.to_gnuplot(fnfmt, ribs)
    outf = open("gp.cmd", "w")
    outf.write(
        'plot ' +
        ', '.join(['"{0}" with lines notitle'.format(fn) for fn in fns]) +
        '; pause 10;'
    )
    outf.close()
    os.system("gnuplot gp.cmd")
    for f in (["gp.cmd"] + fns):
        os.remove(f)


if __name__ == "__main__":
    try_tile()
