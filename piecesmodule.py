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
        self.isstartpos = True
        self.letters = "xx"
        self.moveFactory = movemodule.whiteMoveFactory
        self.moveCaptureFactory = movemodule.whiteMoveCaptureFactory
        self.allyking = None
        self.enemyking = None
        self.enemyindex = 1
        self.allyindex = 0

    def generatemoves(self, listpiece):
        self.listpiece = listpiece

    def isthereenemypiece(self, coordinate):
        pieces = self.listpiece.piecesingame[self.enemyindex]
        pawns = self.listpiece.pawnsingame[self.enemyindex]
        for piece in pieces:
            if piece.coordinate == coordinate:
                return piece
        for pawn in pawns:
            if pawn.coordinate == coordinate:
                return pawn
        return None

    def isthereallypiece(self, coordinate):
        pieces = self.listpiece.piecesingame[self.allyindex]
        pawns = self.listpiece.pawnsingame[self.allyindex]
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

    def generatemoves(self, listpiece):
        super().generatemoves(listpiece)
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
        if self.allyking.imincheckonthismove(self, tocell):
            raise TakenKingException
        return self.moveFactory(self, self.coordinate, tocell, False)

    def _onestepmove(self):
        tocell = self.coordinate.sumcoordinate(0, self.filestep)
        if not self.isempty(tocell):
            raise OccupationException
        if self.allyking.imincheckonthismove(self, tocell):
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
            fromcell = self.coordinate
            self.coordinate = tocell
            self.listpiece.removepiece(capturedpiece)
            iskingtaken = self.allyking.imincheck()
            self.listpiece.addpiece(capturedpiece)
            self.coordinate = fromcell
            if iskingtaken:
                raise TakenKingException
            if tocell.fileint == self.promotionfile:
                promotionto = self.mypromotionto(tocell, self.allyking, self.enemyking)
                move = self.moveCapturePromotionFactory(self, self.coordinate, tocell, capturedpiece, promotionto, False)
            else:
                move = self.moveCaptureFactory(self, self.coordinate, tocell, capturedpiece, False)
        else:
            if enpiece.enpassantthreat:
                fromcell = self.coordinate
                self.coordinate = tocell
                self.listpiece.removepiece(enpiece)
                iskingtaken = self.allyking.imincheck()
                self.listpiece.addpiece(enpiece)
                self.coordinate = fromcell
                if iskingtaken:
                    raise TakenKingException
                move = self.moveEnpassantFactory(self, self.coordinate, tocell, enpiece, False)
            else:
                raise NotLegalMoveException
        return move

    def isthereenemypawn(self, coordinate):
        pawns = self.listpiece.pawnsingame[self.enemyindex]
        for pawn in pawns:
            if pawn.coordinate == coordinate:
                return pawn
        return None


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
        if self.allyking.imincheckonthismove(self, tocell):
            raise TakenKingException
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece is not None:
            move = self.moveCaptureFactory(self, self.coordinate, tocell, capturedpiece, False)
        else:
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
                    except(TakenKingException):
                        pass
            except(CoordinateException, AllyOccupationException):
                pass
        return moves

    def generatemoves(self, listpiece):
        super().generatemoves(listpiece)
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
        move = None
        if self.allyking.imincheckonthismove(self, tocell):
            raise TakenKingException
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece is None:
            move = self.moveFactory(self, self.coordinate, tocell, False)
        else:
            move = self.moveCaptureFactory(self, self.coordinate, tocell, capturedpiece, False)
        return move

    def generatemoves(self, listpiece):
        super().generatemoves(listpiece)
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
        if self.allyking.imincheckonthismove(self, tocell):
            raise TakenKingException
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece is not None:
            move = self.moveCaptureFactory(self, self.coordinate, tocell, capturedpiece, False)
        else:
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

    def generatemoves(self, listpiece):
        super().generatemoves(listpiece)
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
        if self.allyking.imincheckonthismove(self, tocell):
            raise TakenKingException
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece is not None:
            move = self.moveCaptureFactory(self, self.coordinate, tocell, capturedpiece, False)
        else:
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
                    except(TakenKingException):
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
        if self.allyking.imincheckonthismove(self, tocell):
            raise TakenKingException
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece is not None:
            move = self.moveCaptureFactory(self, self.coordinate, tocell, capturedpiece, False)
        else:
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

    def generatemoves(self, listpiece):
        super().generatemoves(listpiece)
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

    def delta_0_2(self, delta):
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

    def delta_1_3_5_7(self, delta):
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

    def delta_4_6(self, delta):
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

    def knight_delta(self, delta):
        targetcell = self.coordinate.sumcoordinate(*delta)
        enemypiece = self.isthereenemypiece(targetcell)
        if isinstance(enemypiece, Knight):
            return True
        else:
            return False

    def imincheckonthismove(self, piece, tocell):
        self.piececoordinate = piece.coordinate
        piece.coordinate = tocell
        imincheck = False
        for i in range(0, 8):
            try:
                imincheck = False
                if i in (0, 2):
                    imincheck = self.delta_0_2(self.deltas[i])
                elif i in (1, 3, 5, 7):
                    imincheck = self.delta_1_3_5_7(self.deltas[i])
                elif i in (4, 6):
                    imincheck = self.delta_4_6(self.deltas[i])
                if imincheck:
                    piece.coordinate = self.piececoordinate
                    return imincheck
            except(CoordinateException, AllyOccupationException):
                pass
        for delta in self.knightdeltas:
            try:
                imincheck = self.knight_delta(delta)
                if imincheck:
                    break
            except(CoordinateException, AllyOccupationException):
                pass
        piece.coordinate = self.piececoordinate
        return imincheck

    def imincheck(self):
        for i in range(0, 8):
            try:
                incheck = False
                if i in (0, 2):
                    incheck = self.delta_0_2(self.deltas[i])
                elif i in (1, 3, 5, 7):
                    incheck = self.delta_1_3_5_7(self.deltas[i])
                elif i in (4, 6):
                    incheck = self.delta_4_6(self.deltas[i])
                if incheck:
                    return incheck
            except(CoordinateException, AllyOccupationException):
                pass
        for delta in self.knightdeltas:
            try:
                incheck = self.knight_delta(delta)
                if incheck:
                    break
            except(CoordinateException, AllyOccupationException):
                pass
        return incheck

    def issafekingsideline(self):
        if self.imincheckonthismove(self, f1):
            return False
        if self.isthereallypiece(f1) or self.isthereenemypiece(f1):
            return False
        if self.imincheckonthismove(self, g1):
            return False
        if self.isthereallypiece(g1) or self.isthereenemypiece(g1):
            return False
        return True

    def issafequeensideline(self):
        if self.imincheckonthismove(self, d1):
            return False
        if self.isthereallypiece(d1) or self.isthereenemypiece(d1):
            return False
        if self.imincheckonthismove(self, c1):
            return False
        if self.isthereallypiece(c1) or self.isthereenemypiece(c1):
            return False
        if self.imincheckonthismove(self, b1):
            return False
        if self.isthereallypiece(b1) or self.isthereenemypiece(b1):
            return False
        return True

    def generatemove(self, rankstep, filestep):
        tocell = self.coordinate.sumcoordinate(rankstep, filestep)
        allypiece = self.isthereallypiece(tocell)
        if allypiece is not None:
            raise AllyOccupationException
        if self.imincheckonthismove(self, tocell):
            raise TakenKingException
        move = None
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece is not None:
            move = self.moveCaptureFactory(self, self.coordinate, tocell, capturedpiece, False)
        else:
            move = self.moveFactory(self, self.coordinate, tocell, False)
        return move

    def generatemoves(self, listpiece):
        super().generatemoves(listpiece)
        moves = []
        for delta in self.deltas:
            try:
                move = self.generatemove(*delta)
                moves.append(move)
            except(CoordinateException, AllyOccupationException, TakenKingException):
                pass
        self.castlingrights.safekindsideline = self.issafekingsideline()
        if self.castlingrights.ispossiblekingcastling():
            ischeck = self.imincheckonthismove(self, self.kingcastlingcoordinate)
            move = self.moveKingCastlingFactory(ischeck)
            moves.append(move)
        self.castlingrights.safequeensideline = self.issafequeensideline()
        if self.castlingrights.ispossiblequeencastling():
            ischeck = self.imincheckonthismove(self, self.queencastlingcoordinate)
            move = self.moveQueenCastlingFactory(ischeck)
            moves.append(move)
        return moves

    def updatecastlingrights(self):
        pass


class WhiteKing(King):
    def __init__(self, coordinate, castlingrights):
        super().__init__(coordinate, castlingrights)
        self.letters = "wK"

    def imincheckonthismove(self, piece, tocell):
        return super().imincheckonthismove(piece, tocell)


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

    def imincheckonthismove(self, piece, tocell):
        return super().imincheckonthismove(piece, tocell)

    def issafekingsideline(self):
        if self.imincheckonthismove(self, f8):
            return False
        if self.isthereallypiece(f8) or self.isthereenemypiece(f8):
            return False
        if self.imincheckonthismove(self, g8):
            return False
        if self.isthereallypiece(g8) or self.isthereenemypiece(g8):
            return False
        return True

    def issafequeensideline(self):
        if self.imincheckonthismove(self, d8):
            return False
        if self.isthereallypiece(d8) or self.isthereenemypiece(d8):
            return False
        if self.imincheckonthismove(self, c8):
            return False
        if self.isthereallypiece(c8) or self.isthereenemypiece(c8):
            return False
        if self.imincheckonthismove(self, b8):
            return False
        if self.isthereallypiece(b8) or self.isthereenemypiece(b8):
            return False
        return True


class NullPiece(RealPiece):
    def __init__(self):
        self.letters = "--"


class ListPiece:
    def __init__(self, whitepieces, whitepawns, blackpieces, blackpawns):
        self.whitepieces = whitepieces
        self.whitepawns = whitepawns
        self.blackpieces = blackpieces
        self.blackpawns = blackpawns
        self.piecesingame = [self.whitepieces, self.blackpieces]
        self.pawnsingame = [self.whitepawns, self.blackpawns]
        self.nullpiece = NullPiece()
        self.board = self._builtboard()
        for piece in self.whitepieces:
            if isinstance(piece, WhiteKing):
                self.whiteking = piece
                break
        else:
            raise Exception("No White King on the board")
        for piece in self.blackpieces:
            if isinstance(piece, BlackKing):
                self.blackking = piece
                break
        else:
            raise Exception("No Black King on the board")

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

    def _movepiece(self, piece, targetcoordinate):
        self.board[piece.coordinate] = self.nullpiece
        self.board[targetcoordinate] = piece
        piece.coordinate = targetcoordinate

    def _capturepiece(self, move):
        self.removepiece(move.piece)
        self._movepiece(move.piece, move.tocell)

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
        self._movepiece(king, king.kingcastlingcoordinate)
        self._movepiece(rook, rook.kingcastlingcoordinate)

    def _applyqueencastling(self, move):
        if move.iswhiteturn:
            king = self.board[e1]
            rook = self.board[a1]
        else:
            king = self.board[e8]
            rook = self.board[a8]
        self._movepiece(king, king.queencastlingcoordinate)
        self._movepiece(rook, rook.queencastlingcoordinate)

    def _applyenpassant(self, move):
        self.removepiece(move.capturedpiece)
        self._movepiece(move.piece, move.tocell)

    def applymove(self, move):
        if move.iskingcastling:
            self._applykingcastling(move)
        elif move.isqueencastling:
            self._applyqueencastling(move)
        elif move.isenpassant:
            self._applyenpassant(move)
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
            self._movepiece(move.piece, move.tocell)
            pass

    def _undokingcastling(self, move):
        if move.iswhiteturn:
            king = self.board[g1]
            rook = self.board[f1]
            rookstartpos = h1
        else:
            king = self.board[g8]
            rook = self.board[f8]
            rookstartpos = h8
        self._movepiece(king, king.startpos)
        self._movepiece(rook, rookstartpos)

    def _undoqueencastling(self, move):
        if move.iswhiteturn:
            king = self.board[c1]
            rook = self.board[d1]
            rookstartpos = a1
        else:
            king = self.board[c8]
            rook = self.board[d8]
            rookstartpos = a8
        self._movepiece(king, king.startpos)
        self._movepiece(rook, rookstartpos)

    def _undoenpassant(self, move):
        self._movepiece(move.piece, move.fromcell)
        self.addpiece(move.capturedpiece)

    def _undocaptureandpromotion(self, move):
        self.addpiece(move.piece)
        self.removepiece(move.promotionto)
        self.addpiece(move.capturedpiece)

    def _undocapturepiece(self, move):
        self._movepiece(move.piece, move.fromcell)
        self.addpiece(move.capturedpiece)

    def _undopromotepawn(self, move):
        self.removepiece(move.promotionto)
        self.addpiece(move.piece)

    def undomove(self, move):
        if move.iskingcastling:
            self._undokingcastling(move)
        elif move.isqueencastling:
            self._undoqueencastling(move)
        elif move.isenpassant:
            self._undoenpassant(move)
        elif move.capturedpiece is not None:
            if move.promotionto is not None:
                self._undocaptureandpromotion(move)
            else:
                self._undocapturepiece(move)
        elif move.promotionto is not None:
            self._undopromotepawn(move)
        else:
            self._movepiece(move.piece, move.fromcell)

    def iswhitekingincheck(self):
        return self.whiteking.imincheck()

    def isblackkingincheck(self):
        return self.blackking.imincheck()

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


if __name__ == '__main__':
    import movemodule

    wc = movemodule.CastlingRights()
    bc = movemodule.CastlingRights()
    whiteKing = WhiteKing(g1, wc)
    blackKing = BlackKing(c8, bc)
    whitepieces = [whiteKing, WhiteRook(f1, whiteKing, blackKing), WhiteQueen(h8, whiteKing, blackKing)]
    whitepawns = []
    blackpawns = [BlackPawn(d3, blackKing, whiteKing)]
    blackpieces = [blackKing, BlackRook(d8, blackKing, whiteKing), BlackQueen(g2, blackKing, whiteKing)]
    l = ListPiece(whitepieces, whitepawns, blackpieces, blackpawns)
    whiteKing.listpiece = l
    blackKing.listpiece = l
    print(l)
    moves = whiteKing.generatemoves(l)
    for move in moves:
        print(move)