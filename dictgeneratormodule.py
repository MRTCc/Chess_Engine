from algebraicnotationmodule import (a8, b8, c8, d8, e8, f8, g8, h8,
                                     a7, b7, c7, d7, e7, f7, g7, h7,
                                     a6, b6, c6, d6, e6, f6, g6, h6,
                                     a5, b5, c5, d5, e5, f5, g5, h5,
                                     a4, b4, c4, d4, e4, f4, g4, h4,
                                     a3, b3, c3, d3, e3, f3, g3, h3,
                                     a2, b2, c2, d2, e2, f2, g2, h2,
                                     a1, b1, c1, d1, e1, f1, g1, h1)

occupiedcells = []
whiteoccupiedcells = []
blackoccupiedcells = []
whitepawns = []
blackpawns = []
whiterooks = []
blackrooks = []
whiteknights = []
blackknights = []
whitebishops = []
blackbishops = []
whitequeen = []
blackqueen = []
whiteking = []
blackking = []
enpassantcells = []
castlingrights = ['wk', 'wq', 'bk', 'bq']

whitepawnonestep = {a7: a8, b7: b8, c7: c8, d7: d8, e7: e8, f7: f8, g7: g8, h7: h8,
                    a6: a7, b6: b7, c6: c7, d6: d7, e6: e7, f6: f7, g6: g7, h6: h7,
                    a5: a6, b5: b6, c5: c6, d5: d6, e5: e6, f5: f6, g5: g6, h5: h6,
                    a4: a5, b4: b5, c4: c5, d4: d5, e4: e5, f4: f5, g4: g5, h4: h5,
                    a3: a4, b3: b4, c3: c4, d3: d4, e3: e4, f3: f4, g3: g4, h3: h4,
                    a2: a3, b2: b3, c2: c3, d2: d3, e2: e3, f2: f3, g2: g3, h2: h3}

whitepawntwostep = {a2: a4, b2: b4, c2: c4, d2: d4, e2: e4, f2: f4, g2: g4, h2: h4}


def white_pawn_generator(fromcell):
    pass


def white_generator_moves():
    # genera mosse dei pedoni
    for fromcell in whitepawns:
        tocell = white_pawn_generator(fromcell)
    # genera mosse delle torri
    # genera mosse dei cavalli
    # genera mosse degli alfieri
    # genera mosse della regina
    # genera mosse del re
    # genera arrocchi possibili
    pass


def black_generator_moves():
    pass