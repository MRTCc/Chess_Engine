import movemodule as mvm
import piecesmodule as pcsm
import random
import evaluationmodule as evm
import transpositionmodule as trsp
import algebraicnotationmodule as algn
import hashingalgorithms as hsa
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


checkmatevalue = 10000
nposition = 0
hashingmethod = 'zobrist'
isactivetraspositiontable = True     # default True
algorithm = 'alphabeta'                    # default alphabeta
maxply = 4                          # default 5
transpositiontable = None
hashgenerator = None
rootposition = None
isrunning = True


def initnewgame():
    global transpositiontable
    global hashgenerator
    if isactivetraspositiontable:
        if hashingmethod == 'zobrist':
            hashgenerator = hsa.Zobrist()
        transpositiontable = trsp.transpositiontablefactory(algorithm)


def initgameposition(tokens):
    if transpositiontable:
        transpositiontable.updatetonewposition()
    global isrunning
    isrunning = True
    global rootposition
    movestr = []
    fenstr = []
    if tokens[0] == 'startpos':
        fenstr.append('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
        fenstr.append('w')
        fenstr.append('-')
        fenstr.append('-')
        fenstr.append('0')
        fenstr.append('0')
        isamove = False
        for token in tokens:
            if token == 'moves':
                isamove = True
                continue
            if isamove:
                movestr.append(token)
    else:
        isfenstr = True
        for token in tokens:
            if token == 'moves':
                isfenstr = False
                continue
            if isfenstr:
                fenstr.append(token)
            else:
                movestr.append(token)
    fenparser = FenStrParser(algorithm, transpositiontable, hashgenerator)
    rootposition = fenparser(fenstr, movestr)


class UciMoveSetter:
    def __init__(self, listpiece, strmoves):
        self.listpiece = listpiece
        self.strmoves = strmoves

    @staticmethod
    def movefactory(piece, fromcell, tocell, capturedpiece, iswhiteturn):
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
            piece = self.listpiece.getpiecefromcoordinate(fromcell)
            capturedpiece = self.listpiece.getpiecefromcoordinate(tocell)
            move = self.movefactory(piece, fromcell, tocell, capturedpiece, activecolor)
            self.listpiece.applymove(move)
            activecolor = not activecolor


class FenStrParser:
    def __init__(self, algorithm, transpositiontable, hashgenerator):
        self.whiteletters = ('R', 'N', 'B', 'Q', 'K', 'P')
        self.blackletters = ('r', 'n', 'b', 'q', 'k', 'p')
        self.enginecolor = None
        self.startingcolor = None
        self.algorithm = algorithm
        self.transpositiontable = transpositiontable
        self.hashgenerator = hashgenerator

    @staticmethod
    def _parsecastlingrights(fencastling):
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

    @staticmethod
    def _parsekings(boardstring, wcastlingrights, bcastlingrights):
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

    @staticmethod
    def _parsepieces(boardstring, whiteking, blackking):
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
        if self.algorithm == 'minmax' and self.transpositiontable:
            if self.enginecolor:
                gameposition = MinMaxWhiteGamePositionTable(self.transpositiontable, pcsm.listpiece)
            else:
                gameposition = MinMaxBlackGamePositionTable(self.transpositiontable, pcsm.listpiece)
        elif self.algorithm == 'minmax' and self.transpositiontable is None:
            if self.enginecolor:
                gameposition = MinMaxWhiteGamePosition(pcsm.listpiece)
            else:
                gameposition = MinMaxBlackGamePosition(pcsm.listpiece)
        elif self.algorithm == 'alphabeta' and self.transpositiontable:
            if self.enginecolor:
                gameposition = AlphaBetaWhiteGamePositionTable(self.transpositiontable, pcsm.listpiece)
            else:
                gameposition = AlphaBetaBlackGamePositionTable(self.transpositiontable, pcsm.listpiece)
        elif self.algorithm == 'alphabeta' and self.transpositiontable is None:
            if self.enginecolor:
                gameposition = AlphaBetaWhiteGamePosition(pcsm.listpiece)
            else:
                gameposition = AlphaBetaBlackGamePosition(pcsm.listpiece)
        else:
            raise TypeError("FenStrParser --> invalid gameposition creation... data not valid!!!")
        return gameposition

    @staticmethod
    def _parserenpassant(enpassantstr, listpiece):
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

    def _parsestartingcolor(self, colorstring):
        if colorstring not in ('w', 'b'):
            raise ValueError('Not a valid string fen color!!!')
        if colorstring == 'w':
            self.startingcolor = True
        else:
            self.startingcolor = False

    @staticmethod
    def _getactivecolor(startingcolor, nummoves):
        if nummoves % 2 == 0:
            return startingcolor
        else:
            return not startingcolor

    def __call__(self, fenstr, movestr):
        tokens = fenstr
        # TODO vedere cosa invia ARENA GUI
        if len(tokens) != 6:
            raise ValueError("Invalid FEN string!!!")
        self._isboardvalid(tokens[0])
        wcastlingrights, bcastlingrights = self._parsecastlingrights(tokens[2])
        whiteking, blackking = self._parsekings(tokens[0], wcastlingrights, bcastlingrights)
        whitepieces, whitepawns, blackpieces, blackpawns = self._parsepieces(tokens[0], whiteking, blackking)
        self._parsestartingcolor(tokens[1])
        pcsm.listpiece = pcsm.listpiecefactory(whitepieces, whitepawns, blackpieces, blackpawns, self.hashgenerator,
                                               self.startingcolor)
        pcsm.listpiece.updatecastlingrights()
        self._parserenpassant(tokens[3], pcsm.listpiece)
        movesetter = UciMoveSetter(pcsm.listpiece, movestr)
        movesetter(self.startingcolor)
        self.enginecolor = self._getactivecolor(self.startingcolor, len(movestr))
        gameposition = self._parsergameposition(pcsm.listpiece)
        # print(gameposition)
        # TODO al momento, ignoro gli altri due campi fen
        return gameposition


# TODO Solo per debug
testfile = open("built_tree_test", "w")


class GamePosition:
    def __init__(self, listpiece, parent=None):
        self.iswhiteturn = None
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
        raise Exception("GamePosition --> calcbestmove : not implemented!!!")

    def _outputmoves(self):
        msg = ""
        for move in self.listpiece.moves:
            msg += move.short__str__() + " "
        msg += str(self.value)
        return msg

    def getrandomoutmove(self):
        index = random.randint(0, len(self.moves) - 1)
        strmove = self.moves[index].short__str__()
        return strmove


class MinMaxGamePosition(GamePosition):
    def __init__(self, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.bestmove = None

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
        """
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
        """
        raise Exception("MinMaxGamePosition --> builtplytreevalue : not implemented!!!")

    def calcbestmove(self, ply):
        self.builtplytreevalue(ply)
        for index in range(0, len(self.children)):
            if self.children[index].value == self.value:
                self.bestmove = self.moves[index]
                break
        return self.bestmove


class MinMaxWhiteGamePosition(MinMaxGamePosition):
    def __init__(self, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.iswhiteturn = True
        self.movegeneratorfunc = pcsm.white_generator_moves
        self.enemy_game_position_func = MinMaxBlackGamePosition
        self.ischeckfunc = self.listpiece.iswhitekingincheck
        self.imincheckmatevalue = -checkmatevalue
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
            testfile.write(msg + "\n")
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

    def __str__(self):
        msg = 'Active color: white\n'
        msg += str(self.listpiece)
        return msg


class MinMaxWhiteGamePositionTable(MinMaxWhiteGamePosition):
    def __init__(self, transpositiontable, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.iswhiteturn = True
        self.movegeneratorfunc = pcsm.white_generator_moves
        self.enemy_game_position_func = MinMaxBlackGamePositionTable
        self.ischeckfunc = self.listpiece.iswhitekingincheck
        self.imincheckmatevalue = -checkmatevalue
        self.childrenevaluationfunc = max
        if transpositiontable is None:
            raise ValueError("MinMaxWhiteGamePositionTable --> __init__ : no transposition table available!!!")
        self.transpositiontable = transpositiontable

    def _updatetranspositiontable(self, key, depthleft, bestmove, ishorizonleaf):
        self.transpositiontable.insertnewrecord(key, self.value, depthleft, bestmove, ishorizonleaf,
                                                str(self.listpiece))

    def builtplytreevalue(self, depthleft):
        global nposition
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        positionkey = self.listpiece.gethashkey()
        record = self.transpositiontable.getrecordfromkey(positionkey, str(self.listpiece))
        if record is not None:
            self.value = record.score
            self.bestmove = record.bestmove
            msg = self._outputmoves()
            testfile.write(msg + "________ Transposition Table match ___________" + "\n")
            return
        if depthleft == 0:
            evaluator = evm.Evaluator(self.listpiece)
            self.value = evaluator()
            msg = self._outputmoves()
            self._updatetranspositiontable(positionkey, depthleft, None, True)
            testfile.write(msg + "\n")
            return
        for move in self.movegeneratorfunc(self.listpiece):
            self.moves.append(move)
        for move in self.moves:
            self.listpiece.applymove(move)
            child = self.enemy_game_position_func(self.transpositiontable, self.listpiece, self)
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
            self._updatetranspositiontable(positionkey, depthleft, None, False)
            testfile.write(msg + "****** CHECKMATE - GAME ENDED ******\n")
            return
        if self.isstalemate():
            self.value = 0
            msg = self._outputmoves()
            self._updatetranspositiontable(positionkey, depthleft, None, False)
            testfile.write(msg + "****** DRAW - GAME ENDED ******\n")
            return
        values = []
        for child in self.children:
            values.append(child.value)
        bestvalue = self.childrenevaluationfunc(values)
        self.value = bestvalue
        for index in range(0, len(self.children)):
            if self.children[index].value == self.value:
                self.bestmove = self.moves[index]
                break
        self._updatetranspositiontable(positionkey, depthleft, self.bestmove, False)

    def _outputmoves(self):
        msg = ""
        for move in self.listpiece.moves:
            msg += move.short__str__() + " "
        msg += str(self.value)
        return msg


class MinMaxBlackGamePosition(MinMaxGamePosition):
    def __init__(self, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.iswhiteturn = False
        self.movegeneratorfunc = pcsm.black_generator_moves
        self.enemy_game_position_func = MinMaxWhiteGamePosition
        self.ischeckfunc = self.listpiece.isblackkingincheck
        self.imincheckmatevalue = checkmatevalue
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
            testfile.write(msg + "\n")
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

    def __str__(self):
        msg = 'Active color: black\n'
        msg += str(self.listpiece)
        return msg


class MinMaxBlackGamePositionTable(MinMaxBlackGamePosition):
    def __init__(self, transpositiontable, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.iswhiteturn = False
        self.movegeneratorfunc = pcsm.black_generator_moves
        self.enemy_game_position_func = MinMaxWhiteGamePositionTable
        self.ischeckfunc = self.listpiece.isblackkingincheck
        self.imincheckmatevalue = checkmatevalue
        self.childrenevaluationfunc = min
        if transpositiontable is None:
            raise ValueError("MinMaxWhiteGamePositionTable --> __init__ : no transposition table available!!!")
        self.transpositiontable = transpositiontable

    def _updatetranspositiontable(self, key, depthleft, bestmove, ishorizonleaf):
        self.transpositiontable.insertnewrecord(key, self.value, depthleft, bestmove, ishorizonleaf,
                                                str(self.listpiece))

    def builtplytreevalue(self, depthleft):
        global nposition
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        positionkey = self.listpiece.gethashkey()
        record = self.transpositiontable.getrecordfromkey(positionkey, str(self.listpiece))
        if record is not None:
            self.value = record.score
            self.bestmove = record.bestmove
            msg = self._outputmoves()
            testfile.write(msg + "________ Transposition Table match ___________" + "\n")
            return
        if depthleft == 0:
            evaluator = evm.Evaluator(self.listpiece)
            self.value = evaluator()
            msg = self._outputmoves()
            self._updatetranspositiontable(positionkey, depthleft, None, True)
            testfile.write(msg + "\n")
            return
        for move in self.movegeneratorfunc(self.listpiece):
            self.moves.append(move)
        for move in self.moves:
            self.listpiece.applymove(move)
            child = self.enemy_game_position_func(self.transpositiontable, self.listpiece, self)
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
            self._updatetranspositiontable(positionkey, depthleft, None, False)
            testfile.write(msg + "****** CHECKMATE - GAME ENDED ******\n")
            return
        if self.isstalemate():
            self.value = 0
            msg = self._outputmoves()
            self._updatetranspositiontable(positionkey, depthleft, None, False)
            testfile.write(msg + "****** DRAW - GAME ENDED ******\n")
            return
        values = []
        for child in self.children:
            values.append(child.value)
        bestvalue = self.childrenevaluationfunc(values)
        self.value = bestvalue
        for index in range(0, len(self.children)):
            if self.children[index].value == self.value:
                self.bestmove = self.moves[index]
                break
        self._updatetranspositiontable(positionkey, depthleft, self.bestmove, False)

    def _outputmoves(self):
        msg = ""
        for move in self.listpiece.moves:
            msg += move.short__str__() + " "
        msg += str(self.value)
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
        raise Exception("AlphaBetaGamePosition --> alphabeta : not implemented!!!")

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
        self.iswhiteturn = True
        self.movegeneratorfunc = pcsm.white_generator_moves
        self.enemy_game_position_func = AlphaBetaBlackGamePosition
        self.ischeckfunc = self.listpiece.iswhitekingincheck
        self.imincheckmatevalue = -checkmatevalue
        self.childrenevaluationfunc = max

    def alphabeta(self, alpha, beta, depthleft):
        global nposition
        nposition += 1
        global  isrunning
        if not isrunning:
            raise StopSearchSystemExit
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
            try:
                child.value = child.alphabeta(alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                self.listpiece.undomove(move)
                raise StopSearchSystemExit
            if child.value >= beta:
                self.value = beta
                msg = self._outputmoves()
                testfile.write(msg + "---------- beta cut-off -----------" + "\n")
                self.listpiece.undomove(move)
                return beta
            if child.value > alpha:
                alpha = child.value
            self.children.append(child)
            self.listpiece.undomove(move)
        self.value = alpha
        return alpha

    def __str__(self):
        msg = 'Active color: white\n'
        msg += str(self.listpiece)
        return msg


class AlphaBetaWhiteGamePositionTable(AlphaBetaWhiteGamePosition):
    def __init__(self, transpositiontable, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.enemy_game_position_func = AlphaBetaBlackGamePositionTable
        self.transpositiontable = transpositiontable
        self.bestmove = None

    def _updatetranspositiontable(self, key, isalphacutoff, isbetacutoff, depthleft, bestmove, ishorizonleaf):
        self.transpositiontable.insertnewrecord(key, self.value, isalphacutoff, isbetacutoff, depthleft, bestmove,
                                                ishorizonleaf, str(self.listpiece))

    def alphabeta(self, alpha, beta, depthleft):
        global nposition
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        positionkey = self.listpiece.gethashkey()
        record = self.transpositiontable.getrecordfromkey(positionkey, str(self.listpiece))
        if record is not None:
            self.value = record.score
            self.bestmove = record.bestmove
            msg = self._outputmoves()
            testfile.write(msg + "________ Transposition table match ______________" + "\n")
            return self.value
        if depthleft == 0:
            evaluator = evm.Evaluator(self.listpiece)
            self.value = evaluator()
            msg = self._outputmoves()
            self._updatetranspositiontable(positionkey, False, False, depthleft, None, True)
            testfile.write(msg + "\n")
            return self.value
        for move in self.movegeneratorfunc(pcsm.listpiece):
            self._movepriority(move)
            self.moves.append(move)
        if self.imincheckmate():
            self.value = self.imincheckmatevalue
            msg = self._outputmoves()
            self._updatetranspositiontable(positionkey, False, False, depthleft, None, False)
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return self.value
        if self.isstalemate():
            self.value = 0
            msg = self._outputmoves()
            self._updatetranspositiontable(positionkey, False, False, depthleft, None, False)
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return self.value
        self.moves.sort(key=AlphaBetaGamePosition._moveorderingkey, reverse=True)
        for move in self.moves:
            self.listpiece.applymove(move)
            child = self.enemy_game_position_func(self.transpositiontable, self.listpiece, self)
            try:
                child.value = child.alphabeta(alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                self.listpiece.undomove(move)
                raise StopSearchSystemExit
            if child.value >= beta:
                self.value = beta
                msg = self._outputmoves()
                self._updatetranspositiontable(positionkey, False, True, depthleft, None, False)
                testfile.write(msg + "---------- beta cut-off -----------" + "\n")
                self.listpiece.undomove(move)
                return beta
            if child.value > alpha:
                alpha = child.value
            self.children.append(child)
            self.listpiece.undomove(move)
        self.value = alpha
        for index in range(0, len(self.children)):
            if self.children[index].value == self.value:
                self.bestmove = self.moves[index]
                break
        self._updatetranspositiontable(positionkey, False, False, depthleft, self.bestmove, False)
        return alpha

    def calcbestmove(self, ply):
        self.value = self.alphabeta(-10000000, +10000000, ply)
        bestmove = self.bestmove
        for index in range(0, len(self.children)):
            if self.children[index].value == self.value:
                bestmove = self.moves[index]
                break
        return bestmove


class AlphaBetaBlackGamePosition(AlphaBetaGamePosition):
    def __init__(self, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.iswhiteturn = False
        self.movegeneratorfunc = pcsm.black_generator_moves
        self.enemy_game_position_func = AlphaBetaWhiteGamePosition
        self.ischeckfunc = self.listpiece.isblackkingincheck
        self.imincheckmatevalue = checkmatevalue
        self.childrenevaluationfunc = min

    def alphabeta(self, alpha, beta, depthleft):
        global nposition
        nposition += 1
        global isrunning
        if not isrunning:
            raise StopSearchSystemExit
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
            try:
                child.value = child.alphabeta(alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                self.listpiece.undomove(move)
                raise StopSearchSystemExit
            if child.value <= alpha:
                self.value = alpha
                msg = self._outputmoves()
                testfile.write(msg + "---------- alpha cut-off -----------" + "\n")
                self.listpiece.undomove(move)
                return alpha
            if child.value < beta:
                beta = child.value
            self.children.append(child)
            self.listpiece.undomove(move)
        self.value = beta
        return beta

    def __str__(self):
        msg = 'Active color: black\n'
        msg += str(self.listpiece)
        return msg


class AlphaBetaBlackGamePositionTable(AlphaBetaBlackGamePosition):
    def __init__(self, transpositiontable, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.enemy_game_position_func = AlphaBetaWhiteGamePositionTable
        self.transpositiontable = transpositiontable
        self.bestmove = None

    def _updatetranspositiontable(self, key, isalphacutoff, isbetacutoff, depthleft, bestmove, ishorizonleaf):
        self.transpositiontable.insertnewrecord(key, self.value, isalphacutoff, isbetacutoff, depthleft, bestmove,
                                                ishorizonleaf, str(self.listpiece))

    def alphabeta(self, alpha, beta, depthleft):
        global nposition
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        positionkey = self.listpiece.gethashkey()
        record = self.transpositiontable.getrecordfromkey(positionkey, str(self.listpiece))
        if record is not None:
            self.value = record.score
            self.bestmove = record.bestmove
            msg = self._outputmoves()
            testfile.write(msg + "________ Transposition table match ___________" + "\n")
            return self.value
        if depthleft == 0:
            evaluator = evm.Evaluator(self.listpiece)
            self.value = evaluator()
            msg = self._outputmoves()
            testfile.write(msg + "\n")
            self._updatetranspositiontable(positionkey, False, False, depthleft, None, True)
            return self.value
        for move in self.movegeneratorfunc(pcsm.listpiece):
            self._movepriority(move)
            self.moves.append(move)
        if self.imincheckmate():
            self.value = self.imincheckmatevalue
            msg = self._outputmoves()
            self._updatetranspositiontable(positionkey, False, False, depthleft, None, False)
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return self.value
        if self.isstalemate():
            self.value = 0
            msg = self._outputmoves()
            self._updatetranspositiontable(positionkey, False, False, depthleft, None, False)
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return self.value
        self.moves.sort(key=AlphaBetaGamePosition._moveorderingkey, reverse=True)
        for move in self.moves:
            self.listpiece.applymove(move)
            child = self.enemy_game_position_func(self.transpositiontable, self.listpiece, self)
            try:
                child.value = child.alphabeta(alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                self.listpiece.undomove(move)
                raise StopSearchSystemExit
            if child.value <= alpha:
                self.value = alpha
                msg = self._outputmoves()
                self._updatetranspositiontable(positionkey, True, False, depthleft, None, False)
                testfile.write(msg + "---------- alpha cut-off -----------" + "\n")
                self.listpiece.undomove(move)
                return alpha
            if child.value < beta:
                beta = child.value
            self.children.append(child)
            self.listpiece.undomove(move)
        self.value = beta
        for index in range(0, len(self.children)):
            if self.children[index].value == self.value:
                self.bestmove = self.moves[index]
                break
        self._updatetranspositiontable(positionkey, False, False, depthleft, self.bestmove, False)
        return beta

    def calcbestmove(self, ply):
        self.value = self.alphabeta(-10000000, +10000000, ply)
        bestmove = self.bestmove
        for index in range(0, len(self.children)):
            if self.children[index].value == self.value:
                bestmove = self.moves[index]
                break
        return bestmove


def debug_pos_factory(hashgenerator):
    wc = mvm.CastlingRights(True, True, False, True, False, False)
    bc = mvm.CastlingRights(True, True, False, True, False, False)
    whiteKing = pcsm.WhiteKing(e1, wc)
    blackKing = pcsm.BlackKing(e8, bc)
    whitepieces = [whiteKing, pcsm.WhiteRook(a1, whiteKing, blackKing),
                   pcsm.WhiteKnight(h5, whiteKing, blackKing)]
    whitepawns = [pcsm.WhitePawn(b7, whiteKing, blackKing)]
    blackpieces = [blackKing, pcsm.BlackRook(a8, blackKing, whiteKing),
                   pcsm.BlackKnight(g7, blackKing, whiteKing)]
    blackpawns = [pcsm.BlackPawn(b2, blackKing, whiteKing)]
    pcsm.listpiece = pcsm.listpiecefactory(whitepieces, whitepawns, blackpieces, blackpawns, hashgenerator, True)
    return pcsm.listpiece, whiteKing, blackKing


if __name__ == '__main__':
    """
    table = trsp.TranspositionTable(trsp.AlphaBetaRecord)
    fen = FenStrParser('white', 'alphabeta', table)
    gameposition = fen("8/8/8/8/k2K4/2Q5/8/8 w - - 0 0".split())
    print(pcsm.listpiece)
    bestmove = gameposition.calcbestmove(8)
    print(nposition)
    print(bestmove)
    nposition = 0
    print(len(table.records))
    """

    initnewgame()
    initgameposition("1k6/8/8/8/8/3R4/2Q5/1K6 w - - 0 0 moves".split())
    bestmove = rootposition.calcbestmove(maxply)
    print(rootposition)
    print(bestmove)
    initgameposition("1k6/8/8/8/8/3R4/2Q5/1K6 w - - 0 0 moves d3d7".split())
    bestmove = rootposition.calcbestmove(maxply)
    print(rootposition)
    print(bestmove)

    """
    listpiece, whiteking, blackking = debug_pos_factory()
    gameposition = MinMaxWhiteGamePosition(listpiece)
    print("Tocca a bianco: \n", pcsm.listpiece)
    key = listpiece.gethashvalue()
    print(key)
    # move = mvm.whiteMoveCapturePromotionFactory(listpiece.whitepawns[0], b7, a8, listpiece.blackpieces[1],
    #                                            listpiece.whitepawns[0].mypromotionto(a8, whiteking, blackking), False)
    move = mvm.whiteMovePromotionFactory(listpiece.whitepawns[0], b7, b8,
                                         listpiece.whitepawns[0].mypromotionto(b8, whiteking, blackking), False)
    listpiece.applymove(move)
    print("Tocca a bianco: \n", pcsm.listpiece)
    newkey = listpiece.gethashvalue()
    import hashingalgorithms as has
    rightkey = has.zobristgenerator.gethashkey(listpiece, listpiece.getcurrentactivecolor())
    print("Zobrist key from scratch: ", rightkey, "\nZobrist key from update:  ", newkey)
    move = mvm.whiteMoveFactory(listpiece.whitepieces[0], e1, f1, False)
    listpiece.applymove(move)
    print(listpiece)
    """

    """
    gameposition = fen("2r1k3/3r4/8/8/8/8/K7/8 b - - 0 0".split())
    print(pcsm.listpiece)
    newkey = z.updatezobristkey(key, gameposition.listpiece)
    print("update key:", newkey)
    print("get zobrist key: ", z.getzobristhash(gameposition.listpiece, gameposition.iswhiteturn))
    """
