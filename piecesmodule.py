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


class AllyOccupationException(Exception):
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

    def __str__(self):
        return self.letters


class Pawn(RealPiece):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate)
        self.enpassantthreat = False
        self.allyking = allyking
        self.enemyking = enemyking
        self.filestep = +1
        self.finalfile = 8
        self.mypromotionto = WhiteQueen
        self.moveCapturePromotionFactory = movemodule.whiteMoveCapturePromotionFactory
        self.moveEnpassantFactory = movemodule.whiteMoveEnpassantFactory

    def generatemoves(self, listpiece):
        super().generatemoves(listpiece)
        moves = []
        tmpmoves = (self.twostepsmove(), self.onestepmove(), self.capture(),
                    self.capture(False), self.captureenpassant())
        for move in tmpmoves:
            if move is not None:
                moves.append(move)
        return moves

    def twostepsmove(self):
        if not self.isstartpos:
            return None
        tocell = self.coordinate.sumcoordinate(0, self.filestep * 2)
        tmp = self.coordinate.sumcoordinate(0, self.filestep)
        if self.isempty(tmp) == False or self.isempty(tocell) == False:
            return None
        if self.allyking.imincheckonthismove(self, tocell):
            return None
        self.enpassantthreat = True
        return self.moveFactory(self, self.coordinate, tocell, False)

    def onestepmove(self):
        tocell = self.coordinate.sumcoordinate(0, self.filestep)
        if not self.isempty(tocell):
            return None
        if self.allyking.imincheckonthismove(self, tocell):
            return None
        return self.moveFactory(self, self.coordinate, tocell, False)

    def capture(self, sx=True):
        rank = -1
        if sx == False:
            rank = +1
        tocell = None
        try:
            tocell = self.coordinate.sumcoordinate(rank, self.filestep)
        except CoordinateException:
            return None
        if self.allyking.imincheckonthismove(self, tocell):
            return None
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece is None:
            return None
        move = None
        if tocell.fileint == self.finalfile:
            promotionto = self.mypromotionto(tocell)
            move = self.moveCapturePromotionFactory(self, self.coordinate, tocell, capturedpiece, promotionto, False)
        else:
            move = self.moveCaptureFactory(
                self, self.coordinate, tocell, capturedpiece, False)
        return move

    def isthereenemypawn(self, coordinate):
        pawns = self.listpiece.pawnsingame[self.enemyindex]
        for pawn in pawns:
            if pawn.coordinate == coordinate:
                return pawn
        return None

    def captureenpassant(self):
        movesx = None
        movedx = None
        targetcellsx = None
        targetcelldx = None
        try:
            targetcellsx = self.coordinate.sumcoordinate(-1, self.filestep)
        except CoordinateException:
            pass
        try:
            targetcelldx = self.coordinate.sumcoordinate(+1, self.filestep)
        except CoordinateException:
            pass
        targetpawnsx = None
        targetpawndx = None
        if targetcellsx is not None:
            targetpawnsx = self.isthereenemypawn(targetcellsx)
        if targetcelldx is not None:
            targetpawndx = self.isthereenemypawn(targetcelldx)
        if targetpawnsx is not None and targetpawnsx.enpassantthreat == True:
            tocell = self.coordinate.sumcoordinate(-1, self.filestep)
            movesx = self.moveEnpassantFactory(
                self, self.coordinate, tocell, targetpawnsx, False)
        if targetpawndx is not None and targetpawndx.enpassantthreat == True:
            tocell = self.coordinate.sumcoordinate(+1, self.filestep)
            movedx = self.moveEnpassantFactory(
                self, self.coordinate, tocell, targetpawndx, False)
        move = None
        if movesx is None:
            move = movedx
        else:
            move = movesx
        return move


class BlackPawn(Pawn, Black):
    def __init__(self, coordinate, allyking, enemyking):
        super().__init__(coordinate, allyking, enemyking)
        super().setblackparameters()
        self.letters = "bp"
        self.filestep = -1
        self.finalfile = 1
        self.mypromotionto = BlackQueen
        self.moveCapturePromotionFactory = movemodule.blackMoveCapturePromotionFactory
        self.moveEnpassantFactory = movemodule.blackMoveEnpassantFactory


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
        self.deltas = ((-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0))
        self.knightdeltas = ((-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2),
                             (-2, 1), (-2, -1))
        self.castlingrights = castlingrights
        self.moveKingCastlingFactory = movemodule.whiteKindsideCastlingFactory
        self.moveQueenCastlingFactory = movemodule.whiteQueensideCastlingFactory
        self.kingcastlingcoordinate = g1
        self.queencastlingcoordinate = c1

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
                if isinstance(enemypiece, (Pawn, Rook, Queen, King)):
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

    def issafekingsideline(self):
        if self.imincheckonthismove(self, f1) == True:
            return False
        if self.isthereallypiece(f1) or self.isthereenemypiece(f1):
            return False
        if self.imincheckonthismove(self, g1) == True:
            return False
        if self.isthereallypiece(g1) or self.isthereenemypiece(g1):
            return False
        return True

    def issafequeensideline(self):
        if self.imincheckonthismove(self, d1) == True:
            return False
        if self.isthereallypiece(d1) or self.isthereenemypiece(d1):
            return False
        if self.imincheckonthismove(self, c1) == True:
            return False
        if self.isthereallypiece(c1) or self.isthereenemypiece(c1):
            return False
        if self.imincheckonthismove(self, b1) == True:
            return False
        if self.isthereallypiece(b1) or self.isthereenemypiece(b1):
            return False
        return True

    def generatemove(self, rankstep, filestep):
        tocell = self.coordinate.sumcoordinate(rankstep, filestep)
        allypiece = self.isthereallypiece(tocell)
        if allypiece != None:
            raise AllyOccupationException
        if self.imincheckonthismove(self, tocell) == True:
            raise TakenKingException
        move = None
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece != None:
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
        if self.castlingrights.ispossiblekingcastling() == True:
            ischeck = self.imincheckonthismove(self, self.kingcastlingcoordinate)
            move = self.moveKingCastlingFactory(ischeck)
            moves.append(move)
        self.castlingrights.safequeensideline = self.issafequeensideline()
        if self.castlingrights.ispossiblequeencastling() == True:
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
        self.moveFactory = movemodule.blackMoveFactory
        self.moveCaptureFactory = movemodule.blackMoveCaptureFactory
        self.moveKingCastlingFactory = movemodule.blackKindsideCastlingFactory
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


class ListPiece:
    def __init__(self, whitepieces, whitepawns, blackpieces, blackpawns):
        self.whitepieces = whitepieces
        self.whitepawns = whitepawns
        self.blackpieces = blackpieces
        self.blackpawns = blackpawns
        self.piecesingame = [self.whitepieces, self.blackpieces]
        self.pawnsingame = [self.whitepawns, self.blackpawns]


class MovesGenerator:
    def __init__(self, listpiece):
        self.listpiece = listpiece

    def generatewhitemoves(self):
        moves = []
        l = self.listpiece
        for piece in l.whitepieces:
            moves += piece.generatemoves(l)
        for pawn in l.whitepawns:
            moves += pawn.generatemoves(l)
        return moves

    def generateblackmoves(self):
        moves = []
        l = self.listpiece
        for piece in l.blackpieces:
            moves += piece.generatemoves(l)
        for pawn in l.blackpawns:
            moves += pawn.generatemoves(l)
        return moves

    def generatemoves(self, iswhiteturn=True):
        if iswhiteturn:
            return self.generatewhitemoves()
        else:
            return self.generateblackmoves()



if __name__ == '__main__':
    import movemodule
    wc = movemodule.CastlingRights(False)
    bc = movemodule.CastlingRights(False)
    whiteKing = WhiteKing(d2, wc)
    blackKing = BlackKing(e7, bc)
    whitepieces = [whiteKing, WhiteQueen(a3, whiteKing, blackKing), WhiteKnight(e3, whiteKing, blackKing)]
    whitepawns = []
    blackpawns = []
    blackpieces = [blackKing, BlackRook(f5, blackKing, whiteKing), BlackKnight(b4, blackKing, whiteKing)]
    l = ListPiece(whitepieces, whitepawns, blackpieces, blackpawns)
    g = MovesGenerator(l)
    moves = g.generatemoves()
    for move in moves:
        print(move)