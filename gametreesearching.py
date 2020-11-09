import movemodule as mvm
import piecesmodule as pcsm
import threading
import ctypes
import evaluationmodule as evm
import algebraicnotationmodule as algn
from algebraicnotationmodule import (a8, b8, c8, d8, e8, f8, g8, h8,
                                     a7, b7, c7, d7, e7, f7, g7, h7,
                                     a6, b6, c6, d6, e6, f6, g6, h6,
                                     a5, b5, c5, d5, e5, f5, g5, h5,
                                     a4, b4, c4, d4, e4, f4, g4, h4,
                                     a3, b3, c3, d3, e3, f3, g3, h3,
                                     a2, b2, c2, d2, e2, f2, g2, h2,
                                     a1, b1, c1, d1, e1, f1, g1, h1)

checkmatevalue = 10000
nposition = 0


def startpos_factory(enginecolor, algorithm):
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
    if algorithm == 'minmax':
        if enginecolor == 'white':
            gameposition = MinMaxWhiteGamePosition(pcsm.listpiece)
        elif enginecolor == 'black':
            gameposition = MinMaxBlackGamePosition(pcsm.listpiece)
        else:
            raise ValueError('Not a valid enginecolor value!!!')
    elif algorithm == 'alphabeta':
        if enginecolor == 'white':
            gameposition = AlphaBetaWhiteGamePosition(pcsm.listpiece)
        elif enginecolor == 'black':
            gameposition = AlphaBetaBlackGamePosition(pcsm.listpiece)
        else:
            raise ValueError('Not a valid enginecolor value!!!')
    else:
        raise ValueError('Not a valid algorithm!!!')
    return gameposition


def debug_pos_factory():
    wc = mvm.CastlingRights()
    bc = mvm.CastlingRights()
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
        elif isinstance(piece, pcsm.Pawn) and fromcell.absfiledifference(tocell) == 2:
            # enpassant
            if iswhiteturn:
                move = mvm.whiteMoveEnpassantFactory(piece, fromcell, tocell, False)
            else:
                move = mvm.blackMoveEnpassantFactory(piece, fromcell, tocell, False)
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

    def __call__(self, activecolor):
        for strmove in self.strmoves:
            fromcell = algn.str_to_algebraic(strmove[0:2])
            tocell = algn.str_to_algebraic(strmove[2:4])
            piece = self.gameposition.listpiece.getpiecefromcoordinate(fromcell)
            capturedpiece = self.gameposition.listpiece.getpiecefromcoordinate(tocell)
            move = self.movefactory(piece, fromcell, tocell, capturedpiece, activecolor)
            self.gameposition.listpiece.applymove(move)
            activecolor = not activecolor


class FenStrParser:
    def __init__(self, enginecolor, algorithm):
        self.whiteletters = ('R', 'N', 'B', 'Q', 'K', 'P')
        self.blackletters = ('r', 'n', 'b', 'q', 'k', 'p')
        self.enginecolor = enginecolor
        self.activecolor = None
        self.algorithm = algorithm

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

    def _parsergameposition(self, listpiece):
        if self.algorithm == 'minmax':
            if self.enginecolor == 'white':
                gameposition = MinMaxWhiteGamePosition(listpiece)
            elif self.enginecolor == 'black':
                gameposition = MinMaxBlackGamePosition(listpiece)
            else:
                raise ValueError('Not a valid enginecolor value!!!')
        elif self.algorithm == 'alphabeta':
            if self.enginecolor == 'white':
                gameposition = AlphaBetaWhiteGamePosition(listpiece)
            elif self.enginecolor == 'black':
                gameposition = AlphaBetaBlackGamePosition(listpiece)
            else:
                raise ValueError('Not a valid enginecolor value!!!')
        else:
            raise ValueError('Not a valid algorithm!!!')
        return gameposition

    def _parseactivecolor(self, colorstring):
        if colorstring not in ('w', 'b'):
            raise ValueError('Not a valid string fen color!!!')
        if colorstring == 'w':
            self.activecolor = True
        else:
            self.activecolor = False

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
        tokens = fenstr
        if len(tokens) != 6:
            raise ValueError("Invalid FEN string!!!")
        self._isboardvalid(tokens[0])
        wcastlingrights, bcastlingrights = self._parsecastlingrights(tokens[2])
        whiteking, blackking = self._parsekings(tokens[0], wcastlingrights, bcastlingrights)
        whitepieces, whitepawns, blackpieces, blackpawns = self._parsepieces(tokens[0], whiteking, blackking)
        pcsm.listpiece = pcsm.listpiecefactory(whitepieces, whitepawns, blackpieces, blackpawns)
        pcsm.listpiece.updatecastlingrights()
        self._parserenpassant(tokens[3], pcsm.listpiece)
        gameposition = self._parsergameposition(pcsm.listpiece)
        self._parseactivecolor(tokens[1])
        # print(gameposition)
        # TODO al momento, ignoro gli altri due campi fen
        return gameposition


# TODO Solo per debug
testfile = open("built_tree_test", "w")


class GamePosition:
    def __init__(self, listpiece, parent=None):
        self.listpiece = listpiece
        self.parent = parent
        self.value = None
        self.moves = []
        self.children = []
        self.movegeneratorfunc = None
        self.enemy_game_position_func = None
        self.ischeckfunc = None
        self.imincheckmatevalue = None
        self.childrenevaluationfunc = None

    def imincheckmate(self):
        if len(self.moves) < 1 and self.ischeckfunc():
            return True
        else:
            return False

    def isstalemate(self):
        if (len(self.listpiece.whitepieces) + len(self.listpiece.whitepawns) == 1 and
                len(self.listpiece.blackpieces) + len(self.listpiece.blackpawns) == 1):
            return True
        if len(self.moves) < 1 and not self.ischeckfunc():
            return True
        else:
            return False

    def calcbestmove(self, ply):
        pass

    def _outputmoves(self):
        msg = ""
        for move in self.listpiece.moves:
            msg += move.short__str__() + " "
        msg += str(self.value)
        return msg


class MinMaxGamePosition(GamePosition):
    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def builtplytreevalue(self, depthleft):
        global nposition
        nposition += 1
        if depthleft == 0:
            evaluator = evm.Evaluator(self.listpiece)
            self.value = evaluator()
            msg = self._outputmoves()
            testfile.write(msg + "\n")
            return
        for move in self.movegeneratorfunc(self.listpiece):
            self.moves.append(move)
        for move in self.moves:
            self.listpiece.applymove(move)
            child = self.enemy_game_position_func(self.listpiece, self)
            child.builtplytreevalue(depthleft - 1)
            self.children.append(child)
            self.listpiece.undomove(move)
        if self.imincheckmate():
            self.value = self.imincheckmatevalue
            msg = self._outputmoves()
            testfile.write(msg + "****** CHECKMATE - GAME ENDED ******\n")
            return
        if self.isstalemate():
            self.value = 0
            msg = self._outputmoves()
            testfile.write(msg + "****** DRAW - GAME ENDED ******\n")
            return
        values = []
        for child in self.children:
            values.append(child.value)
        bestvalue = self.childrenevaluationfunc(values)
        self.value = bestvalue

    def calcbestmove(self, ply):
        self.builtplytreevalue(ply)
        bestmove = None
        for index in range(0, len(self.children)):
            if self.children[index].value == self.value:
                bestmove = self.moves[index]
                break
        return bestmove


class MinMaxWhiteGamePosition(MinMaxGamePosition):
    def __init__(self, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.movegeneratorfunc = pcsm.white_generator_moves
        self.enemy_game_position_func = MinMaxBlackGamePosition
        self.ischeckfunc = self.listpiece.iswhitekingincheck
        self.imincheckmatevalue = -checkmatevalue
        self.childrenevaluationfunc = max

    def __str__(self):
        msg = 'Active color: white\n'
        msg += str(self.listpiece)
        return msg


class MinMaxBlackGamePosition(MinMaxGamePosition):
    def __init__(self, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.movegeneratorfunc = pcsm.black_generator_moves
        self.enemy_game_position_func = MinMaxWhiteGamePosition
        self.ischeckfunc = self.listpiece.isblackkingincheck
        self.imincheckmatevalue = checkmatevalue
        self.childrenevaluationfunc = min

    def __str__(self):
        msg = 'Active color: black\n'
        msg += str(self.listpiece)
        return msg


class AlphaBetaGamePosition(GamePosition):
    @staticmethod
    def _movepriority(move):
        if move.ischeck:
            move.priority = 6
        elif move.capturedpiece:
            move.priority = 5
        elif move.iskingcastling:
            move.priority = 4
        elif move.isqueencastling:
            move.priority = 3
        elif move.promotionto:
            move.priority = 2
        else:
            move.priority = 1

    @staticmethod
    def _moveorderingkey(move):
        return move.priority

    def alphabeta(self, alpha, beta, ply):
        pass

    def calcbestmove(self, ply):
        self.value = self.alphabeta(-10000000, +10000000, ply)
        bestmove = None
        for index in range(0, len(self.children)):
            if self.children[index].value == self.value:
                bestmove = self.moves[index]
                break
        return bestmove


class AlphaBetaWhiteGamePosition(AlphaBetaGamePosition):
    def __init__(self, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.movegeneratorfunc = pcsm.white_generator_moves
        self.enemy_game_position_func = AlphaBetaBlackGamePosition
        self.ischeckfunc = self.listpiece.iswhitekingincheck
        self.imincheckmatevalue = -checkmatevalue
        self.childrenevaluationfunc = max

    def alphabeta(self, alpha, beta, depthleft):
        global nposition
        nposition += 1
        if depthleft == 0:
            evaluator = evm.Evaluator(self.listpiece)
            self.value = evaluator()
            msg = self._outputmoves()
            testfile.write(msg + "\n")
            return self.value
        for move in self.movegeneratorfunc(pcsm.listpiece):
            self._movepriority(move)
            self.moves.append(move)
        if self.imincheckmate():
            self.value = self.imincheckmatevalue
            msg = self._outputmoves()
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return self.value
        if self.isstalemate():
            self.value = 0
            msg = self._outputmoves()
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return self.value
        self.moves.sort(key=AlphaBetaGamePosition._moveorderingkey, reverse=True)
        for move in self.moves:
            self.listpiece.applymove(move)
            child = self.enemy_game_position_func(self.listpiece, self)
            child.value = child.alphabeta(alpha, beta, depthleft - 1)
            if child.value >= beta:
                tmp = self.value
                msg = self._outputmoves()
                testfile.write(msg + "\n")
                self.value = tmp
                self.listpiece.undomove(move)
                return beta
            if child.value > alpha:
                alpha = child.value
            self.children.append(child)
            self.listpiece.undomove(move)
        return alpha

    def __str__(self):
        msg = 'Active color: white\n'
        msg += str(self.listpiece)
        return msg


class AlphaBetaBlackGamePosition(AlphaBetaGamePosition):
    def __init__(self, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.movegeneratorfunc = pcsm.black_generator_moves
        self.enemy_game_position_func = AlphaBetaWhiteGamePosition
        self.ischeckfunc = self.listpiece.isblackkingincheck
        self.imincheckmatevalue = checkmatevalue
        self.childrenevaluationfunc = min

    def alphabeta(self, alpha, beta, depthleft):
        global nposition
        nposition += 1
        if depthleft == 0:
            evaluator = evm.Evaluator(self.listpiece)
            self.value = evaluator()
            msg = self._outputmoves()
            testfile.write(msg + "\n")
            return self.value
        for move in self.movegeneratorfunc(pcsm.listpiece):
            self._movepriority(move)
            self.moves.append(move)
        if self.imincheckmate():
            self.value = self.imincheckmatevalue
            msg = self._outputmoves()
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return self.value
        if self.isstalemate():
            self.value = 0
            msg = self._outputmoves()
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return self.value
        self.moves.sort(key=AlphaBetaGamePosition._moveorderingkey, reverse=True)
        for move in self.moves:
            self.listpiece.applymove(move)
            child = self.enemy_game_position_func(self.listpiece, self)
            child.value = child.alphabeta(alpha, beta, depthleft - 1)
            if child.value <= alpha:
                tmp = self.value
                msg = self._outputmoves()
                testfile.write(msg + "\n")
                self.value = tmp
                self.listpiece.undomove(move)
                return alpha
            if child.value < beta:
                beta = child.value
            self.children.append(child)
            self.listpiece.undomove(move)
        return beta

    def __str__(self):
        msg = 'Active color: black\n'
        msg += str(self.listpiece)
        return msg


class GameThread(threading.Thread):
    def __init__(self, gameposition, maxply):
        super().__init__()
        self.gameposition = gameposition
        self.bestmove = None
        self.maxply = maxply
        self.start()

    def run(self):
        try:
            self.bestmove = self.gameposition.builtplytreevalue(self.maxply)
        except Exception:
            print('GameThread ended')

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def killthread(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

    def randommove(self):
        self.bestmove = self.gameposition.movegeneratorfunc(self.gameposition.listpiece)

    def getbestmove(self):
        return self.bestmove


if __name__ == '__main__':
    """"
    fen = FenStrParser('black')
    gameposition = fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1".split())
    setter = UciMoveSetter(gameposition, ['e2e4'])
    setter(False)
    gamethread = GameThread(gameposition, 5)
    print("started")
    import time
    time.sleep(5)
    gamethread.killthread()
    print(gamethread.getbestmove())
    """

    fen = FenStrParser('black', 'alphabeta')
    gameposition = fen("1r2k3/3r4/8/8/8/8/K7/8 b - - 0 0".split())
    print(pcsm.listpiece)
    bestmove = gameposition.calcbestmove(3)
    print(nposition)
    print(bestmove)
    nposition = 0

    """
    fen = FenStrParser('white')
    gameposition = fen("8/8/8/8/k2K4/2Q5/8/8 w - - 0 0".split())
    ev = evm.Evaluator(gameposition.listpiece)
    evaluation = ev()
    print(ev)
    """

