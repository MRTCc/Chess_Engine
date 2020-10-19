import movemodule
import piecesmodule as pcsm
import algebraicnotationmodule as algn

nposition = 0


def white_generator_moves(listpiece):
    for piece in listpiece.whitepieces:
        moves = piece.generatemoves()
        for move in moves:
            yield move
    for pawn in listpiece.whitepawns:
        moves = pawn.generatemoves()
        for move in moves:
            yield move


def black_generator_moves(listpiece):
    for piece in listpiece.blackpieces:
        moves = piece.generatemoves()
        for move in moves:
            yield move
    for pawn in listpiece.blackpawns:
        moves = pawn.generatemoves()
        for move in moves:
            yield move


# TODO Solo per debug
testfile = open("built_tree_test", "w")


class Evaluator:
    def __init__(self, listpiece, nummoves):
        self.listpiece = listpiece
        self.nummoves = nummoves
        self.wkings = 0
        self.bkings = 0
        self.wqueens = 0
        self.bqueens = 0
        self.wrooks = 0
        self.brooks = 0
        self.wbishops = 0
        self.bbishops = 0
        self.wknights = 0
        self.bknights = 0
        self.wpawns = 0
        self.bpawns = 0
        self.wdoubledpawns = 0
        self.bdoubledpawns = 0
        self.wblockedpawns = 0
        self.bblockedpawns = 0
        self._countpieces()
        self._countdoubledpawns()
        self._countblockedpawns()

    def _countpieces(self):
        for piece in self.listpiece.whitepieces:
            if isinstance(piece, pcsm.WhiteKing):
                self.wkings += 1
            elif isinstance(piece, pcsm.WhiteQueen):
                self.wqueens += 1
            elif isinstance(piece, pcsm.WhiteBishop):
                self.wbishops += 1
            elif isinstance(piece, pcsm.WhiteKnight):
                self.wknights += 1
            elif isinstance(piece, pcsm.WhiteRook):
                self.wrooks += 1
        for piece in self.listpiece.blackpieces:
            if isinstance(piece, pcsm.BlackKing):
                self.bkings += 1
            elif isinstance(piece, pcsm.BlackQueen):
                self.bqueens += 1
            elif isinstance(piece, pcsm.BlackBishop):
                self.bbishops += 1
            elif isinstance(piece, pcsm.BlackKnight):
                self.bknights += 1
            elif isinstance(piece, pcsm.BlackRook):
                self.brooks += 1
        self.wpawns = len(self.listpiece.whitepawns)
        self.bpawns = len(self.listpiece.blackpawns)

    def _countdoubledpawns(self):
        for column in algn.columns:
            columncount = 0
            for pawn in self.listpiece.whitepawns:
                if pawn.coordinate.isequalcolumn(column):
                    columncount += 1
            if columncount > 1:
                self.wdoubledpawns += columncount
        for column in algn.columns:
            columncount = 0
            for pawn in self.listpiece.blackpawns:
                if pawn.coordinate.isequalcolumn(column):
                    columncount += 1
            if columncount > 1:
                self.bdoubledpawns += columncount

    def _countblockedpawns(self):
        for pawn in self.listpiece.whitepawns:
            if not pawn.onestepmove():
                self.wblockedpawns += 1
        for pawn in self.listpiece.blackpawns:
            if not pawn.onestepmove():
                self.bblockedpawns += 1

    def __str__(self):
        msg = "Evaluation of position: \n\t"
        for key, value in self.__dict__.items():
            msg += key + " --> "
            msg += str(value) + "\n\t"
        return msg


class GamePosition:
    def __init__(self, listpiece, parent=None, originmove=None):
        self.listpiece = listpiece
        self.parent = parent
        self.originmove = originmove
        self.value = None
        self.moves = []
        self.children = []
        self.movegeneratorfunc = None
        self.enemy_game_position_func = None
        self.ischeckfunc = None

    def ischeckmate(self):
        if self.moves == [] and self.ischeckfunc():
            return True
        else:
            return False

    def isstalemate(self):
        if self.moves == [] and self.ischeckfunc() == False:
            return True
        else:
            return False

    def builtplytree(self, maxply, curply=0):
        global nposition
        nposition += 1

        if self.parent is None:
            msg = "ply: " + str(curply) + " root position"
        else:
            msg = ("ply: " + str(curply) + "\n\t last move: " + str(self.originmove.piece) + " " +
                   self.originmove.fromcell + self.originmove.tocell + "\n\t class: " + self.__class__.__name__ +
                   "\n\t position: " + str(self) + "\n\t parent: " + str(self.parent))
        testfile.write(msg + '\n' + str(self.listpiece))

        for move in self.movegeneratorfunc(pcsm.listpiece):
            self.moves.append(move)
        if self.ischeckmate():
            testfile.write("***************** CHECKMATE - GAME ENDED ************************\n")
            return
        elif self.isstalemate():
            testfile.write("***************** DRAW - GAME ENDED ************************\n")
            return
        if curply >= maxply:
            testfile.write("-------------- max ply -----------------\n")
            return
        for move in self.moves:
            self.listpiece.applymove(move)
            child = self.enemy_game_position_func(self.listpiece, self, move)
            child.builtplytree(maxply, curply + 1)
            self.children.append(child)
            self.listpiece.undomove(move)



    def bestmove(self):
        pass


class WhiteGamePosition(GamePosition):
    def __init__(self, listpiece, parent=None, originmove=None):
        super().__init__(listpiece, parent, originmove)
        self.movegeneratorfunc = white_generator_moves
        self.enemy_game_position_func = BlackGamePosition
        self.ischeckfunc = self.listpiece.iswhitekingincheck


class BlackGamePosition(GamePosition):
    def __init__(self, listpiece, parent=None, originmove=None):
        super().__init__(listpiece, parent, originmove)
        self.movegeneratorfunc = black_generator_moves
        self.enemy_game_position_func = WhiteGamePosition
        self.ischeckfunc = self.listpiece.isblackkingincheck


if __name__ == '__main__':
    import movemodule
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
    whiteKing = pcsm.WhiteKing(d4, wc)
    blackKing = pcsm.BlackKing(a4, bc)
    whitepieces = [whiteKing, pcsm.WhiteQueen(c3, whiteKing, blackKing)]
    whitepawns = [pcsm.WhitePawn(f3, whiteKing, blackKing)]
    blackpawns = [pcsm.BlackPawn(h7, blackKing, whiteKing), pcsm.BlackPawn(h6, blackKing, whiteKing)]
    blackpieces = [blackKing]
    pcsm.listpiece = pcsm.ListPiece(whitepieces, whitepawns, blackpieces, blackpawns)
    print(pcsm.listpiece)

    evaluator = Evaluator(pcsm.listpiece, 0)
    print(evaluator)
