import gametreesearching as gm
import piecesmodule as pcsm
import evaluationmodule as evm
import movemodule as mvm
from algebraicnotationmodule import (a8, b8, c8, d8, e8, f8, g8, h8,
                                     a7, b7, c7, d7, e7, f7, g7, h7,
                                     a6, b6, c6, d6, e6, f6, g6, h6,
                                     a5, b5, c5, d5, e5, f5, g5, h5,
                                     a4, b4, c4, d4, e4, f4, g4, h4,
                                     a3, b3, c3, d3, e3, f3, g3, h3,
                                     a2, b2, c2, d2, e2, f2, g2, h2,
                                     a1, b1, c1, d1, e1, f1, g1, h1)


class StopSearchSystemExit(SystemExit):
    pass


isrunning = True
nposition = 0


class MinMaxWhiteGamePosition(gm.MinMaxGamePosition):
    def __init__(self, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.iswhiteturn = True
        self.movegeneratorfunc = pcsm.white_generator_moves
        self.enemy_game_position_func = MinMaxBlackGamePosition
        self.ischeckfunc = self.listpiece.iswhitekingincheck
        self.imincheckmatevalue = -gm.checkmatevalue
        self.childrenevaluationfunc = max

    def builtplytreevalue(self, depthleft):
        global nposition
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        if depthleft == 0:
            evaluator = evm.Evaluator(self.listpiece)
            self.value = evaluator()
            msg = self._outputmoves()
            # testfile.write(msg + "\n")
            return
        for move in self.movegeneratorfunc(self.listpiece):
            self.moves.append(move)
        for move in self.moves:
            self.listpiece.applymove(move)
            child = self.enemy_game_position_func(self.listpiece, self)
            try:
                child.builtplytreevalue(depthleft - 1)
            except StopSearchSystemExit:
                self.listpiece.undomove(move)
                raise StopSearchSystemExit
            self.children.append(child)
            self.listpiece.undomove(move)
        if self.imincheckmate():
            self.value = self.imincheckmatevalue
            msg = self._outputmoves()
            # testfile.write(msg + "****** CHECKMATE - GAME ENDED ******\n")
            return
        if self.isstalemate():
            self.value = 0
            msg = self._outputmoves()
            # testfile.write(msg + "****** DRAW - GAME ENDED ******\n")
            return
        values = []
        for child in self.children:
            values.append(child.value)
        bestvalue = self.childrenevaluationfunc(values)
        self.value = bestvalue

    def __str__(self):
        msg = 'Active color: white\n'
        msg += str(self.listpiece)
        return msg


class MinMaxBlackGamePosition(gm.MinMaxGamePosition):
    def __init__(self, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.iswhiteturn = False
        self.movegeneratorfunc = pcsm.black_generator_moves
        self.enemy_game_position_func = MinMaxWhiteGamePosition
        self.ischeckfunc = self.listpiece.isblackkingincheck
        self.imincheckmatevalue = gm.checkmatevalue
        self.childrenevaluationfunc = min

    def builtplytreevalue(self, depthleft):
        global nposition
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        if depthleft == 0:
            evaluator = evm.Evaluator(self.listpiece)
            self.value = evaluator()
            msg = self._outputmoves()
            # testfile.write(msg + "\n")
            return
        for move in self.movegeneratorfunc(self.listpiece):
            self.moves.append(move)
        for move in self.moves:
            self.listpiece.applymove(move)
            child = self.enemy_game_position_func(self.listpiece, self)
            try:
                child.builtplytreevalue(depthleft - 1)
            except StopSearchSystemExit:
                self.listpiece.undomove(move)
                raise StopSearchSystemExit
            self.children.append(child)
            self.listpiece.undomove(move)
        if self.imincheckmate():
            self.value = self.imincheckmatevalue
            msg = self._outputmoves()
            # testfile.write(msg + "****** CHECKMATE - GAME ENDED ******\n")
            return
        if self.isstalemate():
            self.value = 0
            msg = self._outputmoves()
            # testfile.write(msg + "****** DRAW - GAME ENDED ******\n")
            return
        values = []
        for child in self.children:
            values.append(child.value)
        bestvalue = self.childrenevaluationfunc(values)
        self.value = bestvalue

    def __str__(self):
        msg = 'Active color: black\n'
        msg += str(self.listpiece)
        return msg


class Perf:
    def __init__(self):
        pass

    def __call__(self, depth):
        pass


def debug_pos_factory(hashgenerator):
    wc = mvm.CastlingRights()
    bc = mvm.CastlingRights()
    whiteKing = pcsm.WhiteKing(e1, wc)
    blackKing = pcsm.BlackKing(e8, bc)
    whitepieces = [pcsm.WhiteRook(a1, whiteKing, blackKing), pcsm.WhiteKnight(b1, whiteKing, blackKing),
                   pcsm.WhiteBishop(c1, whiteKing, blackKing), pcsm.WhiteQueen(d1, whiteKing, blackKing),
                   whiteKing, pcsm.WhiteBishop(f1, whiteKing, blackKing), pcsm.WhiteKnight(g1, whiteKing, blackKing),
                   pcsm.WhiteRook(h1, whiteKing, blackKing)]
    whitepawns = [pcsm.WhitePawn(a2, whiteKing, blackKing), pcsm.WhitePawn(b2, whiteKing, blackKing),
                  pcsm.WhitePawn(c2, whiteKing, blackKing), pcsm.WhitePawn(d2, whiteKing, blackKing),
                  pcsm.WhitePawn(e2, whiteKing, blackKing), pcsm.WhitePawn(f2, whiteKing, blackKing),
                  pcsm.WhitePawn(g2, whiteKing, blackKing), pcsm.WhitePawn(h2, whiteKing, blackKing)]
    blackpieces = [pcsm.BlackRook(a8, blackKing, whiteKing), pcsm.BlackKnight(b8, blackKing, whiteKing),
                   pcsm.BlackBishop(c8, blackKing, whiteKing), pcsm.BlackQueen(d8, blackKing, whiteKing),
                   blackKing, pcsm.BlackBishop(f8, blackKing, whiteKing), pcsm.BlackKnight(g8, blackKing, whiteKing),
                   pcsm.BlackRook(h8, blackKing, whiteKing)]
    blackpawns = [pcsm.BlackPawn(a7, blackKing, whiteKing), pcsm.BlackPawn(b7, blackKing, whiteKing),
                  pcsm.BlackPawn(c7, blackKing, whiteKing), pcsm.BlackPawn(d7, blackKing, whiteKing),
                  pcsm.BlackPawn(e7, blackKing, whiteKing), pcsm.BlackPawn(f7, blackKing, whiteKing),
                  pcsm.BlackPawn(g7, blackKing, whiteKing), pcsm.BlackPawn(h7, blackKing, whiteKing)]
    pcsm.listpiece = pcsm.listpiecefactory(whitepieces, whitepawns, blackpieces, blackpawns, hashgenerator, True)
    return pcsm.listpiece, whiteKing, blackKing


if __name__ == '__main__':
    listpiece, whiteking, blackking = debug_pos_factory(None)
    gameposition = MinMaxWhiteGamePosition(listpiece)
    print("Tocca a bianco:\n" + str(pcsm.listpiece))
    gameposition.calcbestmove(2)
