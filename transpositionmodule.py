import piecesmodule as pcsm
import algebraicnotationmodule as alg
import random

MIN64INT = -9223372036854775808
MAX64INT = 9223372036854775807


class Zobrist:
    def __init__(self):
        self.zarray = [[[self._getrandomnumber() for k in range(0, 64)] for j in range(0, 6)] for i in range(0, 2)]
        self.zenpassant = [self._getrandomnumber() for i in range(0, 8)]
        self.zcastle = [self._getrandomnumber() for i in range(0, 4)]
        self.zblackmove = self._getrandomnumber()

    def _getrandomnumber(self):
        return random.randint(MIN64INT, MAX64INT)

    def _getpiecetype(self, piece):
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

    def _getcellnumber(self, piece):
        return alg.celllist.index(piece.coordinate)

    def getzobristhash(self, listpiece, iswhiteturn):
        zobristkey = 0
        if iswhiteturn:
            zobristkey ^= self.zblackmove
        for pieces in (listpiece.whitepieces, listpiece.blackpieces):
            color = 0
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
        for pieces in (listpiece.whitepawns, listpiece.blackpawns):
            color = 0
            for pawn in listpiece.whitepawns + listpiece.blackpawns:
                color = 0
                piecetype = self._getpiecetype(pawn)
                cellnumber = self._getcellnumber(pawn)
                if pawn.isenpassantthreat:
                    column = pawn.coordinate.getfile() - 1
                    zobristkey ^= self.zenpassant[column]
                zobristkey ^= self.zarray[color][piecetype][cellnumber]
            color += 1
        return zobristkey

    def _istwostepsmove(self, move):
        if not isinstance(move.piece, pcsm.Pawn):
            return False
        filesteps = move.fromcell.absfiledifference(move.tocell)
        if filesteps == 2:
            return True
        else:
            return False

    def _getcastlingcells(self, move):
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

    def updatezobristkey(self, key, listpiece, whomoved):
        newzobristkey = key
        prevmove = listpiece.moves[-2]
        move = listpiece.moves[-1]
        if whomoved != move.iswhiteturn:
            newzobristkey ^= self.zblackmove
        for i in range(0, 4):
            if listpiece.arecastlingrightschanged[i]:
                newzobristkey ^= self.zcastle[i]
        if self._istwostepsmove(prevmove):
            column = move.fromcell.getfile() - 1
            newzobristkey ^= self.zenpassant[column]
        if self._istwostepsmove(move):
            column = move.fromcell.getfile() - 1
            newzobristkey ^= self.zenpassant[column]
        if move.iswhiteturn:
            color = 0
        else:
            color = 1
        if move.iskingcastling or move.isqueencastling:
            kingtype = self._getpiecetype(listpiece.whiteking)
            # TODO da mettere a posto questo hardcoding
            rooktype = 3
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
                newzobristkey ^= self.zarray[color][piecetype][cellnumber]
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


if __name__ == '__main__':
    z = Zobrist()
    print(z)
