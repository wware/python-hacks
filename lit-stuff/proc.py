import os
import re


class Parser(object):
    def __init__(self, infile):
        self._lines = open(infile).readlines()
        self._sourcefile = None
        self._sourcelines = None
        self._previous = None

    def process_lines(self):
        for L in self._lines:
            handler = m = None
            for name in dir(self):
                prefix, hname = name[:7], name[7:]
                if prefix != 'handle_':
                    continue
                handler = getattr(self, name)
                pattern = r"^\s*" + hname.upper() + r"\s+(.+)\s*$"
                #print((pattern, hname))
                m = re.match(pattern, L)
                if m:
                    words = re.split(r"\s+", m.group(1))
                    handler(words)
                    break
            self._previous = handler
            if m is None:
                print(L.rstrip())

    def get_handlers(self):
        return [
            getattr(self, name) for name in dir(self)
            if name.startswith("handle_")
        ]

    def handle_sourcefile(self, words):
        r"^\s*SOURCEFILE\s+(\S+)"
        self._sourcefile = f = words[0]
        if os.path.isfile(f):
            self._sourcelines = open(f).readlines()
            self._sourceindex = 1

    def find_pattern(self, pattern, start=None):
        if self._sourcelines is None:
            return None
        start = self._sourceindex if start is None else start
        for i in range(start, len(self._sourcelines)):
            if re.search(pattern, self._sourcelines[i-1]):
                self._sourceindex = i
                return i
            i += 1

    def handle_after(self, words):
        r"^\s*AFTER\s+(\S+)"
        pattern = r"\s+".join(words)
        self.find_pattern(pattern)

    def handle_include(self, words):
        r"^\s*INCLUDE\s+(\S+)"
        # how to handle "@property" ???
        pattern = r"\s+".join(words)
        m = self.find_pattern(pattern)
        m_indent = re.match(r"^(\s*)" + pattern, self._sourcelines[m-1]).group(1)
        pattern2 = r'^' + m_indent + '\S+'
        n = self.find_pattern(pattern2, m + 1)
        mylines = []
        for j in range(m, n-1):
            L = self._sourcelines[j-1].rstrip()
            if L:
                mylines.append((j, L))
        print("```python")
        for x in mylines:
            print(x[1])
        print("```")
        # print(f"include {words}")

    def handle_rdf(self, words):
        r"^\s*RDF\s+(.*)"
        if self._previous is self.handle_include:
            # this refers to the previous python object
            pass
        print(f"rdf {words}")


parser = Parser("README.md")
parser.process_lines()
