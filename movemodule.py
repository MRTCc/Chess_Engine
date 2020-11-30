# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 17:52:20 2020

@author: martu
"""


class Move:
    def __init__(self, piece=None, fromcell=None, tocell=None, iswhiteturn=True, capturedpiece=None,
                 iskingcastling=False, isqueencastling=False, promotionto=None,
                 isenpassant=False, ischeck=False):
        self.piece = piece
        self.fromcell = fromcell
        self.tocell = tocell
        self.iswhiteturn = iswhiteturn
        self.capturedpiece = capturedpiece
        self.iskingcastling = iskingcastling
        self.isqueencastling = isqueencastling
        self.promotionto = promotionto
        self.isenpassant = isenpassant
        self.ischeck = ischeck  # per ora lo metto, forse può servire a qualche ottimizzazione

    def short__str__(self):
        msg = ''
        if self.iswhiteturn:
            if self.iskingcastling:
                msg += 'e1g1'
                return msg
            elif self.isqueencastling:
                msg += 'e1c1'
                return msg
        else:
            if self.iskingcastling:
                msg += 'e8g8'
                return msg
            elif self.isqueencastling:
                msg += 'e8c8'
                return msg
        msg += str(self.fromcell) + str(self.tocell)
        if self.promotionto:
            promotion = 'q'
        else:
            promotion = ''
        msg += promotion
        return msg

    def __str__(self):
        result = "Move: \n"
        result += "\t piece = " + str(self.piece) + '\n'
        result += '\t ' + str(self.fromcell) + " " + str(self.tocell) + '\n'
        result += "\t iswhiteturn = " + str(self.iswhiteturn) + '\n'
        result += "\t capturedpiece = " + str(self.capturedpiece) + '\n'
        result += "\t iskingcastling = " + str(self.iskingcastling) + '\n'
        result += "\t isqueencastling = " + str(self.isqueencastling) + '\n'
        result += "\t promotionto = " + str(self.promotionto) + '\n'
        result += "\t isenpassant = " + str(self.isenpassant) + '\n'
        result += "\t ischeck = " + str(self.ischeck) + '\n'

        return result


class MoveFactory:
    def __init__(self):
        self.piece = None
        self.fromcell = None
        self.tocell = None
        self.iswhiteturn = True
        self.capturedpiece = None
        self.iskingcastling = False
        self.isqueencastling = False
        self.promotionto = None
        self.isenpassant = False
        self.ischeck = False

    def __call__(self, piece, fromcell, tocell, ischeck):
        """
        si assumono le mosse legali, qui non si farà alcun controllo
        """
        self.piece = piece
        self.fromcell = fromcell
        self.tocell = tocell
        self.ischeck = ischeck
        move = Move(self.piece, self.fromcell, self.tocell, self.iswhiteturn,
                    self.capturedpiece, self.iskingcastling, self.isqueencastling,
                    self.promotionto, self.isenpassant, self.ischeck)
        return move


class WhiteMoveFactory(MoveFactory):
    pass


class BlackMoveFactory(MoveFactory):
    def __init__(self):
        super().__init__()
        self.iswhiteturn = False


class MoveCaptureFactory(MoveFactory):
    def __call__(self, piece, fromcell, tocell, capturedpiece, ischeck):
        self.capturedpiece = capturedpiece
        return super().__call__(piece, fromcell, tocell, ischeck)


class WhiteMoveCaptureFactory(MoveCaptureFactory):
    pass


class BlackMoveCaptureFactory(MoveCaptureFactory):
    def __init__(self):
        super().__init__()
        self.iswhiteturn = False


class MovePromotionFactory(MoveFactory):
    def __call__(self, piece, fromcell, tocell, promotionto, ischeck):
        self.promotionto = promotionto
        return super().__call__(piece, fromcell, tocell, ischeck)


class WhiteMovePromotionFactory(MovePromotionFactory):
    pass


class BlackMovePromotionFactory(MovePromotionFactory):
    def __init__(self):
        super().__init__()
        self.iswhiteturn = False


class MoveCapturePromotionFactory(MovePromotionFactory):
    def __call__(self, piece, fromcell, tocell, capturedpiece, promotionto, ischeck):
        self.capturedpiece = capturedpiece
        return super().__call__(piece, fromcell, tocell, promotionto, ischeck)


class WhiteMoveCapturePromotionFactory(MoveCapturePromotionFactory):
    pass


class BlackMoveCapturePromotionFactory(MoveCapturePromotionFactory):
    def __init__(self):
        super().__init__()
        self.iswhiteturn = False


class MoveEnpassantFactory(MoveCaptureFactory):
    pass


class WhiteMoveEnpassantFactory(MoveEnpassantFactory):
    pass


class BlackMoveEnpassantFactory(MoveEnpassantFactory):
    def __init__(self):
        super().__init__()
        self.iswhiteturn = False


class KingsideCastlingFactory(MoveFactory):
    def __call__(self):
        self.iskingcastling = True
        move = Move(self.piece, self.fromcell, self.tocell, self.iswhiteturn,
                    self.capturedpiece, self.iskingcastling, self.isqueencastling,
                    self.promotionto, self.isenpassant, self.ischeck)
        return move


class WhiteKingsideCastlingFactory(KingsideCastlingFactory):
    pass


class BlackKingsideCastlingFactory(KingsideCastlingFactory):
    def __init__(self):
        super().__init__()
        self.iswhiteturn = False


class QueensideCastlingFactory(MoveFactory):
    def __call__(self):
        self.isqueencastling = True
        self.ischeck = False
        move = Move(self.piece, self.fromcell, self.tocell, self.iswhiteturn,
                    self.capturedpiece, self.iskingcastling, self.isqueencastling,
                    self.promotionto, self.isenpassant, self.ischeck)
        return move


class WhiteQueensideCastlingFactory(QueensideCastlingFactory):
    pass


class BlackQueensideCastlingFactory(QueensideCastlingFactory):
    def __init__(self):
        super().__init__()
        self.iswhiteturn = False


whiteMoveFactory = WhiteMoveFactory()
blackMoveFactory = BlackMoveFactory()

whiteMoveCaptureFactory = WhiteMoveCaptureFactory()
blackMoveCaptureFactory = BlackMoveCaptureFactory()

whiteMovePromotionFactory = WhiteMovePromotionFactory()
blackMovePromotionFactory = BlackMovePromotionFactory()

whiteMoveCapturePromotionFactory = WhiteMoveCapturePromotionFactory()
blackMoveCapturePromotionFactory = BlackMoveCapturePromotionFactory()

whiteMoveEnpassantFactory = WhiteMoveEnpassantFactory()
blackMoveEnpassantFactory = BlackMoveEnpassantFactory()

whiteKingsideCastlingFactory = WhiteKingsideCastlingFactory()
blackKingsideCastlingFactory = BlackKingsideCastlingFactory()

whiteQueensideCastlingFactory = WhiteQueensideCastlingFactory()
blackQueensideCastlingFactory = BlackQueensideCastlingFactory()


class CastlingRights:
    def __init__(self, kinginstartpos=True, rooksxinstartpos=True, rookdxinstartpos=True, safekingsideline=True,
                 safequeensideline=True, kingincheck=False):
        self.kinginstartpos = kinginstartpos
        self.rooksxinstartpos = rooksxinstartpos
        self.rookdxinstartpos = rookdxinstartpos
        self.safekingsideline = safekingsideline
        self.safequeensideline = safequeensideline
        self.kingincheck = kingincheck

    def ispossiblekingcastling(self):
        result = False
        if (self.kinginstartpos == True and self.rookdxinstartpos == True and
                self.safekingsideline == True and self.kingincheck == False):
            result = True
        return result

    def ispossiblequeencastling(self):
        result = False
        if (self.kinginstartpos == True and self.rooksxinstartpos == True and
                self.safequeensideline == True and self.kingincheck == False):
            result = True
        return result

    def setonlykingcastling(self):
        self.rooksxinstartpos = False
        self.safequeensideline = False

    def setonlyqueencastling(self):
        self.rookdxinstartpos = False
        self.safekingsideline = False

    def __str__(self):
        msg = "Castling rights: \n\t"
        for key, value in self.__dict__.items():
            msg += key + " --> "
            msg += str(value) + "\n\t"
        return msg


if __name__ == '__main__':

    c = CastlingRights()
    a = c.ispossiblekingcastling()
    print(a)
    c.kingincheck = True
    a = c.ispossiblequeencastling()
    print(a)
