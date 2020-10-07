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

    def sumcoordinatedatogliere(self, rank=0, file=0):
        if rank < 0 or file < 0:
            raise AttributeError("rank and file must be positive")
        rankvalue = self.rankint
        rankvalue += rank
        filevalue = self.fileint
        filevalue += file
        if rankvalue > 8 or filevalue > 8:
            raise CoordinateException("Invalid: " + self.coordinate + " sum rank:" +
                                      str(rank) + " and file:" + str(file))

        return self.lettervalues[rankvalue] + str(filevalue)

    def subcoordinatedatogliere(self, rank=0, file=0):
        if rank < 0 or file < 0:
            raise AttributeError("rank and file must be positive")
        rankvalue = 0
        rankvalue = self.rankint
        rankvalue -= rank
        filevalue = self.fileint
        filevalue -= file
        if rankvalue < 1 or filevalue < 1:
            raise CoordinateException("Invalid: " + self.coordinate + " sum rank:" +
                                      str(rank) + " and file:" + str(file))

        return self.lettervalues[rankvalue] + str(filevalue)

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

    def __str__(self):
        return self.coordinate

class NullAlgebricNotation(AlgebraicNotation):
    def __init__(self):
        self.coordinate = "00"

    def sumcoordinate(self, rank=0, file=0):
        return self

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

null = NullAlgebricNotation()

# board from white's point of view
celllist = (a8, b8, c8, d8, e8, f8, g8, h8,
            a7, b7, c7, d7, e7, f7, g7, h7,
            a6, b6, c6, d6, e6, f6, g6, h6,
            a5, b5, c5, d5, e5, f5, g5, h5,
            a4, b4, c4, d4, e4, f4, g4, h4,
            a3, b3, c3, d3, e3, f3, g3, h3,
            a2, b2, c2, d2, e2, f2, g2, h2,
            a1, b1, c1, d1, e1, f1, g1, h1)

if __name__ == '__main__':
    a1.sumcoordinate(1, 7)
