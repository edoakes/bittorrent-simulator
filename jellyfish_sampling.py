import random
import argparse

parser = argparse.ArgumentParser(description='Simulate incrementally generating a random graph')
parser.add_argument('--n', default=50, type=int, help='number of vertices')
parser.add_argument('--k', default=10, type=int, help='edges per vertex')

class Node(object):
    def __init__(self, name, degree):
        self.name = name
        self.degree = degree
        self.neighbors = {}
        self.connects = 0
        self.disconnects = 0

    def is_full():
        return len(self.neighbors) >= self.degree

    def connect(self, other):
        if self.is_full() or other.is_full():
            return False

        #TODO
        if other.name in self.neighbors:
            return False
        if len(self.neighbors) == self.degree or len(other.neighbors) == self.degree:
            return False
        self.neighbors[other.name] = other
        other.neighbors[self.name] = self

        self.connects += 1
        other.connects += 1
        return True

    def disconnect(self, other):
        if other.name not in self.neighbors:
            return False
        del self.neighbors[other.name]
        del other.neighbors[self.name]

        self.disconnects += 1
        other.disconnects += 1
        return True

    def reconnect(self, new_node):
        old_node = self.neighbors[random.choice(list(self.neighbors))]
        if not self.disconnect(old_node):
            raise RuntimeError("couldn't disconnect existing connected node")

        if not self.connect(new_node):
            return False
        if not old_node.connect(new_node):
            if not self.disconnect(new_node):
                raise RuntimeError("couldn't disconnect newly connected node")
            return False

        return True

    def add_edges(self, candidates):
        candidates = random.sample(candidates, len(candidates))

        for candidate in candidates:
            if len(self.neighbors) == self.degree:
                break
            if not self.connect(candidate):
                candidate.reconnect(self)

    def print_summary(self):
        print(self.disconnects)

class Graph(object):
    def __init__(self, n, k):
        self.nodes = []

        for i in range(n):
            new_node = Node(i, k)
            new_node.add_edges(self.nodes)
            self.nodes.append(new_node)

    def print_summary(self):
        for node in self.nodes:
            node.print_summary()

def main(args):
    graph = Graph(args.n, args.k)
    graph.print_summary()

if __name__== "__main__":
     main(parser.parse_args())
