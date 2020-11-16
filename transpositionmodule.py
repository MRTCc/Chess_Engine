def transpositiontablefactory(algorithm):
    if algorithm == 'minmax':
        transpositiontable = TranspositionTable(MinMaxRecord)
    elif algorithm == 'alphabeta':
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

    def getrecordfromkey(self, key, board):
        try:
            record = self.records[key]
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

    def __str__(self):
        length = str(len(self.records))
        msg = "Transposition table (n. of elements: " + length + " ):\n{\n"
        for key, record in self.records.items():
            msg += '\t' + str(record) + '\n'
        msg += "}\n"
        return msg


class Record:
    def __init__(self, key, score, depthleft, board):
        if key is None or score is None or depthleft is None or board is None:
            raise AttributeError("Record --> __init__ : 'None' attribute value!!!")
        self.key = key
        self.score = score
        self.depthleft = depthleft
        self.board = board

    def getrecorddata(self):
        pass

    def __str__(self):
        msg = "key: " + str(self.key) + "\tscore: " + str(self.score) + "\tdepth left: " + str(self.depthleft)
        return msg


class MinMaxRecord(Record):
    def __init__(self, key, score, depthleft, board):
        super().__init__(key, score, depthleft, board)

    def getrecorddata(self):
        return self.score


class AlphaBetaRecord(Record):
    def __init__(self, key, score, isalphacutoff, isbetacutoff, depthleft, board):
        super().__init__(key, score, depthleft, board)
        if isalphacutoff is None or isbetacutoff is None:
            raise AttributeError("Record --> __init__ : 'None' attribute value!!!")
        self.isalphacutoff = isalphacutoff
        self.isbetacutoff = isbetacutoff
        if self.isalphacutoff and self.isbetacutoff:
            raise ValueError("AlphaBetaRecord --> __init__ : invalid request: it's not possible alpha and beta cutoff "
                             "at the same time")

    def getrecorddata(self):
        return self.score, self.isalphacutoff, self.isbetacutoff

    def __str__(self):
        msg = ("key: " + str(self.key) + "\tscore: " + str(self.score) + "\tdepth left: " + str(self.depthleft) +
               "\t\talpha cutoff: " + str(self.isalphacutoff) + "\t\tbeta cutoff: " + str(self.isbetacutoff))
        return msg


if __name__ == '__main__':
    pass
