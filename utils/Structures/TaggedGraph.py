import matplotlib.pyplot as plt
import json

from Iris.utils.Structures.Lifo import Lifo
from Iris.utils.FileProcessing.FileManager import FileManager
from Iris.utils.Utils import Utils
from Iris.utils.Structures.XAbleObject import SerializableObject


class TaggedLink(SerializableObject):
    def __init__(self, vertex_index, tag=None):
        self.vertex_index = vertex_index
        self.tag = tag

    def __eq__(self, other):
        return self.vertex_index == other.vertex_index

    def to_dict(self):
        super().to_dict(vertex_index=self.vertex_index, tag=self.tag)


class TaggedGraph(SerializableObject):
    def __init__(self, V=None, A=None):
        """
        V->list of vertices  [x, y, ...]
                              0  1   
        A->list of adjacency [[...], [...], ...]
                                0      1     
        """
        if V:
            self.V = V
        else:
            self.V = []

        if A:
            self.A = A
        else:
            self.A = []

    def get_index(self, x):
        return self.V.index(x)

    def get_vertex(self, ix):
        return self.V[ix]

    def set_index(self, ix, value):
        self.V[ix] = value

    def set_vertex(self, x, value):
        ix = self.get_index(x)
        self.set_index(ix, value)

    def adjacent(self, x, y):
        ix = self.get_index(x)
        iy = self.get_index(y)

        return TaggedLink(iy) in self.A[ix]

    def neighbors(self, x):
        ix = self.get_index(x)

        return [self.V[tagged_link.vertex_index] for tagged_link in self.A[ix]]

    def in_neighbors(self, x):
        ix = self.get_index(x)
        n = []
        for (iy, adj) in enumerate(self.A):
            if TaggedLink(ix) in adj:
                n.append(self.V[iy])

        return n

    def unoriented_neighbors(self, x):
        neighbors = self.neighbors(x)
        return neighbors + [
            x for x in self.in_neighbors(x) if x not in neighbors
        ]

    def order(self):
        return len(self.V)

    def out_degree(self, x):
        ix = self.get_index(x)
        return len(self.A[ix])

    def in_degree(self, x):
        ix = self.get_index(x)
        d = 0
        for adj in self.A:
            if TaggedLink(ix) in adj:
                d += 1

        return d

    def add_vertex(self, x):
        if x not in self.V:
            self.V.append(x)
            self.A.append([])

    def add_vertices(self, verticies):
        for x in verticies:
            self.add_vertex(x)

    def remove_vertex(self, x):
        ix = self.get_index(x)
        for adj in self.A:
            for iy, tagged_link in enumerate(adj):
                if tagged_link.vertex_index == ix:
                    del adj[iy]
        del self.V[ix]
        del self.A[ix]

    def remove_verticies(self, verticies):
        for x in verticies:
            self.remove_vertex(x)

    def add_link(self, x, y, tag=None):
        ix = self.get_index(x)
        iy = self.get_index(y)

        if TaggedLink(iy) not in self.A[ix]:
            self.A[ix].append(TaggedLink(iy, tag))

    def add_links(self, links):
        for x, y in links:
            self.add_link(x, y)

    def remove_link(self, x, y):
        ix = self.get_index(x)
        iy = self.get_index(y)

        # TODO optimization ?
        for i, tagged_link in enumerate(self.A[ix]):
            if tagged_link.vertex_index == iy:
                self.A[ix].pop(i)

    def remove_links(self, links):
        for x, y in links:
            self.remove_link(x, y)

    def bfs(self):
        remainders = Lifo()
        if self.order() > 0:
            remainders.push(self.V[0])
        viewed = Lifo()

        while len(remainders) > 0:
            h = remainders.pop()
            if h not in viewed:
                viewed.push(h)
                for n in self.neighbors(h):
                    remainders.push(n)

        return viewed

    def is_connected(self):
        return len(self.bfs()) == self.order()

    def weak_bfs(self):
        remainders = Lifo()
        if self.order() > 0:
            remainders.push(self.V[0])
        viewed = Lifo()

        while len(remainders) > 0:
            h = remainders.pop()
            if h not in viewed:
                viewed.push(h)
                for n in self.unoriented_neighbors(h):
                    remainders.push(n)

        return viewed

    def is_weak_connected(self):
        return len(self.weak_bfs()) == self.order()

    def __getitem__(self, x):
        return self.A[self.get_index(x)]

    def __repr__(self):
        return repr(self.to_dict())

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self):
        return super().to_dict(V=self.V, A=self.A)
