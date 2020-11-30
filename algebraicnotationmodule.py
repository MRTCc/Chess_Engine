# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 11:25:05 2020

@author: martu
"""


class CoordinateException(Exception):
    pass


class AlgebraicNotation(str):
    def __init__(self, coordinate):
        self.coordinate = coordinate
        self.lettervalues = {0: '0', 1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e',
                             6: 'f', 7: 'g', 8: 'h'}
        self.rankint = 0
        for key, value in self.lettervalues.items():
            if value == self.coordinate[0]:
                self.rankint = key
        self.fileint = int(self.coordinate[1])
        if self.rankint > 8 or self.rankint < 1 or self.fileint > 8 or self.fileint < 1:
            raise CoordinateException("Invalid: " + self.coordinate + " sum rank:" +
                                      str(self.rankint) + " and file:" + str(self.fileint))

    def sumcoordinate(self, rank=0, file=0):
        rankvalue = self.rankint
        rankvalue += rank
        filevalue = self.fileint
        filevalue += file
        if rankvalue > 8 or rankvalue < 1 or filevalue > 8 or filevalue < 1:
            raise CoordinateException("Invalid: " + self.coordinate + " sum rank:" +
                                      str(rank) + " and file:" + str(file))
        return AlgebraicNotation(self.lettervalues[rankvalue] + str(filevalue))

    def isminfile(self):
        result = False
        if self.fileint == 1:
            result = True
        return result

    def isequalrank(self, rank):
        if self.coordinate[0] == rank:
            return True
        else:
            return False

    def getrank(self):
        return self.coordinate[0]

    def getrankvalue(self):
        return self.rankint

    def getfile(self):
        return int(self.coordinate[1])

    def absfiledifference(self, other):
        return abs(self.fileint - other.fileint)

    def absrankdifference(self, other):
        return abs(self.rankint - other.rankint)

    def __str__(self):
        return self.coordinate


a1 = AlgebraicNotation("a1")
a2 = AlgebraicNotation("a2")
a3 = AlgebraicNotation("a3")
a4 = AlgebraicNotation("a4")
a5 = AlgebraicNotation("a5")
a6 = AlgebraicNotation("a6")
a7 = AlgebraicNotation("a7")
a8 = AlgebraicNotation("a8")
b1 = AlgebraicNotation("b1")
b2 = AlgebraicNotation("b2")
b3 = AlgebraicNotation("b3")
b4 = AlgebraicNotation("b4")
b5 = AlgebraicNotation("b5")
b6 = AlgebraicNotation("b6")
b7 = AlgebraicNotation("b7")
b8 = AlgebraicNotation("b8")
c1 = AlgebraicNotation("c1")
c2 = AlgebraicNotation("c2")
c3 = AlgebraicNotation("c3")
c4 = AlgebraicNotation("c4")
c5 = AlgebraicNotation("c5")
c6 = AlgebraicNotation("c6")
c7 = AlgebraicNotation("c7")
c8 = AlgebraicNotation("c8")
d1 = AlgebraicNotation("d1")
d2 = AlgebraicNotation("d2")
d3 = AlgebraicNotation("d3")
d4 = AlgebraicNotation("d4")
d5 = AlgebraicNotation("d5")
d6 = AlgebraicNotation("d6")
d7 = AlgebraicNotation("d7")
d8 = AlgebraicNotation("d8")
e1 = AlgebraicNotation("e1")
e2 = AlgebraicNotation("e2")
e3 = AlgebraicNotation("e3")
e4 = AlgebraicNotation("e4")
e5 = AlgebraicNotation("e5")
e6 = AlgebraicNotation("e6")
e7 = AlgebraicNotation("e7")
e8 = AlgebraicNotation("e8")
f1 = AlgebraicNotation("f1")
f2 = AlgebraicNotation("f2")
f3 = AlgebraicNotation("f3")
f4 = AlgebraicNotation("f4")
f5 = AlgebraicNotation("f5")
f6 = AlgebraicNotation("f6")
f7 = AlgebraicNotation("f7")
f8 = AlgebraicNotation("f8")
g1 = AlgebraicNotation("g1")
g2 = AlgebraicNotation("g2")
g3 = AlgebraicNotation("g3")
g4 = AlgebraicNotation("g4")
g5 = AlgebraicNotation("g5")
g6 = AlgebraicNotation("g6")
g7 = AlgebraicNotation("g7")
g8 = AlgebraicNotation("g8")
h1 = AlgebraicNotation("h1")
h2 = AlgebraicNotation("h2")
h3 = AlgebraicNotation("h3")
h4 = AlgebraicNotation("h4")
h5 = AlgebraicNotation("h5")
h6 = AlgebraicNotation("h6")
h7 = AlgebraicNotation("h7")
h8 = AlgebraicNotation("h8")

ranks = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')

# board from white's point of view
celllist = (a8, b8, c8, d8, e8, f8, g8, h8,
            a7, b7, c7, d7, e7, f7, g7, h7,
            a6, b6, c6, d6, e6, f6, g6, h6,
            a5, b5, c5, d5, e5, f5, g5, h5,
            a4, b4, c4, d4, e4, f4, g4, h4,
            a3, b3, c3, d3, e3, f3, g3, h3,
            a2, b2, c2, d2, e2, f2, g2, h2,
            a1, b1, c1, d1, e1, f1, g1, h1)

enpassantlist = (a6, b6, c6, d6, e6, f6, g6, h6,
                 a3, b3, c3, d3, e3, f3, g3, h3)


def str_to_algebraic(strcoordinate):
    if strcoordinate == 'a1':
        return a1
    elif strcoordinate == 'a2':
        return a2
    elif strcoordinate == 'a3':
        return a3
    elif strcoordinate == 'a4':
        return a4
    elif strcoordinate == 'a5':
        return a5
    elif strcoordinate == 'a6':
        return a6
    elif strcoordinate == 'a7':
        return a7
    elif strcoordinate == 'a8':
        return a8
    elif strcoordinate == 'b1':
        return b1
    elif strcoordinate == 'b2':
        return b2
    elif strcoordinate == 'b3':
        return b3
    elif strcoordinate == 'b4':
        return b4
    elif strcoordinate == 'b5':
        return b5
    elif strcoordinate == 'b6':
        return b6
    elif strcoordinate == 'b7':
        return b7
    elif strcoordinate == 'b8':
        return b8
    elif strcoordinate == 'c1':
        return c1
    elif strcoordinate == 'c2':
        return c2
    elif strcoordinate == 'c3':
        return c3
    elif strcoordinate == 'c4':
        return c4
    elif strcoordinate == 'c5':
        return c5
    elif strcoordinate == 'c6':
        return c6
    elif strcoordinate == 'c7':
        return c7
    elif strcoordinate == 'c8':
        return c8
    elif strcoordinate == 'd1':
        return d1
    elif strcoordinate == 'd2':
        return d2
    elif strcoordinate == 'd3':
        return d3
    elif strcoordinate == 'd4':
        return d4
    elif strcoordinate == 'd5':
        return d5
    elif strcoordinate == 'd6':
        return d6
    elif strcoordinate == 'd7':
        return d7
    elif strcoordinate == 'd8':
        return d8
    elif strcoordinate == 'e1':
        return e1
    elif strcoordinate == 'e2':
        return e2
    elif strcoordinate == 'e3':
        return e3
    elif strcoordinate == 'e4':
        return e4
    elif strcoordinate == 'e5':
        return e5
    elif strcoordinate == 'e6':
        return e6
    elif strcoordinate == 'e7':
        return e7
    elif strcoordinate == 'e8':
        return e8
    elif strcoordinate == 'f1':
        return f1
    elif strcoordinate == 'f2':
        return f2
    elif strcoordinate == 'f3':
        return f3
    elif strcoordinate == 'f4':
        return f4
    elif strcoordinate == 'f5':
        return f5
    elif strcoordinate == 'f6':
        return f6
    elif strcoordinate == 'f7':
        return f7
    elif strcoordinate == 'f8':
        return f8
    elif strcoordinate == 'g1':
        return g1
    elif strcoordinate == 'g2':
        return g2
    elif strcoordinate == 'g3':
        return g3
    elif strcoordinate == 'g4':
        return g4
    elif strcoordinate == 'g5':
        return g5
    elif strcoordinate == 'g6':
        return g6
    elif strcoordinate == 'g7':
        return g7
    elif strcoordinate == 'g8':
        return g8
    elif strcoordinate == 'h1':
        return h1
    elif strcoordinate == 'h2':
        return h2
    elif strcoordinate == 'h3':
        return h3
    elif strcoordinate == 'h4':
        return h4
    elif strcoordinate == 'h5':
        return h5
    elif strcoordinate == 'h6':
        return h6
    elif strcoordinate == 'h7':
        return h7
    elif strcoordinate == 'h8':
        return h8
    else:
        raise ValueError('Not a valid string argument!!!')


if __name__ == '__main__':
    a1.sumcoordinate(1, 7)
