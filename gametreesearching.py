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
        self.wisolatedpawns = 0
        self.bisolatedpawns = 0
        self.mobility = 0
        self._countpieces()
        self._countdoubledpawns()
        self._countblockedpawns()
        self._countisolatedpawns(self.listpiece.whitepawns)
        self._countisolatedpawns(self.listpiece.blackpawns)
        self._countmobility(nummoves)

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
        for column in algn.ranks:
            columncount = 0
            for pawn in self.listpiece.whitepawns:
                if pawn.coordinate.isequalrank(column):
                    columncount += 1
            if columncount > 1:
                self.wdoubledpawns += columncount
        for column in algn.ranks:
            columncount = 0
            for pawn in self.listpiece.blackpawns:
                if pawn.coordinate.isequalrank(column):
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

    def _countisolatedpawns(self, pawnslist):
        for pawn in pawnslist:
            issxisolated = True
            isdxisolated = True
            pawnrank = pawn.coordinate.getrank()
            index = algn.ranks.index(pawnrank)
            try:
                sxrank = algn.ranks[index - 1]
                for sxpawn in pawnslist:
                    if sxpawn == pawn:
                        continue
                    if sxpawn.coordinate.isequalrank(sxrank):
                        issxisolated = False
            except IndexError:
                pass
            try:
                dxrank = algn.ranks[index + 1]
                for dxpawn in pawnslist:
                    if dxpawn == pawn:
                        continue
                    if dxpawn.coordinate.isequalrank(dxrank):
                        isdxisolated = False
            except IndexError:
                pass
            if issxisolated and isdxisolated:
                if pawnslist == self.listpiece.whitepawns:
                    self.wisolatedpawns += 1
                elif pawnslist == self.listpiece.blackpawns:
                    self.bisolatedpawns += 1
                else:
                    raise AttributeError

    def _countmobility(self, nummoves):
        if nummoves > 5:
            self.mobility = 1
        else:
            self.mobility = -1

    def __call__(self):
        pawnmaterial = (self.wpawns - self.bpawns) * 1
        rookmaterial = (self.wrooks - self.brooks) * 5
        knightmaterial = (self.wknights - self.bknights) * 3
        bishopmaterial = (self.wbishops - self.bbishops) * 3
        queenmaterial = (self.wqueens - self.bqueens) * 9
        kingmaterial = (self.wkings - self.bkings) * 500
        doubledpawns = (self.wdoubledpawns - self.bdoubledpawns) * 0.5
        isolatedpawns = (self.wisolatedpawns - self.bisolatedpawns) * 0.5
        blockedpawns = (self.wblockedpawns - self.bblockedpawns) * 0.5
        mobility = self.mobility

        self.evaluation = (pawnmaterial + rookmaterial + knightmaterial + bishopmaterial + queenmaterial + kingmaterial
                           + doubledpawns + isolatedpawns + blockedpawns + mobility)
        return self.evaluation

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
        self.imincheckmatevalue = None
        self.childrenevaluationfunc = None

    def imincheckmate(self):
        if self.moves == [] and self.ischeckfunc():
            return True
        else:
            return False

    def isstalemate(self):
        if len(self.listpiece.whitepieces) == 1 and len(self.listpiece.blackpieces) == 1:
            return True
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
        if self.imincheckmate():
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

    def __lt__(self, other):
        if self.value < other.value:
            return True
        else:
            return False

    def __gt__(self, other):
        if self.value > other.value:
            return True
        else:
            return False

    def __eq__(self, other):
        if self.value == other.value:
            return True
        else:
            return False

    def builtplytreevalue(self, maxply, curply=0):
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
        if self.imincheckmate():
            self.value = self.imincheckmatevalue
            testfile.write("position value : " + str(self.value) + '\n')
            testfile.write("***************** CHECKMATE - GAME ENDED ************************\n")
            return

        elif self.isstalemate():
            self.value = 0
            testfile.write("position value : " + str(self.value) + '\n')
            testfile.write("***************** DRAW - GAME ENDED ************************\n")
            return
        if curply >= maxply:
            evaluator = Evaluator(self.listpiece, len(self.moves))
            self.value = evaluator()
            testfile.write("position value : " + str(self.value) + '\n')
            testfile.write("-------------- max ply -----------------\n")
            return
        for move in self.moves:
            self.listpiece.applymove(move)
            child = self.enemy_game_position_func(self.listpiece, self, move)
            child.builtplytreevalue(maxply, curply + 1)
            self.children.append(child)
            self.listpiece.undomove(move)
        self.value = self.childrenevaluationfunc((child.value for child in self.children))
        testfile.write(str(self) + " --> " + "position value : " + str(self.value) + '\n')
        bestchild = self.childrenevaluationfunc(self.children)
        indexbestchild = self.children.index(bestchild)
        bestmove = self.moves[indexbestchild]
        testfile.write(str(self) + " --> " + "position value : " + str(self.value) + "\n\t best move: " + str(bestmove) +
                       '\n')
        return bestmove


class WhiteGamePosition(GamePosition):
    def __init__(self, listpiece, parent=None, originmove=None):
        super().__init__(listpiece, parent, originmove)
        self.movegeneratorfunc = white_generator_moves
        self.enemy_game_position_func = BlackGamePosition
        self.ischeckfunc = self.listpiece.iswhitekingincheck
        self.imincheckmatevalue = -1000
        self.childrenevaluationfunc = max


class BlackGamePosition(GamePosition):
    def __init__(self, listpiece, parent=None, originmove=None):
        super().__init__(listpiece, parent, originmove)
        self.movegeneratorfunc = black_generator_moves
        self.enemy_game_position_func = WhiteGamePosition
        self.ischeckfunc = self.listpiece.isblackkingincheck
        self.imincheckmatevalue = 1000
        self.childrenevaluationfunc = min


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
    whiteKing = pcsm.WhiteKing(c4, wc)
    blackKing = pcsm.BlackKing(a4, bc)
    whitepieces = [whiteKing, pcsm.WhiteQueen(b8, whiteKing, blackKing)]
    whitepawns = []
    blackpawns = []
    blackpieces = [blackKing, pcsm.BlackRook(h8, blackKing, whiteKing)]
    pcsm.listpiece = pcsm.listpiecefactory(whitepieces, whitepawns, blackpieces, blackpawns)
    print(pcsm.listpiece)

    root = BlackGamePosition(pcsm.listpiece)
    root.builtplytreevalue(2)
    print(nposition)
