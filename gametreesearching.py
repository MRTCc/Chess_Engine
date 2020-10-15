import movemodule
import piecesmodule
import algebraicnotationmodule


class GameTree:
    def __init__(self, position, children=None, parent=None):
        self.position = position
        self.value = 0
        self.children = children or []
        self.parent = parent

    def add_child(self, gametree):
        if not isinstance(gametree, GameTree):
            raise AttributeError("GameTree.add_child accept only GameTree instances!")
        self.children.append(gametree)

    def is_root(self):
        return self.parent is None

    def is_leaf(self):
        return not self.children

    def __str__(self):
        if self.is_leaf():
            return str(self.position)
        return '{data} [{children}]'.format(data=self.position, children=', '.join(map(str, self.children)))

class GameTreeConstructor:
    def __init__(self, gametree, max_depth, movegenerator):
        self.gametree = gametree
        self.max_depth = max_depth
        self.movegenerator = movegenerator

    def builtgametree(self, depth=0, position=None):
        pass

if __name__ == '__main__':
    root = GameTree('foo')
    node = GameTree('nodo1')
    root.add_child(node)
    leaf = GameTree('im a leaf')
    node.add_child(leaf)
    print(root)



