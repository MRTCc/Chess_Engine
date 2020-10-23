import movemodule as mvm
import piecesmodule as pcsm
import threading
import algebraicnotationmodule as algn
from algebraicnotationmodule import (a8, b8, c8, d8, e8, f8, g8, h8,
                                     a7, b7, c7, d7, e7, f7, g7, h7,
                                     a6, b6, c6, d6, e6, f6, g6, h6,
                                     a5, b5, c5, d5, e5, f5, g5, h5,
                                     a4, b4, c4, d4, e4, f4, g4, h4,
                                     a3, b3, c3, d3, e3, f3, g3, h3,
                                     a2, b2, c2, d2, e2, f2, g2, h2,
                                     a1, b1, c1, d1, e1, f1, g1, h1)


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


def startpos_factory():
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
    pcsm.listpiece = pcsm.listpiecefactory(whitepieces, whitepawns, blackpieces, blackpawns)
    pcsm.listpiece.updatecastlingrights()
    return pcsm.listpiece


def debug_pos_factory():
    wc = movemodule.CastlingRights()
    bc = movemodule.CastlingRights()
    whiteKing = pcsm.WhiteKing(e1, wc)
    blackKing = pcsm.BlackKing(e8, bc)
    whitepieces = [whiteKing, pcsm.WhiteRook(a1, whiteKing, blackKing),
                   pcsm.WhiteKnight(h5, whiteKing, blackKing)]
    whitepawns = [pcsm.WhitePawn(a2, whiteKing, blackKing), pcsm.WhitePawn(b2, whiteKing, blackKing),
                  pcsm.WhitePawn(c2, whiteKing, blackKing), pcsm.WhitePawn(d2, whiteKing, blackKing),
                  pcsm.WhitePawn(e2, whiteKing, blackKing), pcsm.WhitePawn(f2, whiteKing, blackKing),
                  pcsm.WhitePawn(g2, whiteKing, blackKing), pcsm.WhitePawn(h2, whiteKing, blackKing)]
    blackpieces = [blackKing, pcsm.BlackRook(a8, blackKing, whiteKing),
                   pcsm.BlackKnight(g7, blackKing, whiteKing)]
    blackpawns = [pcsm.BlackPawn(a7, blackKing, whiteKing), pcsm.BlackPawn(b7, blackKing, whiteKing),
                  pcsm.BlackPawn(c7, blackKing, whiteKing), pcsm.BlackPawn(d7, blackKing, whiteKing),
                  pcsm.BlackPawn(e7, blackKing, whiteKing), pcsm.BlackPawn(f7, blackKing, whiteKing),
                  pcsm.BlackPawn(g7, blackKing, whiteKing), pcsm.BlackPawn(h7, blackKing, whiteKing)]
    pcsm.listpiece = pcsm.listpiecefactory(whitepieces, whitepawns, blackpieces, blackpawns)
    return pcsm.listpiece


class UciMoveSetter:
    def __init__(self, gameposition, strmoves):
        self.gameposition = gameposition
        self.strmoves = strmoves

    def movefactory(self, piece, fromcell, tocell, capturedpiece, iswhiteturn):
        if isinstance(piece, pcsm.WhiteKing) and fromcell == e1 and tocell == g1:
            # arrocco corto re bianco
            move = mvm.whiteKingsideCastlingFactory()
        elif isinstance(piece, pcsm.WhiteKing) and fromcell == e1 and tocell == d1:
            # arrocco lungo re bianco
            move = mvm.whiteQueensideCastlingFactory(False)
        elif isinstance(piece, pcsm.BlackKing) and fromcell == e8 and tocell == g8:
            # arrocco corto re nero
            move = mvm.blackKingsideCastlingFactory()
        elif isinstance(piece, pcsm.BlackKing) and fromcell == e8 and tocell == d8:
            # arrocco lungo re nero
            move = mvm.blackQueensideCastlingFactory(False)
        elif isinstance(piece, pcsm.Pawn) and capturedpiece is not None and piece.promotionfile == tocell.fileint:
            # promozione con cattura
            promotionto = piece.mypromotiontofactory(tocell)
            if iswhiteturn:
                move = mvm.whiteMoveCapturePromotionFactory(piece, fromcell, tocell, capturedpiece, promotionto, False)
            else:
                move = mvm.blackMoveCapturePromotionFactory(piece, fromcell, tocell, capturedpiece, promotionto, False)
        elif isinstance(piece, pcsm.Pawn) and piece.promotionfile == tocell.fileint:
            # promozione
            promotionto = piece.mypromotiontofactory(tocell)
            if iswhiteturn:
                move = mvm.whiteMovePromotionFactory(piece, fromcell, tocell, promotionto, False)
            else:
                move = mvm.blackMovePromotionFactory(piece, fromcell, tocell, promotionto, False)
        elif capturedpiece is not None:
            # cattura
            if iswhiteturn:
                move = mvm.whiteMoveCaptureFactory(piece, fromcell, tocell, capturedpiece, False)
            else:
                move = mvm.blackMoveCaptureFactory(piece, fromcell, tocell, capturedpiece, False)
        else:
            # movimento semplice
            if iswhiteturn:
                move = mvm.whiteMoveFactory(piece, fromcell, tocell, False)
            else:
                move = mvm.blackMoveFactory(piece, fromcell, tocell, False)

        return move

    def __call__(self):
        iswhiteturn = True
        for strmove in self.strmoves:
            fromcell = algn.str_to_algebraic(strmove[0:2])
            tocell = algn.str_to_algebraic(strmove[2:4])
            piece = self.gameposition.listpiece.getpiecefromcoordinate(fromcell)
            capturedpiece = self.gameposition.listpiece.getpiecefromcoordinate(tocell)
            move = self.movefactory(piece, fromcell, tocell, capturedpiece, iswhiteturn)
            self.gameposition.listpiece.applymove(move)
            iswhiteturn = not iswhiteturn


class FenStrParser:
    def __init__(self):
        self.whiteletters = ('R', 'N', 'B', 'Q', 'K', 'P')
        self.blackletters = ('r', 'n', 'b', 'q', 'k', 'p')

    def _parsecastlingrights(self, fencastling):
        if '-' in fencastling:
            wcastlingrights = mvm.CastlingRights(False, False, False, False, False, False)
            bcastlingrights = mvm.CastlingRights(False, False, False, False, False, False)
            return wcastlingrights, bcastlingrights
        kingsidecastling = 'K' in fencastling
        queensidecastling = 'Q' in fencastling
        if kingsidecastling and queensidecastling:
            wcastlingrights = mvm.CastlingRights()
        elif kingsidecastling and not queensidecastling:
            wcastlingrights = mvm.CastlingRights()
            wcastlingrights.setonlykingcastling()
        elif not kingsidecastling and queensidecastling:
            wcastlingrights = mvm.CastlingRights()
            wcastlingrights.setonlyqueencastling()
        else:
            wcastlingrights = mvm.CastlingRights(False, False, False, False, False, False)
        kingsidecastling = 'k' in fencastling
        queensidecastling = 'q' in fencastling
        if kingsidecastling and queensidecastling:
            bcastlingrights = mvm.CastlingRights()
        elif kingsidecastling and not queensidecastling:
            bcastlingrights = mvm.CastlingRights()
            bcastlingrights.setonlykingcastling()
        elif not kingsidecastling and queensidecastling:
            bcastlingrights = mvm.CastlingRights()
            bcastlingrights.setonlyqueencastling()
        else:
            bcastlingrights = mvm.CastlingRights(False, False, False, False, False, False)
        return wcastlingrights, bcastlingrights

    def _isboardvalid(self, boardstring):
        rankcounter = 0
        for char in boardstring:
            if char in ('1', '2', '3', '4', '5', '6', '7', '8'):
                rankcounter += int(char)
            elif char == '/':
                if rankcounter != 8:
                    raise ValueError('Fen string not valid: invalid first field!!!')
                rankcounter = 0
            elif char in self.whiteletters + self.blackletters:
                rankcounter += 1
            else:
                raise ValueError("Not valid character in first field's string")

    def _parsekings(self, boardstring, wcastlingrights, bcastlingrights):
        index = 0
        whitekingcoordinate = None
        blackkingcoordinate = None
        for char in boardstring:
            if char in ('1', '2', '3', '4', '5', '6', '7', '8'):
                index += int(char) - 1
            elif char == '/':
                continue
            elif char == 'K':
                whitekingcoordinate = algn.celllist[index]
            elif char == 'k':
                blackkingcoordinate = algn.celllist[index]
            index += 1
        if whitekingcoordinate is None or blackkingcoordinate is None:
            raise ValueError("No king on the board!!!")
        whiteking = pcsm.WhiteKing(whitekingcoordinate, wcastlingrights)
        blackking = pcsm.BlackKing(blackkingcoordinate, bcastlingrights)
        return whiteking, blackking

    def _parsepieces(self, boardstring, whiteking, blackking):
        index = 0
        whitepieces = []
        whitepawns = []
        blackpieces = []
        blackpawns = []
        for char in boardstring:
            coordinate = algn.celllist[index]
            if char in ('1', '2', '3', '4', '5', '6', '7', '8'):
                index += int(char) - 1
            elif char == '/':
                continue
            elif char == 'R':
                whitepieces.append(pcsm.WhiteRook(coordinate, whiteking, blackking))
            elif char == 'N':
                whitepieces.append(pcsm.WhiteKnight(coordinate, whiteking, blackking))
            elif char == 'B':
                whitepieces.append(pcsm.WhiteBishop(coordinate, whiteking, blackking))
            elif char == 'Q':
                whitepieces.append(pcsm.WhiteQueen(coordinate, whiteking, blackking))
            elif char == 'P':
                whitepawns.append(pcsm.WhitePawn(coordinate, whiteking, blackking))
            elif char == 'r':
                blackpieces.append(pcsm.BlackRook(coordinate, blackking, whiteking))
            elif char == 'n':
                blackpieces.append(pcsm.BlackKnight(coordinate, blackking, whiteking))
            elif char == 'b':
                blackpieces.append(pcsm.BlackBishop(coordinate, blackking, whiteking))
            elif char == 'q':
                blackpieces.append(pcsm.BlackQueen(coordinate, blackking, whiteking))
            elif char == 'p':
                blackpawns.append(pcsm.BlackPawn(coordinate, blackking, whiteking))
            index += 1
        whitepieces.append(whiteking)
        blackpieces.append(blackking)
        return whitepieces, whitepawns, blackpieces, blackpawns

    def _parsergameposition(self, colorstring, listpiece):
        if len(colorstring) != 1:
            raise ValueError('Not a valid string fen color!!!')
        if colorstring == 'w':
            gameposition = WhiteGamePosition(listpiece)
        elif colorstring == 'b':
            gameposition = BlackGamePosition(listpiece)
        else:
            raise ValueError('Not a valid string fen color!!!')
        return gameposition

    def _parserenpassant(self, enpassantstr, listpiece):
        if enpassantstr == '-':
            return
        enpcoordinate = algn.str_to_algebraic(enpassantstr)
        if enpcoordinate not in algn.enpassantlist:
            raise ValueError("Not valid enpassant square!!!")
        if enpcoordinate.fileint == 3:
            if len(listpiece.whitepawns) <= 0:
                raise ValueError("No white pawns in game!!!")
            filestep = listpiece.whitepawns[0].filestep
        else:
            if len(listpiece.blackpawns) <= 0:
                raise ValueError("No black pawns in game!!!")
            filestep = listpiece.whitepawns[0].filestep
        coordinate = enpcoordinate.sumcoordinate(0, filestep)
        piece = listpiece.getpiecefromcoordinate(coordinate)
        if piece is None:
            raise ValueError("No enpassant-pawn at the coordinate inserted!!!")
        piece.enpassantthreat = True
        # print("En passant pawn: ", piece, "at :", piece.coordinate)

    def __call__(self, fenstr):
        tokens = fenstr.split()
        if len(tokens) != 6:
            raise ValueError("Invalid FEN string!!!")
        self._isboardvalid(tokens[0])
        wcastlingrights, bcastlingrights = self._parsecastlingrights(tokens[2])
        whiteking, blackking = self._parsekings(tokens[0], wcastlingrights, bcastlingrights)
        whitepieces, whitepawns, blackpieces, blackpawns = self._parsepieces(tokens[0], whiteking, blackking)
        pcsm.listpiece = pcsm.listpiecefactory(whitepieces, whitepawns, blackpieces, blackpawns)
        pcsm.listpiece.updatecastlingrights()
        self._parserenpassant(tokens[3], pcsm.listpiece)
        gameposition = self._parsergameposition(tokens[1], pcsm.listpiece)
        # print(gameposition)
        # TODO al momento, ignoro gli altri due campi fen
        return gameposition


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

    def builtplytreevalue1(self, maxply, curply=0):
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

    def builtplytreevalue(self, maxply, curply=0):
        global nposition
        nposition += 1
        for move in self.movegeneratorfunc(pcsm.listpiece):
            self.moves.append(move)
        if self.imincheckmate():
            self.value = self.imincheckmatevalue
            return

        elif self.isstalemate():
            self.value = 0
            return
        if curply >= maxply:
            evaluator = Evaluator(self.listpiece, len(self.moves))
            self.value = evaluator()
            return
        for move in self.moves:
            self.listpiece.applymove(move)
            child = self.enemy_game_position_func(self.listpiece, self, move)
            child.builtplytreevalue(maxply, curply + 1)
            self.children.append(child)
            self.listpiece.undomove(move)
        self.value = self.childrenevaluationfunc((child.value for child in self.children))
        bestchild = self.childrenevaluationfunc(self.children)
        indexbestchild = self.children.index(bestchild)
        bestmove = self.moves[indexbestchild]
        return bestmove


class WhiteGamePosition(GamePosition):
    def __init__(self, listpiece, parent=None, originmove=None):
        super().__init__(listpiece, parent, originmove)
        self.movegeneratorfunc = white_generator_moves
        self.enemy_game_position_func = BlackGamePosition
        self.ischeckfunc = self.listpiece.iswhitekingincheck
        self.imincheckmatevalue = -1000
        self.childrenevaluationfunc = max

    def __str__(self):
        msg = 'Active color: white\n'
        msg += str(self.listpiece)
        return msg


class BlackGamePosition(GamePosition):
    def __init__(self, listpiece, parent=None, originmove=None):
        super().__init__(listpiece, parent, originmove)
        self.movegeneratorfunc = black_generator_moves
        self.enemy_game_position_func = WhiteGamePosition
        self.ischeckfunc = self.listpiece.isblackkingincheck
        self.imincheckmatevalue = 1000
        self.childrenevaluationfunc = min

    def __str__(self):
        msg = 'Active color: black\n'
        msg += str(self.listpiece)
        return msg


class GameThread(threading.Thread):
    def __init__(self, gameposition):
        super().__init__()
        self.gameposition = gameposition

    def run(self):
        return self.gameposition.builtplytreevalue(3)


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

    # root = BlackGamePosition(debug_pos_factory())
    # print(pcsm.listpiece)
    # u = UciMoveSetter(root, ['e1d1', 'e8d8'])
    # u()
    # print(pcsm.listpiece)

    """
        fen = FenStrParser()
        gameposition = fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        gamethread = GameThread(gameposition)
        gamethread.start()
    """
    fen = FenStrParser()
    gameposition = fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    print(pcsm.listpiece)
    print("White castling rights: ", gameposition.listpiece.whiteking.castlingrights)
    print("Black castling rights: ", gameposition.listpiece.blackking.castlingrights)

