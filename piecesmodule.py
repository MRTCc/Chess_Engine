# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 11:05:52 2020

@author: martu
"""
import movemodule
from algebraicnotationmodule import CoordinateException
from algebraicnotationmodule import NullAlgebricNotation
from algebraicnotationmodule import AlgebraicNotation
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

startnullcoordinatelist = (a6, b6, c6, d6, e6, f6, g6, h6,
                           a5, b5, c5, d5, e5, f5, g5, h5,
                           a4, b4, c4, d4, e4, f4, g4, h4,
                           a3, b3, c3, d3, e3, f3, g3, h3)


class AllyOccupationException(Exception):
    pass


class TakenKingException(Exception):
    pass


class Black:
    def setblackparameters(self):
        self.moveFactory = movemodule.blackMoveFactory
        self.moveCaptureFactory = movemodule.blackMoveCaptureFactory
        self.myking = blackKing
        self.enemyking = whiteKing
        self.minenemyindex = 0
        self.maxenemyindex = 8

    def isthereallypiece(self, coordinate):
        for piece in pieces[self.maxenemyindex:]:
            if not isinstance(piece, NullPiece) and piece.coordinate == coordinate:
                return piece
        for piece in pawns[self.maxenemyindex:]:
            if not isinstance(piece, NullPiece) and piece.coordinate == coordinate:
                return piece
        return None


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
        self.myking = None
        self.enemyking = None
        self.minenemyindex = 8
        self.maxenemyindex = 16

    # forse questo metodo è meglio farlo astratto
    def generatemoves(self):
        pass

    def move(self, move):
        pass

    def undomove(self, move):
        pass

    def isthereenemypiece(self, coordinate):
        for piece in pieces[self.minenemyindex: self.maxenemyindex]:
            if not isinstance(piece, NullPiece) and piece.coordinate == coordinate:
                return piece
        for pawn in pawns[self.minenemyindex: self.maxenemyindex]:
            if pawn.coordinate == coordinate:
                return pawn
        return None

    def isthereallypiece(self, coordinate):
        for piece in pieces[0: self.minenemyindex]:
            if not isinstance(piece, NullPiece) and piece.coordinate == coordinate:
                return piece
        for piece in pawns[0: self.minenemyindex]:
            if not isinstance(piece, NullPiece) and piece.coordinate == coordinate:
                return piece
        return None

    def isempty(self, coordinate):
        for piece in pieces:
            if not isinstance(piece, NullPiece):
                if piece.coordinate == coordinate:
                    return False
        for pawn in pawns:
            if pawn.coordinate == coordinate:
                return False
        return True

    def __str__(self):
        return self.letters


class Pawn(RealPiece):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        self.enpassantthreat = False
        self.myking = whiteKing
        self.enemyking = blackKing
        self.filestep = +1
        self.finalfile = 8
        self.mypromotionto = WhiteQueen
        self.moveCapturePromotionFactory = movemodule.whiteMoveCapturePromotionFactory
        self.moveEnpassantFactory = movemodule.whiteMoveEnpassantFactory

    def generatemoves(self):
        moves = []
        tmpmoves = (self.twostepsmove(), self.onestepmove(), self.capture(),
                    self.capture(False), self.captureenpassant())
        for move in tmpmoves:
            if move != None:
                moves.append(move)
        return moves

    def twostepsmove(self):
        if self.isstartpos == False:
            return None
        tocell = self.coordinate.sumcoordinate(0, self.filestep * 2)
        tmp = self.coordinate.sumcoordinate(0, self.filestep)
        if self.isempty(tmp) == False or self.isempty(tocell) == False:
            return None
        if self.myking.imincheckonthismove(self, tocell) == True:
            return None
        self.enpassantthreat = True
        return self.moveFactory(self, self.coordinate, tocell, False)

    def onestepmove(self):
        tocell = self.coordinate.sumcoordinate(0, self.filestep)
        if self.isempty(tocell) == False:
            return None
        if self.myking.imincheckonthismove(self, tocell) == True:
            return None
        return self.moveFactory(self, self.coordinate, tocell, False)

    def isthereenemypiece(self, coordinate):
        for piece in pieces[self.minenemyindex: self.maxenemyindex]:
            if not isinstance(piece, NullPiece) and piece.coordinate == coordinate:
                return piece
        for pawn in pawns[self.minenemyindex: self.maxenemyindex]:
            if pawn.coordinate == coordinate:
                return pawn
        return None

    def capture(self, sx=True):
        rank = -1
        if sx == False:
            rank = +1
        tocell = None
        try:
            tocell = self.coordinate.sumcoordinate(rank, self.filestep)
        except CoordinateException:
            return None
        if self.myking.imincheckonthismove(self, tocell) == True:
            return None
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece == None:
            return None
        move = None
        if tocell.fileint == self.finalfile:
            promotionto = self.mypromotionto(tocell)
            move = self.moveCapturePromotionFactory(self, self.coordinate, tocell, capturedpiece, promotionto, False)
        else:
            move = self.moveCaptureFactory(
                self, self.coordinate, tocell, capturedpiece, False)
        return move

    def istherepawn(self, coordinate):
        for pawn in pawns[self.minenemyindex: self.maxenemyindex]:
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
        if targetcellsx != None:
            targetpawnsx = self.istherepawn(targetcellsx)
        if targetcelldx != None:
            targetpawndx = self.istherepawn(targetcelldx)
        if targetpawnsx != None and targetpawnsx.enpassantthreat == True:
            tocell = self.coordinate.sumcoordinate(-1, self.filestep)
            movesx = self.moveEnpassantFactory(
                self, self.coordinate, tocell, targetpawnsx, False)
        if targetpawndx != None and targetpawndx.enpassantthreat == True:
            tocell = self.coordinate.sumcoordinate(+1, self.filestep)
            movedx = self.moveEnpassantFactory(
                self, self.coordinate, tocell, targetpawndx, False)
        move = None
        if movesx == None:
            move = movedx
        else:
            move = movesx
        return move


class BlackPawn(Pawn, Black):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        super().setblackparameters()
        self.letters = "bp"
        self.filestep = -1
        self.finalfile = 1
        self.mypromotionto = BlackQueen
        self.moveCapturePromotionFactory = movemodule.blackMoveCapturePromotionFactory
        self.moveEnpassantFactory = movemodule.blackMoveEnpassantFactory


class WhitePawn(Pawn):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        self.letters = "wp"


class Rook(RealPiece):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        self.myking = whiteKing
        self.enemyking = blackKing
        self.rookdeltas = ((0, 1), (1, 0), (0, -1), (-1, 0))

    def rookgeneratemove(self, delta, factor):
        """
        le eventuali eccezzioni sollevate, verranno gestite dal chiamante
        """
        rankstep = delta[0] * factor
        filestep = delta[1] * factor
        tocell = self.coordinate.sumcoordinate(rankstep, filestep)
        allypiece = self.isthereallypiece(tocell)
        if allypiece != None:
            raise AllyOccupationException
        if self.myking.imincheckonthismove(self, tocell) == True:
            raise TakenKingException
        move = None
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece != None:
            move = self.moveCaptureFactory(self, self.coordinate, tocell, capturedpiece, False)
        else:
            move = self.moveFactory(self, self.coordinate, tocell, False)
        return move

    def rookgeneratemoves(self):
        moves = []
        for delta in self.rookdeltas:
            try:
                for i in range(1, 8):
                    move = self.rookgeneratemove(delta, i)
                    moves.append(move)
                    if move.capturedpiece != None:
                        break
            except(CoordinateException, AllyOccupationException, TakenKingException):
                pass
        return moves

    def generatemoves(self):
        return self.rookgeneratemoves()

class WhiteRook(Rook):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        self.letters = "wR"


class BlackRook(Black, Rook):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        super().setblackparameters()
        self.letters = "bR"


class Knight(RealPiece):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        self.deltas = ((-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2),
                       (-2, 1), (-2, -1))

    def generatemove(self, rankstep, filestep):
        tocell = self.coordinate.sumcoordinate(rankstep, filestep)
        allypiece = self.isthereallypiece(tocell)
        if allypiece != None:
            raise AllyOccupationException
        move = None
        if self.myking.imincheckonthismove(self, tocell) == True:
            raise TakenKingException
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece == None:
            move = self.moveFactory(self, self.coordinate, tocell, False)
        else:
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
    def __init__(self, coordinate):
        super().__init__(coordinate)
        self.letters = "wN"
        self.myking = whiteKing
        self.enemyking = blackKing


class BlackKnight(Black, Knight):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        super().setblackparameters()
        self.letters = "bN"


class Bishop(RealPiece):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        self.bishopdeltas = ((-1, 1), (1, 1), (1, -1), (-1, -1))
        self.myking = whiteKing
        self.enemyking = blackKing

    def bishopgeneratemove(self, delta, factor):
        """
        le eventuali eccezzioni sollevate, verranno gestite dal chiamante
        """
        rankstep = delta[0] * factor
        filestep = delta[1] * factor
        tocell = self.coordinate.sumcoordinate(rankstep, filestep)
        allypiece = self.isthereallypiece(tocell)
        if allypiece != None:
            raise AllyOccupationException
        if self.myking.imincheckonthismove(self, tocell) == True:
            raise TakenKingException
        move = None
        capturedpiece = self.isthereenemypiece(tocell)
        if capturedpiece != None:
            move = self.moveCaptureFactory(self, self.coordinate, tocell, capturedpiece, False)
        else:
            move = self.moveFactory(self, self.coordinate, tocell, False)
        return move

    def bishopgeneratemoves(self):
        moves = []
        for delta in self.bishopdeltas:
            try:
                for i in range(1, 8):
                    move = self.bishopgeneratemove(delta, i)
                    moves.append(move)
                    if move.capturedpiece != None:
                        break
            except(CoordinateException, AllyOccupationException, TakenKingException):
                pass

        return moves

    def generatemoves(self):
        return self.bishopgeneratemoves()


class WhiteBishop(Bishop):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        self.letters = "wB"


class BlackBishop(Black, Bishop):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        super().setblackparameters()
        self.letters = "bB"


class Queen(Rook, Bishop):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        self.letter = 'Q'

    def generatemoves(self):
        rookmoves = super().rookgeneratemoves()
        bishopmoves = super().bishopgeneratemoves()
        moves = rookmoves + bishopmoves
        return moves


class WhiteQueen(Queen):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        self.letters = "wQ"
        self.myking = whiteKing
        self.enemyking = blackKing


class BlackQueen(Black, Queen):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        super().setblackparameters()
        self.letters = "bQ"


class King(RealPiece):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        self.letter = 'K'
        self.deltas = ((-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0))
        self.knightdeltas = ((-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2),
                             (-2, 1), (-2, -1))
        self.castlingrights = movemodule.CastlingRights()
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
            else:
                if isinstance(enemypiece, (Bishop, Queen)):
                    return True
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
            else:
                if isinstance(enemypiece, (Rook, Queen)):
                    return True
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
            else:
                if isinstance(enemypiece, (Bishop, Queen)):
                    return True
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
                if imincheck == True:
                    return True
            except(CoordinateException, AllyOccupationException):
                pass
        for delta in self.knightdeltas:
            imincheck = self.knight_delta(delta)
            if imincheck == True:
                return True
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

    def generatemoves(self):
        moves = []
        for delta in self.deltas:
            try:
                move = self.generatemove(*delta)
                moves.append(move)
            except(CoordinateException, AllyOccupationException, TakenKingException):
                pass
        # arrocco corto e lungo
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
    def __init__(self, coordinate):
        super().__init__(coordinate)
        self.letters = "wK"

    def imincheckonthismove(self, piece, tocell):
        self.enemyking = blackKing
        return super().imincheckonthismove(piece, tocell)


class BlackKing(King):
    def __init__(self, coordinate):
        super().__init__(coordinate)
        self.letters = "bK"
        self.moveFactory = movemodule.blackMoveFactory
        self.moveCaptureFactory = movemodule.blackMoveCaptureFactory
        self.moveKingCastlingFactory = movemodule.blackKindsideCastlingFactory
        self.moveQueenCastlingFactory = movemodule.blackQueensideCastlingFactory
        self.kingcastlingcoordinate = g8
        self.queencastlingcoordinate = c8
        self.minenemyindex = 0
        self.maxenemyindex = 8

    def imincheckonthismove(self, piece, tocell):
        self.enemyking = whiteKing
        return super().imincheckonthismove(piece, tocell)

    def isthereallypiece(self, coordinate):
        for piece in pieces[self.maxenemyindex:]:
            if not isinstance(piece, NullPiece) and piece.coordinate == coordinate:
                return piece
        for piece in pawns[self.maxenemyindex:]:
            if not isinstance(piece, NullPiece) and piece.coordinate == coordinate:
                return piece
        return None

    def issafekingsideline(self):
        if self.imincheckonthismove(self, f8) == True:
            return False
        if self.isthereallypiece(f8) or self.isthereenemypiece(f8):
            return False
        if self.imincheckonthismove(self, g8) == True:
            return False
        if self.isthereallypiece(g8) or self.isthereenemypiece(g8):
            return False
        return True

    def issafequeensideline(self):
        if self.imincheckonthismove(self, d8) == True:
            return False
        if self.isthereallypiece(d8) or self.isthereenemypiece(d8):
            return False
        if self.imincheckonthismove(self, c8) == True:
            return False
        if self.isthereallypiece(c8) or self.isthereenemypiece(c8):
            return False
        if self.imincheckonthismove(self, b8) == True:
            return False
        if self.isthereallypiece(b8) or self.isthereenemypiece(b8):
            return False
        return True


whiteKing = WhiteKing(e1)
blackKing = BlackKing(e8)
pieces = [WhiteRook(a1), WhiteKnight(b1), WhiteBishop(c1), WhiteQueen(d1),
          whiteKing, WhiteBishop(f1), WhiteKnight(g1), WhiteRook(h1),
          BlackRook(a8), BlackKnight(b8), BlackBishop(c8), BlackQueen(d8),
          blackKing, BlackBishop(f8), BlackKnight(g8), BlackRook(h8)]
pawns = [WhitePawn(a2), WhitePawn(b2), WhitePawn(c2), WhitePawn(d2),
         WhitePawn(e2), WhitePawn(f2), WhitePawn(g2), WhitePawn(h2),
         BlackPawn(a7), BlackPawn(b7), BlackPawn(c7), BlackPawn(d7),
         BlackPawn(e7), BlackPawn(f7), BlackPawn(g7), BlackPawn(h7)]

# DEBUG
whiteKing = WhiteKing(f1)
blackKing = BlackKing(e7)
null = NullAlgebricNotation()
pieces = [WhiteRook(a1), WhiteKnight(null), WhiteBishop(null), WhiteQueen(null),
          whiteKing, WhiteBishop(null), WhiteKnight(g1), WhiteRook(null),
          BlackRook(null), BlackKnight(b8), BlackBishop(null), BlackQueen(null),
          blackKing, BlackBishop(null), BlackKnight(null), BlackRook(null)]
pawns = [WhitePawn(e2), WhitePawn(null), WhitePawn(null), WhitePawn(null),
         WhitePawn(null), WhitePawn(null), WhitePawn(null), WhitePawn(null),
         BlackPawn(null), BlackPawn(null), BlackPawn(null), BlackPawn(null),
         BlackPawn(e7), BlackPawn(null), BlackPawn(null), BlackPawn(null)]

if __name__ == '__main__':
    for p in pieces:
        moves = p.generatemoves()
        print("----------------  ", p, "  ----------")
        for move in moves:
            print(move)
    for p in pawns:
        moves = p.generatemoves()
        print("----------------  ", p, "  ----------")
        for move in moves:
            print(move)