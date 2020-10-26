# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 11:05:52 2020

@author: martu
"""
import movemodule
from algebraicnotationmodule import CoordinateException
from algebraicnotationmodule import (a8, b8, c8, d8, e8, f8, g8, h8,
                                     a7, b7, c7, d7, e7, f7, g7, h7,
                                     a6, b6, c6, d6, e6, f6, g6, h6,
                                     a5, b5, c5, d5, e5, f5, g5, h5,
                                     a4, b4, c4, d4, e4, f4, g4, h4,
                                     a3, b3, c3, d3, e3, f3, g3, h3,
                                     a2, b2, c2, d2, e2, f2, g2, h2,
                                     a1, b1, c1, d1, e1, f1, g1, h1)

coordinatelist = (a8, b8, c8, d8, e8, f8, g8, h8,
                  a7, b7, c7, d7, e7, f7, g7, h7,
                  a6, b6, c6, d6, e6, f6, g6, h6,
                  a5, b5, c5, d5, e5, f5, g5, h5,
                  a4, b4, c4, d4, e4, f4, g4, h4,
                  a3, b3, c3, d3, e3, f3, g3, h3,
                  a2, b2, c2, d2, e2, f2, g2, h2,
                  a1, b1, c1, d1, e1, f1, g1, h1)


class NotLegalMoveException(Exception):
    pass


class OccupationException(Exception):
    pass


class AllyOccupationException(OccupationException):
    pass


class TakenKingException(Exception):
    pass


class ListPieceFactory:
    def __call__(self, whitepieces, whitepawns, blackpieces, blackpawns):
        kingcount = 0
        for piece in whitepieces:
            if kingcount > 1:
                break
            if isinstance(piece, WhiteKing):
                whiteking = piece
                kingcount += 1
        if kingcount > 1:
            raise AttributeError("Only one White King must be on the board")
        kingcount = 0
        for piece in blackpieces:
            if kingcount > 1:
                break
            if isinstance(piece, BlackKing):
                blackking = piece
                kingcount += 1
        if kingcount > 1:
            raise AttributeError("Only one Black King must be on the board")

        wrongcolor = False
        for piece in whitepieces + whitepawns:
            if isinstance(piece, (BlackPawn, BlackRook, BlackKnight, BlackBishop, BlackQueen, BlackKing)):
                wrongcolor = True
                break
        if wrongcolor:
            raise AttributeError("whitepieces and whitepawns contains a not White piece")
        wrongcolor = False
        for piece in blackpieces + blackpawns:
            if isinstance(piece, (WhitePawn, WhiteRook, WhiteKnight, WhiteBishop, WhiteQueen, WhiteKing)):
                wrongcolor = True
                break
        if wrongcolor:
            raise AttributeError("blackpieces and blackpawns contains a not Black piece")

        listpiece = ListPiece(whitepieces, whitepawns, blackpieces, blackpawns, whiteking, blackking)
        return listpiece


listpiecefactory = ListPieceFactory()


class ListPiece:
    def __init__(self, whitepieces, whitepawns, blackpieces, blackpawns, whiteking, blackking):
        self.whitepieces = whitepieces
        self.whitepawns = whitepawns
        self.blackpieces = blackpieces
        self.blackpawns = blackpawns
        self.whiteking = whiteking
        self.blackking = blackking
        self.piecesingame = [self.whitepieces, self.blackpieces]
        self.pawnsingame = [self.whitepawns, self.blackpawns]
        self.nullpiece = NullPiece()
        self.board = self._builtboard()
        self.moves = []
        self.whitesxrook = None
        self.whitedxrook = None
        self.blacksxrook = None
        self.blackdxrook = None
        self._setrooks()

    def _setrooks(self):
        whitedxrook = self.board[h1]
        if isinstance(whitedxrook, WhiteRook) and whitedxrook.isstartpos:
            self.whitedxrook = whitedxrook
        whitesxrook = self.board[a1]
        if isinstance(whitesxrook, WhiteRook) and whitesxrook.isstartpos:
            self.whitesxrook = whitesxrook
        blackdxrook = self.board[h8]
        if isinstance(blackdxrook, BlackRook) and blackdxrook.isstartpos:
            self.blackdxrook = blackdxrook
        blacksxrook = self.board[a8]
        if isinstance(blacksxrook, BlackRook) and blacksxrook.isstartpos:
            self.blacksxrook = blacksxrook

    def addpiece(self, piece):
        if isinstance(piece.allyking, WhiteKing):
            if isinstance(piece, Pawn):
                lst = self.whitepawns
            else:
                lst = self.whitepieces
        else:
            if isinstance(piece, Pawn):
                lst = self.blackpawns
            else:
                lst = self.blackpieces
        lst.append(piece)
        self.board[piece.coordinate] = piece

    def removepiece(self, piece):
        if piece in self.whitepieces:
            lst = self.whitepieces
        elif piece in self.whitepawns:
            lst = self.whitepawns
        elif piece in self.blackpieces:
            lst = self.blackpieces
        elif piece in self.blackpawns:
            lst = self.blackpawns
        else:
            raise Exception("ListPiece --> removepiece function --> lst not assigned")
        lst.remove(piece)
        self.board[piece.coordinate] = self.nullpiece

    def _builtboard(self, ):
        board = {}
        for pieces in (self.whitepieces, self.whitepawns, self.blackpieces, self.blackpawns):
            for piece in pieces:
                board[piece.coordinate] = piece
        keys = board.keys()
        for coordinate in coordinatelist:
            if coordinate not in keys:
                board[coordinate] = self.nullpiece
        return board

    def movepiece(self, piece, targetcoordinate):
        self.board[piece.coordinate] = self.nullpiece
        self.board[targetcoordinate] = piece
        piece.coordinate = targetcoordinate

    def _capturepiece(self, move):
        self.removepiece(move.capturedpiece)
        self.movepiece(move.piece, move.tocell)

    def _captureandpromotion(self, move):
        self.removepiece(move.capturedpiece)
        self._promotepawn(move)

    def _promotepawn(self, move):
        self.removepiece(move.piece)
        self.addpiece(move.promotionto)

    def _applykingcastling(self, move):
        if move.iswhiteturn:
            king = self.board[e1]
            rook = self.board[h1]
        else:
            king = self.board[e8]
            rook = self.board[h8]
        self.movepiece(king, king.kingcastlingcoordinate)
        self.movepiece(rook, rook.kingcastlingcoordinate)
        king.movescounter += 1
        rook.movescounter += 1
        king.isstartpos = False
        rook.isstartpos = False

    def _applyqueencastling(self, move):
        if move.iswhiteturn:
            king = self.board[e1]
            rook = self.board[a1]
        else:
            king = self.board[e8]
            rook = self.board[a8]
        self.movepiece(king, king.queencastlingcoordinate)
        self.movepiece(rook, rook.queencastlingcoordinate)
        king.movescounter += 1
        rook.movescounter += 1
        king.isstartpos = False
        rook.isstartpos = False

    def applymove(self, move):
        if move.iskingcastling:
            self._applykingcastling(move)
        elif move.isqueencastling:
            self._applyqueencastling(move)
        elif move.capturedpiece is not None:
            if move.promotionto is not None:
                self._captureandpromotion(move)
                pass
            else:
                self._capturepiece(move)
                pass
        elif move.promotionto is not None:
            self._promotepawn(move)
            pass
        else:
            self.movepiece(move.piece, move.tocell)
            pass
        if move.piece:
            move.piece.movescounter += 1
            move.piece.isstartpos = False
        if self.moves:
            lastmove = self.moves[-1]
            if lastmove.isenpassant:
                lastmove.piece.enpassantthreat = False
        self._updatekingcastlingrights(self.whiteking, self.whitesxrook, self.whitedxrook)
        self._updatekingcastlingrights(self.blackking, self.blacksxrook, self.blackdxrook)
        self.moves.append(move)
        lastmove = self.moves[-1]
        if lastmove.isenpassant:
            lastmove.piece.enpassantthreat = True

    def _undokingcastling(self, move):
        if move.iswhiteturn:
            king = self.board[g1]
            rook = self.board[f1]
            rookstartpos = h1
        else:
            king = self.board[g8]
            rook = self.board[f8]
            rookstartpos = h8
        self.movepiece(king, king.startpos)
        self.movepiece(rook, rookstartpos)
        king.movescounter -= 1
        rook.movescounter -= 1
        if rook.movescounter == 0:
            rook.isstartpos = True
        if king.movescounter == 0:
            king.isstartpos = True

    def _undoqueencastling(self, move):
        if move.iswhiteturn:
            king = self.board[c1]
            rook = self.board[d1]
            rookstartpos = a1
        else:
            king = self.board[c8]
            rook = self.board[d8]
            rookstartpos = a8
        self.movepiece(king, king.startpos)
        self.movepiece(rook, rookstartpos)
        king.movescounter -= 1
        rook.movescounter -= 1
        if rook.movescounter == 0:
            rook.isstartpos = True
        if king.movescounter == 0:
            king.isstartpos = True

    def _undocaptureandpromotion(self, move):
        self.addpiece(move.piece)
        self.removepiece(move.promotionto)
        self.addpiece(move.capturedpiece)

    def _undocapturepiece(self, move):
        self.movepiece(move.piece, move.fromcell)
        self.addpiece(move.capturedpiece)

    def _undopromotepawn(self, move):
        self.removepiece(move.promotionto)
        self.addpiece(move.piece)

    def undomove(self, move):
        if move.iskingcastling:
            self._undokingcastling(move)
        elif move.isqueencastling:
            self._undoqueencastling(move)
        elif move.capturedpiece is not None:
            if move.promotionto is not None:
                self._undocaptureandpromotion(move)
            else:
                self._undocapturepiece(move)
        elif move.promotionto is not None:
            self._undopromotepawn(move)
        else:
            self.movepiece(move.piece, move.fromcell)
        if move.piece:
            move.piece.movescounter -= 1
            if move.piece.movescounter == 0:
                move.piece.isstartpos = True
        self._updatekingcastlingrights(self.whiteking, self.whitesxrook, self.whitedxrook)
        self._updatekingcastlingrights(self.blackking, self.blacksxrook, self.blackdxrook)
        if move.isenpassant:
            move.piece.enpassantthreat = False
        self.moves.remove(move)
        if self.moves:
            lastmove = self.moves[-1]
            if lastmove.isenpassant:
                lastmove.piece.enpassantthreat = True

    def iswhitekingincheck(self):
        return self.whiteking.iminchecksetup()

    def isblackkingincheck(self):
        return self.blackking.iminchecksetup()

    def getpiecefromcoordinate(self, coordinate):
        piece = self.board[coordinate]
        if isinstance(piece, NullPiece):
            return None
        else:
            return piece

    def _updatekingcastlingrights(self, king, sxrook, dxrook):
        castlingrights = king.castlingrights
        castlingrights.kinginstartpos = king.isstartpos
        if sxrook:
            castlingrights.rooksxinstartpos = sxrook.isstartpos
        if dxrook:
            castlingrights.rookdxinstartpos = dxrook.isstartpos
        castlingrights.safekingsideline = king.issafekingsideline()
        castlingrights.safequeensideline = king.issafequeensideline()
        castlingrights.kingincheck = king.iminchecksetup()

    def updatecastlingrights(self):
        self._updatekingcastlingrights(self.whiteking, self.whitesxrook, self.whitedxrook)
        self._updatekingcastlingrights(self.blackking, self.blacksxrook, self.blackdxrook)

    def __str__(self):
        keys = self.board.keys()
        strlist = [str(self.board[coordinate]) for coordinate in coordinatelist]
        result = ("|%s|%s|%s|%s|%s|%s|%s|%s|\n" +
                  "|%s|%s|%s|%s|%s|%s|%s|%s|\n" +
                  "|%s|%s|%s|%s|%s|%s|%s|%s|\n" +
                  "|%s|%s|%s|%s|%s|%s|%s|%s|\n" +
                  "|%s|%s|%s|%s|%s|%s|%s|%s|\n" +
                  "|%s|%s|%s|%s|%s|%s|%s|%s|\n" +
                  "|%s|%s|%s|%s|%s|%s|%s|%s|\n" +
                  "|%s|%s|%s|%s|%s|%s|%s|%s|\n") % tuple(strlist)

        return result


listpiece = None


class Black:
    def setblackparameters(self):
        self.moveFactory = movemodule.blackMoveFactory
        self.moveCaptureFactory = movemodule.blackMoveCaptureFactory
        self.enemyindex = 0
        self.allyindex = 1


class Piece:
    def __init__(self, coordinate):
        self.iscapturable = True  # forse bisognerà definire getter e setter
        self.ismoveable = False  # forse bisognerà definire getter e setter
        self.coordinate = coordinate

    def __str__(self):
        return str(self.__class__.__name__)


class RealPiece(Piece):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        self.movescounter = 0
        self.isstartpos = True
        self.letters = "xx"
        self.moveFactory = movemodule.whiteMoveFactory
        self.moveCaptureFactory = movemodule.whiteMoveCaptureFactory
        self.allyking = None
        self.enemyking = None
        self.enemyindex = 1
        self.allyindex = 0

    def generatemoves(self):
        pass

    def isthereenemypiece(self, coordinate):
        pieces = listpiece.piecesingame[self.enemyindex]
        pawns = listpiece.pawnsingame[self.enemyindex]
        for piece in pieces:
            if piece.coordinate == coordinate:
                return piece
        for pawn in pawns:
            if pawn.coordinate == coordinate:
                return pawn
        return None

    def isthereallypiece(self, coordinate):
        pieces = listpiece.piecesingame[self.allyindex]
        pawns = listpiece.pawnsingame[self.allyindex]
        for piece in pieces:
            if piece.coordinate == coordinate:
                return piece
        for pawn in pawns:
            if pawn.coordinate == coordinate:
                return pawn
        return None

    def isempty(self, coordinate):
        if self.isthereenemypiece(coordinate) is not None:
            return False
        if self.isthereallypiece(coordinate) is not None:
            return False
        return True

    def __eq__(self, other):
        if not isinstance(other, Piece):
            raise AttributeError
        if type(self) == type(other) and self.coordinate == other.coordinate:
            return True
        else:
            return False

    def __str__(self):
        return self.letters


class Pawn(RealPiece):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate)
        self.enpassantthreat = False
        self.allyking = allyking
        self.enemyking = enemyking
        self.filestep = +1
        self.promotionfile = 8
        self.mypromotionto = WhiteQueen
        self.movePromotionFactory = movemodule.whiteMovePromotionFactory
        self.moveCapturePromotionFactory = movemodule.whiteMoveCapturePromotionFactory
        self.moveEnpassantFactory = movemodule.whiteMoveEnpassantFactory

    def generatemoves(self):
        moves = []
        try:
            moves.append(self._twostepsmove())
        except(TakenKingException, CoordinateException, NotLegalMoveException, OccupationException,
               AllyOccupationException):
            pass
        try:
            moves.append(self._onestepmove())
        except(TakenKingException, CoordinateException, NotLegalMoveException, OccupationException,
               AllyOccupationException):
            pass
        try:
            moves.append(self._capture(True))
        except(TakenKingException, CoordinateException, NotLegalMoveException, OccupationException,
               AllyOccupationException):
            pass
        try:
            moves.append(self._capture(False))
        except(TakenKingException, CoordinateException, NotLegalMoveException, OccupationException,
               AllyOccupationException):
            pass

        return moves

    def _twostepsmove(self):
        if not self.isstartpos:
            raise NotLegalMoveException
        tocell = self.coordinate.sumcoordinate(0, self.filestep * 2)
        tmpcell = self.coordinate.sumcoordinate(0, self.filestep)
        if self.isempty(tmpcell) is False or self.isempty(tocell) is False:
            raise OccupationException
        if self.allyking.iminchecksetup(self, tocell):
            raise TakenKingException
        return self.moveEnpassantFactory(self, self.coordinate, tocell, False)

    def _onestepmove(self):
        tocell = self.coordinate.sumcoordinate(0, self.filestep)
        if not self.isempty(tocell):
            raise OccupationException
        if self.allyking.iminchecksetup(self, tocell):
            raise TakenKingException
        if tocell.fileint == self.promotionfile:
            promotionto = self.mypromotionto(tocell, self.allyking, self.enemyking)
            return self.movePromotionFactory(self, self.coordinate, tocell, promotionto, False)
        return self.moveFactory(self, self.coordinate, tocell, False)

    def _capture(self, sx=True):
        if sx:
            rank = -1
        else:
            rank = 1
        tocell = self.coordinate.sumcoordinate(rank, self.filestep)
        sidecell = self.coordinate.sumcoordinate(rank, 0)
        enpiece = self.isthereenemypiece(sidecell)
        if enpiece is None:
            capturedpiece = self.isthereenemypiece(tocell)
            if capturedpiece is None:
                raise NotLegalMoveException
            iskingtaken = self.allyking.iminchecksetup(self, tocell, capturedpiece)
            if iskingtaken:
                raise TakenKingException
            if tocell.fileint == self.promotionfile:
                promotionto = self.mypromotionto(tocell, self.allyking, self.enemyking)
                move = self.moveCapturePromotionFactory(self, self.coordinate, tocell, capturedpiece, promotionto, False)
            else:
                move = self.moveCaptureFactory(self, self.coordinate, tocell, capturedpiece, False)
        else:
            if isinstance(enpiece, Pawn) and enpiece.enpassantthreat:
                iskingtaken = self.allyking.imincheck(self, tocell, enpiece)
                if iskingtaken:
                    raise TakenKingException
                move = self.moveCaptureFactory(self, self.coordinate, tocell, enpiece, False)
            else:
                raise NotLegalMoveException
        return move

    def isthereenemypawn(self, coordinate):
        pawns = listpiece.pawnsingame[self.enemyindex]
        for pawn in pawns:
            if pawn.coordinate == coordinate:
                return pawn
        return None

    def onestepmove(self):
        try:
            move = self._onestepmove()
        except(TakenKingException, CoordinateException, NotLegalMoveException, OccupationException,
               AllyOccupationException):
            move = None
        return move

    def mypromotiontofactory(self, tocell):
        return self.mypromotionto(tocell, self.allyking, self.enemyking)


class BlackPawn(Pawn, Black):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate, allyking, enemyking)
        super().setblackparameters()
        self.letters = "bp"
        self.filestep = -1
        self.promotionfile = 1
        self.mypromotionto = BlackQueen
        self.moveCapturePromotionFactory = movemodule.blackMoveCapturePromotionFactory
        self.moveEnpassantFactory = movemodule.blackMoveEnpassantFactory
        self.movePromotionFactory = movemodule.blackMovePromotionFactory


class WhitePawn(Pawn):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate, allyking, enemyking)
        self.letters = "wp"


class Rook(RealPiece):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate)
        self.allyking = allyking
        self.enemyking = enemyking
        self.rookdeltas = ((0, 1), (1, 0), (0, -1), (-1, 0))
        self.kingcastlingcoordinate = f1
        self.queencastlingcoordinate = d1

    def rookgeneratemove(self, delta, factor):
        """
        le eventuali eccezzioni sollevate, verranno gestite dal chiamante
        """
        rankstep = delta[0] * factor
        filestep = delta[1] * factor
        tocell = self.coordinate.sumcoordinate(rankstep, filestep)
        allypiece = self.isthereallypiece(tocell)
        if allypiece is not None:
            raise AllyOccupationException
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece is not None:
            if self.allyking.iminchecksetup(self, tocell, capturedpiece):
                raise TakenKingException
            move = self.moveCaptureFactory(self, self.coordinate, tocell, capturedpiece, False)
        else:
            if self.allyking.iminchecksetup(self, tocell):
                raise TakenKingException
            move = self.moveFactory(self, self.coordinate, tocell, False)
        return move

    def rookgeneratemoves(self):
        moves = []
        for delta in self.rookdeltas:
            try:
                for i in range(1, 8):
                    try:
                        move = self.rookgeneratemove(delta, i)
                        moves.append(move)
                        if move.capturedpiece is not None:
                            break
                    except TakenKingException:
                        pass
            except(CoordinateException, AllyOccupationException):
                pass
        return moves

    def generatemoves(self):
        return self.rookgeneratemoves()


class WhiteRook(Rook):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate, allyking, enemyking)
        self.letters = "wR"


class BlackRook(Black, Rook):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate, allyking, enemyking)
        super().setblackparameters()
        self.kingcastlingcoordinate = f8
        self.queencastlingcoordinate = d8
        self.letters = "bR"


class Knight(RealPiece):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate)
        self.allyking = allyking
        self.enemyking = enemyking
        self.deltas = ((-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2),
                       (-2, 1), (-2, -1))

    def generatemove(self, rankstep, filestep):
        tocell = self.coordinate.sumcoordinate(rankstep, filestep)
        allypiece = self.isthereallypiece(tocell)
        if allypiece is not None:
            raise AllyOccupationException
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece is None:
            if self.allyking.iminchecksetup(self, tocell, capturedpiece):
                raise TakenKingException
            move = self.moveFactory(self, self.coordinate, tocell, False)
        else:
            if self.allyking.iminchecksetup(self, tocell):
                raise TakenKingException
            move = self.moveCaptureFactory(self, self.coordinate, tocell, capturedpiece, False)
        return move

    def generatemoves(self):
        moves = []
        for delta in self.deltas:
            try:
                move = self.generatemove(*delta)
                moves.append(move)
            except(CoordinateException, AllyOccupationException, TakenKingException):
                pass
        return moves


class WhiteKnight(Knight):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate, allyking, enemyking)
        self.letters = "wN"


class BlackKnight(Black, Knight):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate, allyking, enemyking)
        super().setblackparameters()
        self.letters = "bN"


class Bishop(RealPiece):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate)
        self.enemyking = enemyking
        self.allyking = allyking
        self.bishopdeltas = ((-1, 1), (1, 1), (1, -1), (-1, -1))

    def bishopgeneratemove(self, delta, factor):
        """
        le eventuali eccezzioni sollevate, verranno gestite dal chiamante
        """
        rankstep = delta[0] * factor
        filestep = delta[1] * factor
        tocell = self.coordinate.sumcoordinate(rankstep, filestep)
        allypiece = self.isthereallypiece(tocell)
        if allypiece is not None:
            raise AllyOccupationException
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece is not None:
            if self.allyking.iminchecksetup(self, tocell, capturedpiece):
                raise TakenKingException
            move = self.moveCaptureFactory(self, self.coordinate, tocell, capturedpiece, False)
        else:
            if self.allyking.iminchecksetup(self, tocell):
                raise TakenKingException
            move = self.moveFactory(self, self.coordinate, tocell, False)
        return move

    def bishopgeneratemoves(self):
        moves = []
        for delta in self.bishopdeltas:
            try:
                for i in range(1, 8):
                    try:
                        move = self.bishopgeneratemove(delta, i)
                        moves.append(move)
                        if move.capturedpiece is not None:
                            break
                    except TakenKingException:
                        pass
            except(CoordinateException, AllyOccupationException):
                pass

        return moves

    def generatemoves(self):
        return self.bishopgeneratemoves()


class WhiteBishop(Bishop):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate, allyking, enemyking)
        self.letters = "wB"


class BlackBishop(Black, Bishop):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate, allyking, enemyking)
        super().setblackparameters()
        self.letters = "bB"


class Queen(RealPiece):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate)
        self.letter = 'Q'
        self.allyking = allyking
        self.enemyking = enemyking
        self.rookdeltas = ((0, 1), (1, 0), (0, -1), (-1, 0))
        self.bishopdeltas = ((-1, 1), (1, 1), (1, -1), (-1, -1))

    def rookgeneratemove(self, delta, factor):
        """
        le eventuali eccezzioni sollevate, verranno gestite dal chiamante
        """
        rankstep = delta[0] * factor
        filestep = delta[1] * factor
        tocell = self.coordinate.sumcoordinate(rankstep, filestep)
        allypiece = self.isthereallypiece(tocell)
        if allypiece is not None:
            raise AllyOccupationException
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece is not None:
            if self.allyking.iminchecksetup(self, tocell, capturedpiece):
                raise TakenKingException
            move = self.moveCaptureFactory(self, self.coordinate, tocell, capturedpiece, False)
        else:
            if self.allyking.iminchecksetup(self, tocell):
                raise TakenKingException
            move = self.moveFactory(self, self.coordinate, tocell, False)
        return move

    def rookgeneratemoves(self):
        moves = []
        for delta in self.rookdeltas:
            try:
                for i in range(1, 8):
                    try:
                        move = self.rookgeneratemove(delta, i)
                        moves.append(move)
                        if move.capturedpiece is not None:
                            break
                    except TakenKingException:
                        pass
            except(CoordinateException, AllyOccupationException):
                pass
        return moves

    def bishopgeneratemove(self, delta, factor):
        """
        le eventuali eccezzioni sollevate, verranno gestite dal chiamante
        """
        rankstep = delta[0] * factor
        filestep = delta[1] * factor
        tocell = self.coordinate.sumcoordinate(rankstep, filestep)
        allypiece = self.isthereallypiece(tocell)
        if allypiece is not None:
            raise AllyOccupationException
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece is not None:
            if self.allyking.iminchecksetup(self, tocell, capturedpiece):
                raise TakenKingException
            move = self.moveCaptureFactory(self, self.coordinate, tocell, capturedpiece, False)
        else:
            if self.allyking.iminchecksetup(self, tocell):
                raise TakenKingException
            move = self.moveFactory(self, self.coordinate, tocell, False)
        return move

    def bishopgeneratemoves(self):
        moves = []
        for delta in self.bishopdeltas:
            try:
                for i in range(1, 8):
                    try:
                        move = self.bishopgeneratemove(delta, i)
                        moves.append(move)
                        if move.capturedpiece is not None:
                            break
                    except(TakenKingException):
                        pass
            except(CoordinateException, AllyOccupationException):
                pass

        return moves

    def generatemoves(self):
        rookmoves = self.rookgeneratemoves()
        bishopmoves = self.bishopgeneratemoves()
        moves = rookmoves + bishopmoves
        return moves


class WhiteQueen(Queen):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate, allyking, enemyking)
        self.letters = "wQ"


class BlackQueen(Black, Queen):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate, allyking, enemyking)
        super().setblackparameters()
        self.letters = "bQ"


class King(RealPiece):
    def __init__(self, coordinate, castlingrights):
        super().__init__(coordinate)
        self.letter = 'K'
        self.startpos = e1
        self.deltas = ((-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0))
        self.knightdeltas = ((-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2),
                             (-2, 1), (-2, -1))
        self.castlingrights = castlingrights
        self.moveKingCastlingFactory = movemodule.whiteKingsideCastlingFactory
        self.moveQueenCastlingFactory = movemodule.whiteQueensideCastlingFactory
        self.kingcastlingcoordinate = g1
        self.queencastlingcoordinate = c1
        self.enemyindex = 1
        self.allyindex = 0
        self.kingsidelinecoordinates = None
        self.queensidelinecoordinates = None

    def _delta_0_2(self, delta):
        for i in range(1, 8):
            targetcell = self.coordinate.sumcoordinate(delta[0] * i, delta[1] * i)
            allypiece = self.isthereallypiece(targetcell)
            if allypiece is not None:
                raise AllyOccupationException
            enemypiece = self.isthereenemypiece(targetcell)
            if i == 1:
                if isinstance(enemypiece, (Pawn, Bishop, Queen, King)):
                    return True
                elif isinstance(enemypiece, (Rook, Knight)):
                    break
            else:
                if isinstance(enemypiece, (Bishop, Queen)):
                    return True
                elif isinstance(enemypiece, (Rook, Knight, Pawn, King)):
                    break
        return False

    def _delta_1_3_5_7(self, delta):
        for i in range(1, 8):
            targetcell = self.coordinate.sumcoordinate(delta[0] * i, delta[1] * i)
            allypiece = self.isthereallypiece(targetcell)
            if allypiece is not None:
                raise AllyOccupationException
            enemypiece = self.isthereenemypiece(targetcell)
            if i == 1:
                if isinstance(enemypiece, (Rook, Queen, King)):
                    return True
                elif isinstance(enemypiece, (Pawn, Knight, Bishop)):
                    break
            else:
                if isinstance(enemypiece, (Rook, Queen)):
                    return True
                elif isinstance(enemypiece, (Pawn, Knight, Bishop, King)):
                    break
        return False

    def _delta_4_6(self, delta):
        for i in range(1, 8):
            targetcell = self.coordinate.sumcoordinate(delta[0] * i, delta[1] * i)
            allypiece = self.isthereallypiece(targetcell)
            if allypiece is not None:
                raise AllyOccupationException
            enemypiece = self.isthereenemypiece(targetcell)
            if i == 1:
                if isinstance(enemypiece, (Bishop, Queen, King)):
                    return True
                elif isinstance(enemypiece, (Pawn, Knight, Rook)):
                    break
            else:
                if isinstance(enemypiece, (Bishop, Queen)):
                    return True
                elif isinstance(enemypiece, (Pawn, Knight, Rook, King)):
                    break
        return False

    def _knight_delta(self, delta):
        targetcell = self.coordinate.sumcoordinate(*delta)
        enemypiece = self.isthereenemypiece(targetcell)
        if isinstance(enemypiece, Knight):
            return True
        else:
            return False

    def iminchecksetup(self, piece=None, targetcoordinate=None, capturedpiece=None):
        originalcoordinate = None
        if capturedpiece:
            listpiece.removepiece(capturedpiece)
        if piece:
            originalcoordinate = piece.coordinate
            listpiece.movepiece(piece, targetcoordinate)
        result = self._imincheck()
        if piece and originalcoordinate:
            listpiece.movepiece(piece, originalcoordinate)
        if capturedpiece:
            listpiece.addpiece(capturedpiece)
        return result

    def _imincheck(self):
        incheck = False
        for i in range(0, 8):
            try:
                if i in (0, 2):
                    incheck = self._delta_0_2(self.deltas[i])
                elif i in (1, 3, 5, 7):
                    incheck = self._delta_1_3_5_7(self.deltas[i])
                elif i in (4, 6):
                    incheck = self._delta_4_6(self.deltas[i])
                if incheck:
                    return incheck
            except(CoordinateException, AllyOccupationException):
                pass
        for delta in self.knightdeltas:
            try:
                incheck = self._knight_delta(delta)
                if incheck:
                    break
            except(CoordinateException, AllyOccupationException):
                pass
        return incheck

    def issafekingsideline(self):
        for coordinate in self.kingsidelinecoordinates:
            if not self.isempty(coordinate):
                return False
            if self.iminchecksetup(self, coordinate):
                return False
        return True

    def issafequeensideline(self):
        for coordinate in self.queensidelinecoordinates:
            if not self.isempty(coordinate):
                return False
            if self.iminchecksetup(self, coordinate):
                return False
        return True

    def generatemove(self, rankstep, filestep):
        tocell = self.coordinate.sumcoordinate(rankstep, filestep)
        allypiece = self.isthereallypiece(tocell)
        if allypiece is not None:
            raise AllyOccupationException
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece is not None:
            if self.iminchecksetup(self, tocell, capturedpiece):
                raise TakenKingException
            move = self.moveCaptureFactory(self, self.coordinate, tocell, capturedpiece, False)
        else:
            if self.iminchecksetup(self, tocell):
                raise TakenKingException
            move = self.moveFactory(self, self.coordinate, tocell, False)
        return move

    def generatemoves(self):
        moves = []
        for delta in self.deltas:
            try:
                move = self.generatemove(*delta)
                moves.append(move)
            except(CoordinateException, AllyOccupationException, TakenKingException):
                pass
        if self.castlingrights.ispossiblekingcastling():
            move = self.moveKingCastlingFactory()
            moves.append(move)
        if self.castlingrights.ispossiblequeencastling():
            move = self.moveQueenCastlingFactory()
            moves.append(move)
        return moves


class WhiteKing(King):
    def __init__(self, coordinate, castlingrights):
        super().__init__(coordinate, castlingrights)
        self.letters = "wK"
        self.kingsidelinecoordinates = (f1, g1)
        self.queensidelinecoordinates = (d1, c1, b1)


class BlackKing(King):
    def __init__(self, coordinate, castlingrights):
        super().__init__(coordinate, castlingrights)
        self.letters = "bK"
        self.startpos = e8
        self.moveFactory = movemodule.blackMoveFactory
        self.moveCaptureFactory = movemodule.blackMoveCaptureFactory
        self.moveKingCastlingFactory = movemodule.blackKingsideCastlingFactory
        self.moveQueenCastlingFactory = movemodule.blackQueensideCastlingFactory
        self.kingcastlingcoordinate = g8
        self.queencastlingcoordinate = c8
        self.enemyindex = 0
        self.allyindex = 1
        self.kingsidelinecoordinates = (f8, g8)
        self.queensidelinecoordinates = (d8, c8, b8)


class WhiteKingFactory:
    pass


class NullPiece(RealPiece):
    def __init__(self):
        self.letters = "--"


if __name__ == '__main__':
    import movemodule
    wc = movemodule.CastlingRights(False)
    bc = movemodule.CastlingRights(False)
    whiteKing = WhiteKing(d4, wc)
    blackKing = BlackKing(a4, bc)
    whitepieces = [whiteKing, WhiteQueen(a1, whiteKing, blackKing)]
    whitepawns = []
    blackpawns = []
    blackpieces = [blackKing]
    listpiece = ListPiece(whitepieces, whitepawns, blackpieces, blackpawns)
    print(listpiece)

    moves = blackKing.generatemoves()
    for move in moves:
        print(move)