def transpositiontablefactory(algorithm):
    if algorithm == 'minmax':
        transpositiontable = TranspositionTable(MinMaxRecord)
    elif algorithm in ('alphabeta', 'iterdeep'):
        transpositiontable = TranspositionTable(AlphaBetaRecord)
    else:
        raise ValueError("Transpositiontablefactory --> algorithm not valid!!!")
    return transpositiontable


class TranspositionTable:
    def __init__(self, record_class):
        self.records = {}
        self.record_class = record_class

    def lookup(self, key):
        return self.records[key]

    def getrecord(self, key, board):
        try:
            record = self.records[key]
            if record.board != board:
                record = None
        except KeyError:
            record = None
        return record

    def insertnewrecord(self, key, *args):
        newrecord = self.record_class(key, *args)
        if key in self.records.keys():
            self._collisionmanagement(newrecord, self.records[key])
        else:
            self.records[key] = newrecord

    def _collisionmanagement(self, newrecord, oldrecord):
        if oldrecord.depthleft < newrecord.depthleft:
            self.records[newrecord.key] = newrecord

    def updatetonewposition(self):
        self.records = {}

    def __str__(self):
        length = str(len(self.records))
        msg = "Transposition table (n. of elements: " + length + " ):\n{\n"
        for key, record in self.records.items():
            msg += '\t' + str(record) + '\n'
        msg += "}\n"
        return msg


class Record:
    def __init__(self, key, score, depthleft, bestmove, ishorizonleaf, board):
        if key is None or score is None or depthleft is None or board is None:
            raise AttributeError("Record --> __init__ : 'None' attribute value!!!")
        self.key = key
        self.score = score
        self.depthleft = depthleft
        self.board = board
        self.bestmove = bestmove
        self.ishorizonleaf = ishorizonleaf
        self.isold = False

    def getrecorddata(self):
        pass


class MinMaxRecord(Record):
    def __init__(self, key, score, depthleft, bestmove, ishorizonleaf, board):
        super().__init__(key, score, depthleft, bestmove, ishorizonleaf, board)
        if self.ishorizonleaf:
            self.isold = True

    def getrecorddata(self):
        return self.score, self.bestmove, self.ishorizonleaf

    def __str__(self):
        msg = ("key: " + str(self.key) + "\tscore: " + str(self.score) + "\tdepth left: " + str(self.depthleft) +
               "\thorizon leaf: " + str(self.ishorizonleaf) + "\tbestmove" + str(self.bestmove.short__str__()))
        return msg


class AlphaBetaRecord(Record):
    def __init__(self, key, score, isalphacutoff, isbetacutoff, depthleft, bestmove, ishorizonleaf, board):
        super().__init__(key, score, depthleft, bestmove, ishorizonleaf, board)
        if isalphacutoff is None or isbetacutoff is None:
            raise AttributeError("Record --> __init__ : 'None' attribute value!!!")
        self.isalphacutoff = isalphacutoff
        self.isbetacutoff = isbetacutoff
        if self.isalphacutoff and self.isbetacutoff:
            raise ValueError("AlphaBetaRecord --> __init__ : invalid request: it's not possible alpha and beta cutoff "
                             "at the same time")
        if self.ishorizonleaf or self.isalphacutoff or self.isbetacutoff:
            self.isold = True

    def getrecorddata(self):
        return self.score, self.isalphacutoff, self.isbetacutoff, self.bestmove, self.ishorizonleaf

    def __str__(self):
        msg = ("key: " + str(self.key) + "\tscore: " + str(self.score) + "\tdepth left: " + str(self.depthleft) +
               "\talpha cutoff: " + str(self.isalphacutoff) + "\tbeta cutoff: " + str(self.isbetacutoff) +
               "\thorizon leaf: " + str(self.ishorizonleaf) + "\tbestmove" + str(self.bestmove.short__str__()))
        return msg


if __name__ == '__main__':
    pass
