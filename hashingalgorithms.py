import piecesmodule as pcsm
import algebraicnotationmodule as alg
import random


class HashingAlgorithm:
    def gethashkey(self, listpiece, activecolor):
        pass

    def updatehashkey(self, key, listpiece, activecolor):
        pass


MIN64INT = -9223372036854775808
MAX64INT = 9223372036854775807


class Zobrist(HashingAlgorithm):
    def __init__(self):
        self.zarray = [[[self._getrandomnumber() for k in range(0, 64)] for j in range(0, 6)] for i in range(0, 2)]
        self.zenpassant = [self._getrandomnumber() for i in range(0, 8)]
        self.zcastle = [self._getrandomnumber() for i in range(0, 4)]
        self.zblackmove = self._getrandomnumber()

    @staticmethod
    def _getrandomnumber():
        return random.randint(MIN64INT, MAX64INT)

    @staticmethod
    def _getpiecetype(piece):
        if isinstance(piece, pcsm.Pawn):
            return 0
        elif isinstance(piece, pcsm.Knight):
            return 1
        elif isinstance(piece, pcsm.Bishop):
            return 2
        elif isinstance(piece, pcsm.Rook):
            return 3
        elif isinstance(piece, pcsm.Queen):
            return 4
        elif isinstance(piece, pcsm.King):
            return 5
        else:
            raise ValueError("Zobrist --> _getpiecetype : Not a valid piece!!!")

    @staticmethod
    def _getcellnumber(piece):
        return alg.celllist.index(piece.coordinate)

    def gethashkey(self, listpiece, activecolor):
        zobristkey = 0
        if not activecolor:
            zobristkey ^= self.zblackmove
        color = 0
        for pieces in (listpiece.whitepieces, listpiece.blackpieces):
            for piece in pieces:
                piecetype = self._getpiecetype(piece)
                cellnumber = self._getcellnumber(piece)
                if piecetype == 5:
                    # king
                    if piece.castlingrights.ispossiblekingcastling():
                        zobristkey ^= self.zcastle[0 + 2 * color]
                    if piece.castlingrights.ispossiblequeencastling():
                        zobristkey ^= self.zcastle[1 + 2 * color]
                zobristkey ^= self.zarray[color][piecetype][cellnumber]
            color += 1
        color = 0
        for pieces in (listpiece.whitepawns, listpiece.blackpawns):
            for pawn in pieces:
                piecetype = self._getpiecetype(pawn)
                cellnumber = self._getcellnumber(pawn)
                if pawn.enpassantthreat:
                    column = pawn.coordinate.getfile() - 1
                    zobristkey ^= self.zenpassant[column]
                zobristkey ^= self.zarray[color][piecetype][cellnumber]
            color += 1
        return zobristkey

    def _getcastlingpiecestype(self):
        kingtype = self._getpiecetype(pcsm.King(alg.a1, None))
        rooktype = self._getpiecetype(pcsm.Rook(alg.a1, None, None))
        return kingtype, rooktype

    @staticmethod
    def _getcastlingcells(move):
        if move.iskingcastling:
            if move.iswhiteturn:
                kingfrom = alg.celllist.index(alg.e1)
                kingto = alg.celllist.index(alg.g1)
                rookfrom = alg.celllist.index(alg.h1)
                rookto = alg.celllist.index(alg.f1)
            else:
                kingfrom = alg.celllist.index(alg.e8)
                kingto = alg.celllist.index(alg.g8)
                rookfrom = alg.celllist.index(alg.h8)
                rookto = alg.celllist.index(alg.f8)
        elif move.isqueencastling:
            if move.iswhiteturn:
                kingfrom = alg.celllist.index(alg.e1)
                kingto = alg.celllist.index(alg.c1)
                rookfrom = alg.celllist.index(alg.a1)
                rookto = alg.celllist.index(alg.d1)
            else:
                kingfrom = alg.celllist.index(alg.e8)
                kingto = alg.celllist.index(alg.c8)
                rookfrom = alg.celllist.index(alg.a8)
                rookto = alg.celllist.index(alg.d8)
        else:
            raise ValueError("Zobrist --> _getcastlingcells : Invalid castling move!!!")
        return kingfrom, kingto, rookfrom, rookto

    def updatehashkey(self, key, listpiece, activecolor):
        newzobristkey = key
        if len(listpiece.moves) < 1:
            raise ValueError("Zobrist --> updatezobristkey : no update needed, because there are no moves applied!!!")
        move = listpiece.moves[-1]
        if move.iswhiteturn != activecolor:
            newzobristkey ^= self.zblackmove
        for i in range(0, 8):
            if listpiece.areenpassantchanged[i]:
                newzobristkey ^= self.zenpassant[i]
        for i in range(0, 4):
            if listpiece.arecastlingrightschanged[i]:
                newzobristkey ^= self.zcastle[i]
        if move.iswhiteturn:
            color = 0
            capturepiececolor = 1
        else:
            color = 1
            capturepiececolor = 0
        if move.iskingcastling or move.isqueencastling:
            kingtype, rooktype = self._getcastlingpiecestype()
            kingfromnumber, kingtonumber, rookfromnumber, rooktonumber = self._getcastlingcells(move)
            newzobristkey ^= self.zarray[color][kingtype][kingfromnumber]
            newzobristkey ^= self.zarray[color][kingtype][kingtonumber]
            newzobristkey ^= self.zarray[color][rooktype][rookfromnumber]
            newzobristkey ^= self.zarray[color][rooktype][rooktonumber]
        else:
            piece = move.capturedpiece
            if piece:
                cellnumber = self._getcellnumber(piece)
                piecetype = self._getpiecetype(piece)
                newzobristkey ^= self.zarray[capturepiececolor][piecetype][cellnumber]
            piece = move.promotionto
            if piece:
                cellnumber = self._getcellnumber(piece)
                piecetype = self._getpiecetype(piece)
                newzobristkey ^= self.zarray[color][piecetype][cellnumber]
            piece = move.piece
            cellnumber = alg.celllist.index(move.fromcell)
            piecetype = self._getpiecetype(piece)
            newzobristkey ^= self.zarray[color][piecetype][cellnumber]
            if move.promotionto is None:
                cellnumber = self._getcellnumber(piece)
                newzobristkey ^= self.zarray[color][piecetype][cellnumber]
        return newzobristkey

    def __str__(self):
        msg = "zArray\n"
        msg += str(self.zarray)
        msg += "\nzEnpassant\n"
        msg += str(self.zenpassant)
        msg += "\nzCastle\n"
        msg += str(self.zcastle)
        msg += "\nzBlackMove\n"
        msg += str(self.zblackmove)
        return msg


zobristgenerator = Zobrist()