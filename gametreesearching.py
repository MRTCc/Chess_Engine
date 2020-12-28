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
perfposition = 0
hashingmethod = 'zobrist'
isactivetraspositiontable = False     # default True
algorithm = 'perf'                    # default alphabeta
maxply = 1                     # default 5
transpositiontable = None
evalfunctype = 1
hashgenerator = None
rootposition = None
isrunning = True


def initnewgame():
    global transpositiontable
    global hashgenerator
    evm.functype = evalfunctype
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
        elif (isinstance(piece, pcsm.Pawn) and fromcell.absrankdifference(tocell) == 1 and
              fromcell.absfiledifference(tocell) == 1 and capturedpiece is None):
            # enpassant
            if iswhiteturn:
                targetcoordinatesx = fromcell.sumcoordinate(-1, 0)
                targetpiecesx = self.listpiece.getpiecefromcoordinate(targetcoordinatesx)
                targetcoordinatedx = fromcell.sumcoordinate(1, 0)
                targetpiecedx = self.listpiece.getpiecefromcoordinate(targetcoordinatedx)
                if isinstance(targetpiecesx, pcsm.BlackPawn):
                    move = mvm.whiteMoveEnpassantFactory(piece, fromcell, tocell, targetpiecesx, False)
                elif isinstance(targetpiecedx, pcsm.BlackPawn):
                    move = mvm.whiteMoveEnpassantFactory(piece, fromcell, tocell, targetpiecedx, False)
                else:
                    raise ValueError("UciMoveSetter --> invalid uci move : not possible enpassant!!!")
            else:
                targetcoordinatesx = fromcell.sumcoordinate(-1, 0)
                targetpiecesx = self.listpiece.getpiecefromcoordinate(targetcoordinatesx)
                targetcoordinatedx = fromcell.sumcoordinate(1, 0)
                targetpiecedx = self.listpiece.getpiecefromcoordinate(targetcoordinatedx)
                if isinstance(targetpiecesx, pcsm.WhitePawn):
                    move = mvm.blackMoveEnpassantFactory(piece, fromcell, tocell, targetpiecesx, False)
                elif isinstance(targetpiecedx, pcsm.WhitePawn):
                    move = mvm.blackMoveEnpassantFactory(piece, fromcell, tocell, targetpiecedx, False)
                else:
                    raise ValueError("UciMoveSetter --> invalid uci move : not possible enpassant!!!")
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
        if self.algorithm == 'minmax':
            gameposition = MinimaxGamePosition(listpiece, self.enginecolor)
        elif self.algorithm == 'alphabeta' and self.transpositiontable:
            gameposition = AlphabetaGamePositionTable(self.transpositiontable, listpiece, self.enginecolor)
        elif self.algorithm == 'alphabeta' and self.transpositiontable is None:
            gameposition = AlphabetaGamePosition(listpiece, self.enginecolor)
        elif self.algorithm == 'iterdeep' and self.transpositiontable is None:
            gameposition = IterativeDeepeningGamePosition(listpiece, self.enginecolor)
        elif self.algorithm == 'iterdeep' and self.transpositiontable is not None:
            gameposition = IterativeDeepeningGamePositionTable(self.transpositiontable, listpiece, self.enginecolor)
        elif self.algorithm == 'perf':
            gameposition = MinimaxPerfGamePosition(listpiece, self.enginecolor)
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

    def applymove(self, move):
        self.listpiece.applymove(move)

    def undomove(self, move):
        self.listpiece.undomove(move)

    def imincheckmate(self):
        if len(self.moves) < 1 and self.ischeckfunc():
            return True
        else:
            return False

    def isstalemate(self):
        if len(self.moves) < 1 and not self.ischeckfunc():
            return True
        if self.listpiece.isstalemate():
            return True
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


class WhiteGamePosition(GamePosition):
    def __init__(self, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.iswhiteturn = True
        self.movegeneratorfunc = pcsm.white_generator_moves
        self.enemy_game_position_func = BlackGamePosition
        self.ischeckfunc = self.listpiece.iswhitekingincheck
        self.imincheckmatevalue = -checkmatevalue
        self.childrenevaluationfunc = max
        self.generateallmoves()

    def generateallmoves(self):
        for move in self.movegeneratorfunc(self.listpiece):
            self.moves.append(move)

    @staticmethod
    def moveorderingkeybypriority(move):
        if move.ischeck:
            move.priority = 7
        elif move.capturedpiece:
            if isinstance(move.capturedpiece, (pcsm.Queen, pcsm.Rook, pcsm.Bishop, pcsm.Knight)):
                move.priority = 6
            else:
                move.priority = 5
        elif move.iskingcastling:
            move.priority = 4
        elif move.isqueencastling:
            move.priority = 3
        elif move.promotionto:
            move.priority = 2
        else:
            move.priority = 1
        return move.priority

    def outputmoves(self):
        msg = ""
        for move in self.listpiece.moves:
            msg += move.short__str__() + " "
        msg += str(self.value)
        return msg

    def __str__(self):
        msg = 'Active color: white\n'
        msg += str(self.listpiece)
        return msg


class WhiteGamePositionTable(WhiteGamePosition):
    def __init__(self, listpiece, transpositiontable, parent=None):
        super().__init__(listpiece, parent)
        self.enemy_game_position_func = BlackGamePositionTable
        self.transpositiontable = transpositiontable

    def gethashkey(self):
        return self.listpiece.gethashkey()

    def getrecord(self):
        key = self.listpiece.gethashkey()
        board = str(self.listpiece)
        record = self.transpositiontable.getrecord(key, board)
        return record

    def updatetranspositiontable(self, isalphacutoff, isbetacutoff, depthleft, bestmove, ishorizonleaf):
        self.transpositiontable.insertnewrecord(self.listpiece.gethashkey(), self.value, isalphacutoff, isbetacutoff,
                                                depthleft, bestmove, ishorizonleaf, str(self.listpiece))

    def refreshtranspositiontable(self):
        self.transpositiontable.updatetonewposition()


class BlackGamePosition(GamePosition):
    def __init__(self, listpiece, parent=None):
        super().__init__(listpiece, parent)
        self.iswhiteturn = False
        self.movegeneratorfunc = pcsm.black_generator_moves
        self.enemy_game_position_func = WhiteGamePosition
        self.ischeckfunc = self.listpiece.isblackkingincheck
        self.imincheckmatevalue = checkmatevalue
        self.childrenevaluationfunc = min
        self.generateallmoves()

    def generateallmoves(self):
        for move in self.movegeneratorfunc(self.listpiece):
            self.moves.append(move)

    @staticmethod
    def moveorderingkeybypriority(move):
        if move.ischeck:
            move.priority = 7
        elif move.capturedpiece:
            if isinstance(move.capturedpiece, (pcsm.Queen, pcsm.Rook, pcsm.Bishop, pcsm.Knight)):
                move.priority = 6
            else:
                move.priority = 5
        elif move.iskingcastling:
            move.priority = 4
        elif move.isqueencastling:
            move.priority = 3
        elif move.promotionto:
            move.priority = 2
        else:
            move.priority = 1
        return move.priority

    def outputmoves(self):
        msg = ""
        for move in self.listpiece.moves:
            msg += move.short__str__() + " "
        msg += str(self.value)
        return msg

    def __str__(self):
        msg = 'Active color: black\n'
        msg += str(self.listpiece)
        return msg


class BlackGamePositionTable(BlackGamePosition):
    def __init__(self, listpiece, transpositiontable, parent=None):
        super().__init__(listpiece, parent)
        self.enemy_game_position_func = WhiteGamePositionTable
        self.transpositiontable = transpositiontable

    def gethashkey(self):
        return self.listpiece.gethashkey()

    def getrecord(self):
        key = self.listpiece.gethashkey()
        board = str(self.listpiece)
        record = self.transpositiontable.getrecord(key, board)
        return record

    def updatetranspositiontable(self, isalphacutoff, isbetacutoff, depthleft, bestmove, ishorizonleaf):
        self.transpositiontable.insertnewrecord(self.listpiece.gethashkey(), self.value, isalphacutoff, isbetacutoff,
                                                depthleft, bestmove, ishorizonleaf, str(self.listpiece))

    def refreshtranspositiontable(self):
        self.transpositiontable.updatetonewposition()


class MinimaxGamePosition:
    def __init__(self, listpiece, rootcolor):
        self.listpiece = listpiece
        self.rootcolor = rootcolor
        if rootcolor:
            self.position = WhiteGamePosition(listpiece)
        else:
            self.position = BlackGamePosition(listpiece)
        self.value = None

    @staticmethod
    def _childorderingkey(child):
        return child.value

    def minimaxformax(self, position, depthleft):
        global nposition
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        if depthleft == 0:
            evaluator = evm.Evaluator(position.listpiece)
            position.value = evaluator()
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            msg = position.outputmoves()
            testfile.write(msg + "****** CHECKMATE - GAME ENDED ******\n")
            return
        if position.isstalemate():
            position.value = 0
            msg = position.outputmoves()
            testfile.write(msg + "****** DRAW - GAME ENDED ******\n")
            return
        for move in position.moves:
            position.applymove(move)
            child = position.enemy_game_position_func(position.listpiece, position)
            try:
                self.minimaxformin(child, depthleft - 1)
            except StopSearchSystemExit:
                position.undomove(move)
                raise StopSearchSystemExit
            position.children.append(child)
            position.undomove(move)
        maxchild = None
        for child in position.children:
            if maxchild is None:
                maxchild = child
            else:
                if maxchild.value < child.value:
                    maxchild = child
        position.value = maxchild.value
        return

    def minimaxformin(self, position, depthleft):
        global nposition
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        if depthleft == 0:
            evaluator = evm.Evaluator(self.listpiece)
            position.value = evaluator()
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            msg = position.outputmoves()
            testfile.write(msg + "****** CHECKMATE - GAME ENDED ******\n")
            return
        if position.isstalemate():
            position.value = 0
            msg = position.outputmoves()
            testfile.write(msg + "****** DRAW - GAME ENDED ******\n")
            return
        for move in position.moves:
            position.applymove(move)
            child = position.enemy_game_position_func(position.listpiece, position)
            try:
                self.minimaxformax(child, depthleft - 1)
            except StopSearchSystemExit:
                position.undomove(move)
                raise StopSearchSystemExit
            position.children.append(child)
            position.undomove(move)
        minchild = None
        for child in position.children:
            if minchild is None:
                minchild = child
            else:
                if minchild.value > child.value:
                    minchild = child
        position.value = minchild.value
        return

    @staticmethod
    def _moveorderingkey(move):
        return move.value

    def calcbestmove(self, ply):
        if self.rootcolor:
            self.minimaxformax(self.position, ply)
        else:
            self.minimaxformin(self.position, ply)
        self.value = self.position.value
        for index in range(0, len(self.position.children)):
            if self.position.children[index].value == self.value:
                return self.position.moves[index]

    def getrandomoutmove(self):
        index = random.randint(0, len(self.position.moves) - 1)
        strmove = self.position.moves[index].short__str__()
        return strmove

    def __str__(self):
        return self.position.__str__()


class MinimaxPerfGamePosition(MinimaxGamePosition):
    def __init__(self, listpiece, rootcolor):
        super().__init__(listpiece, rootcolor)
        self.perfposition = 0

    def minimaxformax(self, position, depthleft):
        global nposition
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        if depthleft == 0:
            self.perfposition += 1
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        if position.imincheckmate():
            msg = position.outputmoves()
            testfile.write(msg + "****** CHECKMATE - GAME ENDED ******\n")
            return
        if position.isstalemate():
            msg = position.outputmoves()
            testfile.write(msg + "****** DRAW - GAME ENDED ******\n")
            return
        for move in position.moves:
            position.applymove(move)
            child = position.enemy_game_position_func(position.listpiece, position)
            try:
                self.minimaxformin(child, depthleft - 1)
            except StopSearchSystemExit:
                position.undomove(move)
                raise StopSearchSystemExit
            position.children.append(child)
            position.undomove(move)
        return

    def minimaxformin(self, position, depthleft):
        global nposition
        nposition += 1
        if not isrunning:
            raise StopSearchSystemExit
        if depthleft == 0:
            self.perfposition += 1
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        if position.imincheckmate():
            msg = position.outputmoves()
            testfile.write(msg + "****** CHECKMATE - GAME ENDED ******\n")
            return
        if position.isstalemate():
            msg = position.outputmoves()
            testfile.write(msg + "****** DRAW - GAME ENDED ******\n")
            return
        for move in position.moves:
            position.applymove(move)
            child = position.enemy_game_position_func(position.listpiece, position)
            try:
                self.minimaxformax(child, depthleft - 1)
            except StopSearchSystemExit:
                position.undomove(move)
                raise StopSearchSystemExit
            position.children.append(child)
            position.undomove(move)
        return

    def calcbestmove(self, ply):
        if self.rootcolor:
            self.minimaxformax(self.position, ply)
        else:
            self.minimaxformin(self.position, ply)
        return self.perfposition


class AlphabetaGamePosition:
    def __init__(self, listpiece, rootcolor):
        self.listpiece = listpiece
        self.rootcolor = rootcolor
        if rootcolor:
            self.position = WhiteGamePosition(listpiece)
        else:
            self.position = BlackGamePosition(listpiece)
        self.value = None

    def alphabetamax(self, position, alpha, beta, depthleft):
        global nposition
        nposition += 1
        global isrunning
        if not isrunning:
            raise StopSearchSystemExit
        if depthleft == 0:
            evaluator = evm.Evaluator(position.listpiece)
            position.value = evaluator()
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            msg = position.outputmoves()
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return
        if position.isstalemate():
            position.value = 0
            msg = position.outputmoves()
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return
        for move in position.moves:
            position.applymove(move)
            child = position.enemy_game_position_func(position.listpiece, position)
            try:
                child.moves.sort(key=child.moveorderingkeybypriority, reverse=True)
                self.alphabetamin(child, alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                position.undomove(move)
                raise StopSearchSystemExit
            if child.value >= beta:
                position.value = beta
                msg = position.outputmoves()
                testfile.write(msg + "---------- beta cut-off -----------" + "\n")
                position.undomove(move)
                return
            if child.value > alpha:
                alpha = child.value
            position.children.append(child)
            position.undomove(move)
        position.value = alpha
        return

    def alphabetamin(self, position, alpha, beta, depthleft):
        global nposition
        nposition += 1
        global isrunning
        if not isrunning:
            raise StopSearchSystemExit
        if depthleft == 0:
            evaluator = evm.Evaluator(position.listpiece)
            position.value = evaluator()
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            msg = position.outputmoves()
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return
        if position.isstalemate():
            position.value = 0
            msg = position.outputmoves()
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return
        for move in position.moves:
            position.applymove(move)
            child = position.enemy_game_position_func(position.listpiece, position)
            try:
                child.moves.sort(key=child.moveorderingkeybypriority, reverse=False)
                self.alphabetamax(child, alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                position.undomove(move)
                raise StopSearchSystemExit
            if child.value <= alpha:
                position.value = alpha
                msg = position.outputmoves()
                testfile.write(msg + "---------- alpha cut-off -----------" + "\n")
                position.undomove(move)
                return
            if child.value < beta:
                beta = child.value
            position.children.append(child)
            position.undomove(move)
        position.value = beta
        return

    @staticmethod
    def _moveorderingkey(move):
        return move.value

    def calcbestmove(self, ply):
        if self.rootcolor:
            self.alphabetamax(self.position, -800, +800, ply)
        else:
            self.alphabetamin(self.position, -800, +800, ply)
        self.value = self.position.value
        for index in range(0, len(self.position.children)):
            if self.position.children[index].value == self.value:
                return self.position.moves[index]

    def getrandomoutmove(self):
        index = random.randint(0, len(self.position.moves) - 1)
        strmove = self.position.moves[index].short__str__()
        return strmove

    def __str__(self):
        return self.position.__str__()


class AlphabetaGamePositionTable:
    def __init__(self, transpositiontable, listpiece, rootcolor):
        self.listpiece = listpiece
        self.rootcolor = rootcolor
        if rootcolor:
            self.position = WhiteGamePositionTable(listpiece, transpositiontable)
        else:
            self.position = BlackGamePositionTable(listpiece, transpositiontable)
        self.value = None

    def alphabetamax(self, position, alpha, beta, depthleft):
        global nposition
        nposition += 1
        global isrunning
        if not isrunning:
            raise StopSearchSystemExit
        record = position.getrecord()
        if record is not None:
            position.value = record.score
            position.bestmove = record.bestmove
            msg = position.outputmoves()
            testfile.write(msg + "________ Transposition table match ______________" + "\n")
            return
        if depthleft == 0:
            evaluator = evm.Evaluator(position.listpiece)
            position.value = evaluator()
            position.updatetranspositiontable(False, False, depthleft, None, True)
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            position.updatetranspositiontable(False, False, depthleft, None, False)
            msg = position.outputmoves()
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return
        if position.isstalemate():
            position.value = 0
            position.updatetranspositiontable(False, False, depthleft, None, False)
            msg = position.outputmoves()
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return
        for move in position.moves:
            position.applymove(move)
            child = position.enemy_game_position_func(position.listpiece, transpositiontable, position)
            try:
                child.moves.sort(key=child.moveorderingkeybypriority, reverse=True)
                self.alphabetamin(child, alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                position.listpiece.undomove(move)
                raise StopSearchSystemExit
            if child.value >= beta:
                position.value = beta
                position.updatetranspositiontable(False, True, depthleft, None, False)
                msg = position.outputmoves()
                testfile.write(msg + "---------- beta cut-off -----------" + "\n")
                position.undomove(move)
                return
            if child.value > alpha:
                alpha = child.value
            position.children.append(child)
            position.undomove(move)
        position.value = alpha
        position.updatetranspositiontable(False, False, depthleft, None, False)
        return

    def alphabetamin(self, position, alpha, beta, depthleft):
        global nposition
        nposition += 1
        global isrunning
        if not isrunning:
            raise StopSearchSystemExit
        record = position.getrecord()
        if record is not None:
            position.value = record.score
            position.bestmove = record.bestmove
            msg = position.outputmoves()
            testfile.write(msg + "________ Transposition table match ______________" + "\n")
            return
        if depthleft == 0:
            evaluator = evm.Evaluator(position.listpiece)
            position.value = evaluator()
            position.updatetranspositiontable(False, False, depthleft, None, True)
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            position.updatetranspositiontable(False, False, depthleft, None, False)
            msg = position.outputmoves()
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return
        if position.isstalemate():
            position.value = 0
            position.updatetranspositiontable(False, False, depthleft, None, False)
            msg = position.outputmoves()
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return
        for move in position.moves:
            position.applymove(move)
            child = position.enemy_game_position_func(position.listpiece, transpositiontable, position)
            try:
                child.moves.sort(key=child.moveorderingkeybypriority, reverse=False)
                self.alphabetamax(child, alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                position.undomove(move)
                raise StopSearchSystemExit
            if child.value <= alpha:
                position.value = alpha
                position.updatetranspositiontable(True, False, depthleft, None, False)
                msg = position.outputmoves()
                testfile.write(msg + "---------- alpha cut-off -----------" + "\n")
                position.undomove(move)
                return
            if child.value < beta:
                beta = child.value
            position.children.append(child)
            position.undomove(move)
        position.value = beta
        position.updatetranspositiontable(False, False, depthleft, None, False)
        return

    @staticmethod
    def _moveorderingkey(move):
        return move.value

    def calcbestmove(self, ply):
        if self.rootcolor:
            self.alphabetamax(self.position, -800, +800, ply)
        else:
            self.alphabetamin(self.position, -800, +800, ply)
        self.value = self.position.value
        for index in range(0, len(self.position.children)):
            if self.position.children[index].value == self.value:
                return self.position.moves[index]

    def getrandomoutmove(self):
        index = random.randint(0, len(self.position.moves) - 1)
        strmove = self.position.moves[index].short__str__()
        return strmove

    def __str__(self):
        return self.position.__str__()


class IterativeDeepeningGamePosition:
    def __init__(self, listpiece, rootcolor):
        self.listpiece = listpiece
        self.rootcolor = rootcolor
        if rootcolor:
            self.position = WhiteGamePosition(listpiece)
        else:
            self.position = BlackGamePosition(listpiece)
        self.value = None

    def alphabetamax(self, position, alpha, beta, depthleft):
        global nposition
        nposition += 1
        global isrunning
        if not isrunning:
            raise StopSearchSystemExit
        if depthleft == 0:
            evaluator = evm.Evaluator(position.listpiece)
            position.value = evaluator()
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            msg = position.outputmoves()
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return
        if position.isstalemate():
            position.value = 0
            msg = position.outputmoves()
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return
        for move in position.moves:
            position.applymove(move)
            child = position.enemy_game_position_func(position.listpiece, position)
            try:
                child.moves.sort(key=child.moveorderingkeybypriority, reverse=True)
                self.alphabetamin(child, alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                position.undomove(move)
                raise StopSearchSystemExit
            if child.value >= beta:
                position.value = beta
                msg = position.outputmoves()
                testfile.write(msg + "---------- beta cut-off -----------" + "\n")
                position.undomove(move)
                return
            if child.value > alpha:
                alpha = child.value
            position.children.append(child)
            position.undomove(move)
        position.value = alpha
        return

    def alphabetamin(self, position, alpha, beta, depthleft):
        global nposition
        nposition += 1
        global isrunning
        if not isrunning:
            raise StopSearchSystemExit
        if depthleft == 0:
            evaluator = evm.Evaluator(position.listpiece)
            position.value = evaluator()
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            msg = position.outputmoves()
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return
        if position.isstalemate():
            position.value = 0
            msg = position.outputmoves()
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return
        for move in position.moves:
            self.listpiece.applymove(move)
            child = position.enemy_game_position_func(position.listpiece, position)
            try:
                child.moves.sort(key=child.moveorderingkeybypriority, reverse=False)
                self.alphabetamax(child, alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                position.listpiece.undomove(move)
                raise StopSearchSystemExit
            if child.value <= alpha:
                position.value = alpha
                msg = position.outputmoves()
                testfile.write(msg + "---------- alpha cut-off -----------" + "\n")
                position.listpiece.undomove(move)
                return
            if child.value < beta:
                beta = child.value
            position.children.append(child)
            position.listpiece.undomove(move)
        position.value = beta
        return

    @staticmethod
    def _moveorderingkey(move):
        return move.value

    def calcbestmove(self, maxply):
        for ply in range(1, maxply + 1):
            self.position.children = []
            if self.rootcolor:
                self.alphabetamax(self.position, -800, +800, ply)
            else:
                self.alphabetamin(self.position, -800, +800, ply)
            self.value = self.position.value
            for index in range(0, len(self.position.children)):
                self.position.moves[index].value = self.position.children[index].value
            self.position.moves.sort(key=self._moveorderingkey, reverse=True)
        return self.position.moves[0]

    def getrandomoutmove(self):
        index = random.randint(0, len(self.position.moves) - 1)
        strmove = self.position.moves[index].short__str__()
        return strmove

    def __str__(self):
        return self.position.__str__()


class IterativeDeepeningGamePositionTable:
    def __init__(self, transpositiontable, listpiece, rootcolor):
        self.listpiece = listpiece
        self.rootcolor = rootcolor
        if rootcolor:
            self.position = WhiteGamePositionTable(listpiece, transpositiontable)
        else:
            self.position = BlackGamePositionTable(listpiece, transpositiontable)
        self.value = None

    def alphabetamax(self, position, alpha, beta, depthleft):
        global nposition
        nposition += 1
        global isrunning
        if not isrunning:
            raise StopSearchSystemExit
        record = position.getrecord()
        if record is not None:
            position.value = record.score
            position.bestmove = record.bestmove
            msg = position.outputmoves()
            testfile.write(msg + "________ Transposition table match ______________" + "\n")
            return
        if depthleft == 0:
            evaluator = evm.Evaluator(position.listpiece)
            position.value = evaluator()
            position.updatetranspositiontable(False, False, depthleft, None, True)
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            position.updatetranspositiontable(False, False, depthleft, None, False)
            msg = position.outputmoves()
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return
        if position.isstalemate():
            position.value = 0
            position.updatetranspositiontable(False, False, depthleft, None, False)
            msg = position.outputmoves()
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return position.value
        for move in position.moves:
            position.applymove(move)
            child = position.enemy_game_position_func(position.listpiece, transpositiontable, position)
            try:
                child.moves.sort(key=child.moveorderingkeybypriority, reverse=True)
                self.alphabetamin(child, alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                position.listpiece.undomove(move)
                raise StopSearchSystemExit
            if child.value >= beta:
                position.value = beta
                position.updatetranspositiontable(False, True, depthleft, None, False)
                msg = position.outputmoves()
                testfile.write(msg + "---------- beta cut-off -----------" + "\n")
                position.undomove(move)
                return
            if child.value > alpha:
                alpha = child.value
            position.children.append(child)
            position.undomove(move)
        position.value = alpha
        position.updatetranspositiontable(False, False, depthleft, None, False)
        return

    def alphabetamin(self, position, alpha, beta, depthleft):
        global nposition
        nposition += 1
        global isrunning
        if not isrunning:
            raise StopSearchSystemExit
        record = position.getrecord()
        if record is not None:
            position.value = record.score
            position.bestmove = record.bestmove
            msg = position.outputmoves()
            testfile.write(msg + "________ Transposition table match ______________" + "\n")
            return
        if depthleft == 0:
            evaluator = evm.Evaluator(position.listpiece)
            position.value = evaluator()
            position.updatetranspositiontable(False, False, depthleft, None, True)
            msg = position.outputmoves()
            testfile.write(msg + "\n")
            return
        if position.imincheckmate():
            position.value = position.imincheckmatevalue
            position.updatetranspositiontable(False, False, depthleft, None, False)
            msg = position.outputmoves()
            testfile.write(msg + "********** CHECKMATE - GAME ENDED **********\n")
            return
        if position.isstalemate():
            position.value = 0
            position.updatetranspositiontable(False, False, depthleft, None, False)
            msg = position.outputmoves()
            testfile.write(msg + "********** DRAW - GAME ENDED **********\n")
            return
        for move in position.moves:
            position.applymove(move)
            child = position.enemy_game_position_func(position.listpiece, transpositiontable, position)
            try:
                child.moves.sort(key=child.moveorderingkeybypriority, reverse=True)
                self.alphabetamax(child, alpha, beta, depthleft - 1)
            except StopSearchSystemExit:
                position.undomove(move)
                raise StopSearchSystemExit
            if child.value <= alpha:
                position.value = alpha
                position.updatetranspositiontable(True, False, depthleft, None, False)
                msg = position.outputmoves()
                testfile.write(msg + "---------- alpha cut-off -----------" + "\n")
                position.undomove(move)
                return
            if child.value < beta:
                beta = child.value
            position.children.append(child)
            position.undomove(move)
        position.value = beta
        position.updatetranspositiontable(False, False, depthleft, None, False)
        return

    @staticmethod
    def _moveorderingkey(move):
        return move.value

    def calcbestmove(self, maxply):
        for ply in range(1, maxply + 1):
            self.position.children = []
            self.position.refreshtranspositiontable()
            if self.rootcolor:
                self.alphabetamax(self.position, -800, +800, ply)
            else:
                self.alphabetamin(self.position, -800, +800, ply)
            self.value = self.position.value
            for index in range(0, len(self.position.children)):
                self.position.moves[index].value = self.position.children[index].value
            self.position.moves.sort(key=self._moveorderingkey, reverse=True)
        return self.position.moves[0]

    def getrandomoutmove(self):
        index = random.randint(0, len(self.position.moves) - 1)
        strmove = self.position.moves[index].short__str__()
        return strmove

    def __str__(self):
        return self.position.__str__()


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
    """
    initnewgame()
    initgameposition("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 moves".split())
    bestmove = rootposition.calcbestmove(maxply)
    print(rootposition)
    print(bestmove)
    initgameposition("1k6/8/8/8/8/3R4/2Q5/1K6 w - - 0 0 moves d3d7".split())
    bestmove = rootposition.calcbestmove(maxply)
    print(rootposition)
    print(bestmove)
    """

    initnewgame()
    initgameposition("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 moves".split())
    perftcount = rootposition.calcbestmove(4)
    print("perf positions : ", perftcount, "nposition : ", nposition)
    """
    nposition = 0
    algorithm = 'minmax'
    initgameposition("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 moves".split())
    rootposition.builtplytreevalue(4)
    print("minmax nposition : ", nposition)
    """
    """
    initnewgame()
    initgameposition("1brrknqn/8/8/1p6/2p5/8/6PP/1NRBKQRN w - - 0 1 moves".split())
    evalu = evm.Evaluator(rootposition.listpiece)
    value = evalu()
    print(rootposition)
    print(value)
    # rootposition.calcbestmove(2)
    """