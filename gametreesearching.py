import movemodule
import piecesmodule
import algebraicnotationmodule


def white_generator_moves(listpiece):
    for piece in listpiece.whitepieces:
        moves = piece.generatemoves(l)
        for move in moves:
            yield move
    for pawn in listpiece.whitepawns:
        moves = pawn.generatemoves(l)
        for move in moves:
            yield move


def black_generator_moves(listpiece):
    for piece in listpiece.blackpieces:
        moves = piece.generatemoves(l)
        for move in moves:
            yield move
    for pawn in listpiece.blackpawns:
        moves = pawn.generatemoves(l)
        for move in moves:
            yield move


# TODO Solo per debug
testfile = open("built_tree_test", "w")


class GamePosition:
    def __init__(self, listpiece, parent=None, originmove=None):
        self.listpiece = listpiece
        self.parent = parent
        self.originmove = originmove
        self.value = None
        self.moves = []
        self.children = []
        self.movegenerator = None
        self.enemy_game_position = None
        self.ischeck = None

    def builtplytree(self, maxply, curply=0):
        # DEBUG
        if self.parent is None:
            msg = "ply: " + str(curply) + " root position"
        else:
            msg = ("ply: " + str(curply) + "\n\t last move: " + str(self.originmove.piece) + " " +
                   self.originmove.fromcell + self.originmove.tocell + "\n\t class: " + self.__class__.__name__ +
                    "\n\t position: " + str(self) + "\n\t parent: " + str(self.parent))

        # DEBUG
        testfile.write(msg + '\n' + str(self.listpiece))
        if curply == maxply:
            return
        for move in self.movegenerator(self.listpiece):
            self.moves.append(move)
            self.listpiece.applymove(move)
            child = self.enemy_game_position(self.listpiece, parent=self, originmove=move)
            self.children.append(child)
            child.builtplytree(maxply, curply + 1)
            self.listpiece.undomove(move)
        if not self.moves:
            if self.ischeck():
                testfile.write("************************ CHECKMATE - GAME ENDED ***********************\n")
            else:
                testfile.write("************************ DRAW - GAME ENDED ***********************\n")

    def bestmove(self):
        pass


class WhiteGamePosition(GamePosition):
    def __init__(self, listpiece, parent=None, originmove=None):
        super().__init__(listpiece, parent, originmove)
        self.movegenerator = white_generator_moves
        self.enemy_game_position = BlackGamePosition
        self.ischeck = self.listpiece.iswhitekingincheck


class BlackGamePosition(GamePosition):
    def __init__(self, listpiece, parent=None, originmove=None):
        super().__init__(listpiece, parent, originmove)
        self.movegenerator = black_generator_moves
        self.enemy_game_position = WhiteGamePosition
        self.ischeck = self.listpiece.isblackkingincheck


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
    import movemodule
    import piecesmodule as pi
    from algebraicnotationmodule import (a8, b8, c8, d8, e8, f8, g8, h8,
                                         a7, b7, c7, d7, e7, f7, g7, h7,
                                         a6, b6, c6, d6, e6, f6, g6, h6,
                                         a5, b5, c5, d5, e5, f5, g5, h5,
                                         a4, b4, c4, d4, e4, f4, g4, h4,
                                         a3, b3, c3, d3, e3, f3, g3, h3,
                                         a2, b2, c2, d2, e2, f2, g2, h2,
                                         a1, b1, c1, d1, e1, f1, g1, h1)
    wc = movemodule.CastlingRights(False)
    bc = movemodule.CastlingRights(False)
    whiteKing = pi.WhiteKing(d4, wc)
    blackKing = pi.BlackKing(a4, bc)
    whitepieces = [whiteKing, pi.WhiteQueen(c3, whiteKing, blackKing)]
    whitepawns = []
    blackpawns = []
    blackpieces = [blackKing]
    l = pi.ListPiece(whitepieces, whitepawns, blackpieces, blackpawns)
    whiteKing.listpiece = l
    blackKing.listpiece = l
    # print(l)

    root = WhiteGamePosition(l)

    root.builtplytree(maxply=2, curply=0)


